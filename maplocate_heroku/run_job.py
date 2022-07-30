
# python3

import os
import io
import json
import traceback

def friendly_url_request(url):
    from urllib.request import Request
    headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}
    return Request(url, headers=headers)

def friendly_url_download(url):
    import urllib.request
    headers = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)')]
    opener = urllib.request.build_opener()
    opener.addheaders = headers
    urllib.request.install_opener(opener)
    #import hashlib
    #filename = hashlib.md5(url.encode('utf8')).hexdigest()
    path,return_headers = urllib.request.urlretrieve(url) #, filename)
    fobj = open(path, mode='rb')
    return fobj

def detect_toponyms(url, text_options=None, toponym_options=None):
    # open image
    from PIL import Image
    fobj = friendly_url_download(url) # downloads then opens
    im = Image.open(fobj)
    print(im)
    w,h = im.size
    iminfo = {'width':w, 'height':h}

    # detect map text
    import maponyms
    kwargs = text_options or {}
    if 'textcolor' not in kwargs: 
        kwargs['textcolor'] = (0,0,0)
    textdata = maponyms.main.text_detection(im, **kwargs)

    # select toponym candidates
    kwargs = toponym_options or {}
    candidate_toponyms = maponyms.main.toponym_selection(im, textdata, **kwargs)

    results = {'image':iminfo, 'toponyms':candidate_toponyms}
    return results

class MySqlCoder(object):
    def __init__(self):
        import pymysql, pymysql.cursors
        self.db = pymysql.connect(host=os.environ['GEOCODER_HOST'],
                                port=int(os.environ['GEOCODER_PORT']), 
                                user=os.environ['GEOCODER_USER'],
                                password=os.environ['GEOCODER_PASSWORD'],
                                ssl_ca="data/azure-mysql-DigiCertGlobalRootCA.crt.pem", 
                                ssl_disabled=False,
                                database=os.environ['GEOCODER_DATABASE'],
                                cursorclass=pymysql.cursors.Cursor)

    def geocode(self, name, limit=None, lang=None):
        if limit:
            raise NotImplemented("Geocode results 'limit' not yet implemented")
        _matches = "SELECT * FROM names WHERE name = %s"
        _select = "sources.name,locs.loc_id,GROUP_CONCAT(names.name SEPARATOR '|'),locs.lon,locs.lat"
        _from = "sources,locs,names,matches WHERE names.loc_id=matches.loc_id AND names.loc_id=locs.loc_id AND locs.source_id=sources.source_id"
        _groupby = "locs.loc_id"
        #_groupby += ",sources.name,locs.lon,locs.lat" # mysql requires specifying all select cols in groupby
        query = "WITH matches AS ({_matches}) SELECT {_select} FROM {_from} GROUP BY {_groupby}".format(_matches=_matches, _select=_select, _from=_from, _groupby=_groupby)
        cur = self.db.cursor()
        cur.execute(query, (name,))
        results = [{'type': 'Feature',
                   'properties': {'data':data,
                                  'id':ID,
                                  'name':names,
                                  'search':name,
                                  },
                   'geometry': {'type':'Point', 'coordinates':[lon,lat]},
                   } for data,ID,names,lon,lat in cur]
        return results

def match_toponyms(toponyms, **match_options):
    import maponyms

    # find toponym coordinates
    geocoder = MySqlCoder()
    matched_toponyms = maponyms.main.match_control_points(toponyms, geocoder=geocoder, **match_options)

    # make into control points
    return matched_toponyms

