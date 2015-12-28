from __future__ import absolute_import
from time import sleep

from celery import shared_task, task
from updateBanner.celery import app
from celery.utils.log import get_task_logger
from .api_yandex import apiGetCampaignsIds, apiGetBanners, ApiError

logger = get_task_logger(__name__)

@shared_task
def add(x,y):
	return x + y

@app.task(bind=True)
def updateBanner(self):
	try:
		lastUpdateState = LastUpdateState.objects.get(pk=1)
		logger.info("startting to update id={}".format(lastUpdateState.pk))
		lastUpdateState.update_state(0, 10)
		self.update_state(state='PROGRESS', meta={'current': 0, 'total': 10})
		for i in range(10):
			sleep(1)
			lastUpdateState.update_state(i)
			self.update_state(state='PROGRESS', meta={'current': i, 'total': 10})
			logger.info("updating banner {} out of {}".format(i, 10))
		logger.info("Finished updating")
	except Exception:
		logger.error("Unknown exception during task run")
		raise
	return

@app.task(bind=True)
def updateBanners(self):
	from main.models import LastUpdateState, Banner
	lastUpdateState = LastUpdateState.objects.get(pk=1)
	try:
		# Get campaign ids from yandex.direct
		campaign_ids = apiGetCampaignsIds()
		# Now we know total number of campaigns. Update status in DB
		lastUpdateState.update_state(0, len(campaign_ids))
		# For each campaign, get its banners from yandex.direct
		campaign_indx = 0
		for campaign_id in campaign_ids:
			banners = apiGetBanners(campaign_id)
			# Extract list of banner ids existing in DB for this campaign
			banner_ids_db = Banner.getCampaignBannerIds(campaign_id)
			# Extract banner ids from resulting set. Leave out only banners that do not exist in DB yet
			banner_ids_yd = [banner[u"BannerID"] for banner in banners]
			new_banner_ids = []
			if len(banner_ids_yd) > 0 and len(banner_ids_db) > 0:
				new_banner_ids = list(set(banner_ids_yd) - set(banner_ids_db))
			else:
				new_banner_ids = banner_ids_yd
			new_banners = (banner for banner in banners if banner[u"BannerID"] in new_banner_ids)
			# If there are banners not in DB yet, upload them
			for banner in new_banners:
				bannerObj = Banner(
					update_result_key=lastUpdateState.update_result_key,
					campaign_id=campaign_id,
					banner_id=banner["uBannerId"]
					)
				bannerObj.save()
			# After successful DB insert, update task status
			campaign_indx += 1
			lastUpdateState.update_state(campaign_indx, len(campaign_ids))
			self.update_state(state='PROGRESS', 
				meta={'current': campaign_indx, 'total': len(campaign_ids)})
	except Exception:
		logger.error("Unknown exception during task run")
		lastUpdateState.status = LastUpdateState.FAIL
		lastUpdateState.save()
		raise
	else:
		lastUpdateState.status = LastUpdateState.SUCCESS
		lastUpdateState.save()
	return
