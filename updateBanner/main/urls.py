from django.conf.urls import url
from main import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^request_update/$', views.request_update, name='update'),
	url(r'^status/$', views.get_task_status, name='task_status'),
]