def estimate_transform(controlpoints, image=None, **transform_options):
    import transformio as tio

    # format the control points as expected by transformio
    frompoints = [(feat['properties']['origx'],feat['properties']['origy']) for feat in controlpoints['features']]
    topoints = [(feat['properties']['matchx'],feat['properties']['matchy']) for feat in controlpoints['features']]
    fromx,fromy = zip(*frompoints)
    tox,toy = zip(*topoints)

    # auto select best transform based on backwards pixel loo rmse
    trytrans = [tio.transforms.Polynomial(order=1),
                tio.transforms.Polynomial(order=2),
                tio.transforms.Polynomial(order=3),
                ]
    result = tio.accuracy.auto_choose_model(topoints, 
                                            frompoints, 
                                            trytrans,
                                            distance='euclidean',
                                            metric='rmse',
                                            )
    backtrans,topoints,frompoints,predicted,residuals,err = result

    # switch to forward transform
    trans = backtrans.inverse()
    transdata = trans.to_json()
    print(transdata)

    # create the final reduced set of controlpoints geojson
    print(frompoints)
    final_controlpoints = {'type':'FeatureCollection', 'features':[]}
    for feat in controlpoints['features']:
        frompoint = feat['properties']['origx'],feat['properties']['origy']
        print(frompoint)
        if frompoint in frompoints:
            final_controlpoints['features'].append(feat)
    print(final_controlpoints)
    
    # results
    results = {'transform':transdata,
                'controlpoints':final_controlpoints}
        
    # calc bbox if image is given
    if image:
        imsize = image['width'],image['height']
        bbox = tio.imwarp.imbounds(*imsize, trans)
        results['bbox'] = bbox

    return results

def calculate_errors(controlpoints, transform, image=None, **error_options):
    import transformio as tio
    import math

    # load transform
    trans = tio.transforms.from_json(transform)

    # calc and store error residual for each control point
    forw,back = trans,trans.inverse()
    for f in controlpoints['features']:
        props = f['properties']
        ox,oy,mx,my = props['origx'],props['origy'],props['matchx'],props['matchy']
        # first pixel to geo
        [mxpred],[mypred] = forw.predict([ox], [oy])
        props['matchx_pred'] = mxpred
        props['matchy_pred'] = mypred
        [mresid] = tio.accuracy.distances([mx], [my], [mxpred], [mypred], 'geodesic')
        props['matchresidual'] = mresid
        # then geo to pixel
        [oxpred],[oypred] = back.predict([mx], [my])
        props['origx_pred'] = oxpred
        props['origy_pred'] = oypred
        [oresid] = tio.accuracy.distances([ox], [oy], [oxpred], [oypred], 'euclidean')
        props['origresidual'] = oresid

    # get the point residuals
    resids_xy = [f['properties']['matchresidual'] for f in controlpoints['features']]
    resids_colrow = [f['properties']['origresidual'] for f in controlpoints['features']]
    
    # calc model errors
    errs = {}
    # first geographic
    errs['geographic'] = {}
    errs['geographic']['mae'] = tio.accuracy.MAE(resids_xy)
    errs['geographic']['rmse'] = tio.accuracy.RMSE(resids_xy)
    errs['geographic']['max'] = tio.accuracy.MAX(resids_xy)
    # then pixels
    errs['pixel'] = {}
    errs['pixel']['mae'] = tio.accuracy.MAE(resids_colrow)
    errs['pixel']['rmse'] = tio.accuracy.RMSE(resids_colrow)
    errs['pixel']['max'] = tio.accuracy.MAX(resids_colrow)
    # then percent (of image pixel dims)
    if image:
        imsize = image['width'],image['height']
        errs['percent'] = {}
        diag = math.hypot(*imsize)
        img_radius = float(diag/2.0) # percent of half the max dist (from img center to corner)
        errs['percent']['mae'] = (errs['pixel']['mae'] / img_radius) * 100.0
        errs['percent']['rmse'] = (errs['pixel']['mae'] / img_radius) * 100.0
        errs['percent']['max'] = (errs['pixel']['max'] / img_radius) * 100.0

        # add percent residual to gcps_final_info
        for f in controlpoints['features']:
            pixres = f['properties']['origresidual']
            percerr = (pixres / img_radius) * 100.0
            f['properties']['percresidual'] = percerr

    return errs

