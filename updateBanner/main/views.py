from __future__ import absolute_import
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from main.tasks import updateBanner, updateBanners
from celery.result import AsyncResult

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
	print("old task_id: {}".format(request.session.get("task_id")))
	if request.session.get("task_id", False):
		res = AsyncResult(request.session["task_id"])
		responseDict["state"] = res.state
		try:
			responseDict["current"] = res.info.get("current")
			responseDict["total"] = res.info.get("total")
		except AttributeError:
			pass
			
		if res.state in ("SUCCESS", "FAILURE"):
			del request.session["task_id"]
	else:
		print("starting new task")
		# start new task
		res = updateBanners.delay()
		request.session["task_id"] = res.id
		print("new task started! id: {}, state: {}".format(res.id, res.state))
	
	response = JsonResponse(responseDict)
	return response

def get_task_status(request):
	responseDict = {"current": 0, "total": 0, "state": "running"}
	return JsonResponse(responseDict)
