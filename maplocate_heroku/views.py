from django.shortcuts import render, redirect
from django.http import HttpResponse

import json

def run_action(request):
    print('job started')

    # get input data as json dict passed through environment variable
    action = request.POST['MAPLOCATE_ACTION']
    mapid = request.POST['MAPLOCATE_MAPID']
    respond_to = request.POST['MAPLOCATE_HOST']
    data = json.loads(request.POST['MAPLOCATE_KWARGS'])
    print(action,mapid,respond_to,data)

    import run_job
    run_job.run_action(action, mapid, respond_to, **data)

    print('job finished')
    return HttpResponse('')