######################################
# NOTE: the url_host must be publicly accessible 
# so that the backend can post the results on completion.
# in the case of local testing must use 
# `manage.py runserver 0.0.0.0:port`, and make the device IP
# publicly accessible by forwarding to that port on the wifi router.

def post_status(url_host, pk, status, details):
    import requests
    data = {'status':status, 'status_details':details}
    url = '{}/map/post/{}/status/'.format(url_host, pk)
    print(url, data)
    res = requests.post(
        url,
        headers = {"Content-Type": "application/json"},
        data = json.dumps(data),
        verify = False,
    )

def post_toponyms(url_host, pk, toponyms):
    import requests
    data = {'toponym_candidates':toponyms}
    url = '{}/map/post/{}/toponyms/'.format(url_host, pk)
    print(url, data)
    res = requests.post(
        url,
        headers = {"Content-Type": "application/json"},
        data = json.dumps(data),
        verify = False,
    )

def post_georef(url_host, pk, matched, final, transform, errors, bbox):
    import requests
    data = {'gcps_matched':matched,
            'gcps_final':final,
            'transform_estimation':transform,
            'error_calculation':errors,
            'bbox':bbox}
    url = '{}/map/post/{}/georef/'.format(url_host, pk)
    print(url, data)
    res = requests.post(
        url,
        headers = {"Content-Type": "application/json"},
        data = json.dumps(data),
        verify = False,
    )

#####################################

def run_action(action, map_id, respond_to, **kwargs):
    # call the correct function
    # upon completion, submits/adds the data to the maplocate website

    try:
        # mark as busy (gets deleted upon fail or completion)
        with open('busy_file.txt', mode='wb') as fobj:
            pass

        iminfo = kwargs.pop('image', {})
        priors = kwargs.pop('priors', {})

        if action in ('detect_toponyms','full_toponyms'):
            # post status
            post_status(respond_to, map_id, 'Processing', 'Performing toponym text label detection...')
            # get results
            results = detect_toponyms(kwargs['url'], kwargs.get('text_options',{}), kwargs.get('toponym_options',{}))
            toponyms = results['toponyms']
            print(toponyms)
            # get image info if not already provided
            if not iminfo:
                iminfo = results['image']
            # post toponyms
            post_toponyms(respond_to, map_id, toponyms)

            if action == 'full_toponyms':
                # fetch the newest toponyms from the website
                # which is based on the posted auto detected ones merged with the manual ones
                import requests
                url = '{}/map/download/{}/toponyms/'.format(respond_to, map_id)
                resp = requests.get(url)
                toponyms = json.loads(resp.content)
                # matching function expects a 'name' property
                for feat in toponyms['features']:
                    feat['properties']['name'] = feat['properties']['img_name']
                priors['toponym_candidates'] = toponyms

        if action in ('georef_toponyms','full_toponyms'):
            # match + estimate toponyms in one step
            # post status
            post_status(respond_to, map_id, 'Processing', 'Matching toponym coordinates...')
            # get results
            matched = match_toponyms(priors['toponym_candidates'], **kwargs.get('match_options', {}) )
            print(1, matched)

            # post status
            post_status(respond_to, map_id, 'Processing', 'Estimating transformation...')
            # get results
            results = estimate_transform(matched, image=iminfo, **kwargs.get('transform_options', {}) )
            transform,final,bbox = results['transform'], results['controlpoints'], results['bbox']
            errors = calculate_errors(final, transform, image=iminfo)
            print(2, transform, errors)
            # post transform
            post_georef(respond_to, map_id, matched, final, transform, errors, bbox)

    except:
        err = traceback.format_exc()
        print('Exception raised:', err)
        details = 'Processing error: {}'.format(err)
        post_status(respond_to, map_id, 'Failed', details)
    
    finally:
        # mark website as no longer busy
        os.remove('busy_file.txt')

