from __future__ import absolute_import
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from main.tasks import updateBanner, updateBanners
from celery.result import AsyncResult
from main.models import LastUpdateState, AlreadyRunning

@ensure_csrf_cookie
def index(request):
	return render(request, 'main/index.html')

def request_update(request):
	updaterTask = UpdaterTask.get_or_create()
	if updaterTask.isRunning:
		pass
	
	updaterTask.run()

def check_update(request):
	pass
	

def request_update(request):
	responseDict = {}
	try:
		LastUpdateState.update_exclusive()
	except AlreadyRunning:
		responseDict = {'msg': 'Task already running'}
	
	response = JsonResponse(responseDict)
	return response

def get_task_status(request):
	responseDict = {"current": 0, "total": 0, "state": "idle"}
	last_update = LastUpdateState.objects.get(pk=1)
	task_id = last_update.task_id
	if task_id != "":
		res = AsyncResult(task_id)
		responseDict["state"] = res.state
		if res.state == "PROGRESS":
			responseDict["current"] = res.info.get("current")
			responseDict["total"] = res.info.get("total")
		else:
			responseDict["current"] = last_update.num_processed
			responseDict["total"] = last_update.num_total
	
	return JsonResponse(responseDict)
