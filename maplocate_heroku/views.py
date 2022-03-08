from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

import os
import json

@csrf_exempt
def run_action(request):
    print('job request received')

    # get input data as json dict passed through body (POST)
    POST = json.loads(request.body)
    action = POST['MAPLOCATE_ACTION']
    mapid = POST['MAPLOCATE_MAPID']
    respond_to = POST['MAPLOCATE_HOST']
    data = json.loads(POST['MAPLOCATE_KWARGS'])
    print(action,mapid,respond_to,data)

    # exit early if worker/website is already busy
    # (ie only allow one run_action to run per worker/website)
    print('pwd',os.path.abspath(''))
    print('listdir',os.listdir(''))
    if os.path.lexists('busy_file.txt'):
        return HttpResponse(status=503)

    from . import run_job
    #run_job.run_action(action, mapid, respond_to, **data)
    from threading import Thread
    thread = Thread(target=run_job.run_action, args=(action, mapid, respond_to), kwargs=data)
    thread.start()

    print('job request started')
    return HttpResponse(status=200)
