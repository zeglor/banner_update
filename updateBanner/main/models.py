from __future__ import unicode_literals

from django.db import models, transaction
from django.utils import timezone
from main.tasks import updateBanners

class BaseUpdateTask(models.Model):
	"""
	Base class for LastUpdateTask and UpdateResult. Holds common fields of 2 classes
	Not used on its own.
	"""
	# Available states
	NOT_RUN = 'NOT_RUN'
	FAIL    = 'FAIL   '
	SUCCESS = 'SUCCESS'
	RUNNING = 'RUNNING'
	STATUS_CHOICES = (
		(NOT_RUN, 'Not run'),
		(FAIL, 'Failed'),
		(SUCCESS, 'Succeeded'),
		(RUNNING, 'Running'),
	)
	
	# Actual fields
	status           = models.CharField(max_length = 7, 
										choices=STATUS_CHOICES,
										default=NOT_RUN)
	num_processed    = models.IntegerField(default=0)
	num_total        = models.IntegerField(default=0)
	
	class Meta:
		abstract = True

class UpdateResult(BaseUpdateTask):
	# Stores update tasks information
	started_datetime = models.DateTimeField()
	ended_datetime   = models.DateTimeField(null=True, default=None)

class LastUpdateState(BaseUpdateTask):
	update_result_key= models.ForeignKey(UpdateResult, null=True)
	task_id = models.CharField(max_length = 200, default = '')
	
	def update_state(self, num_processed, num_total=None):
		"""
		Update state of LastUpdateState instance and bound UpdateResult instance
		"""
		with transaction.atomic():
			#get bound updateResult instance
			updateResult = self.update_result_key
			
			self.num_processed = num_processed
			updateResult.num_processed = num_processed
			if num_total is not None:
				self.num_total = num_total
				updateResult.num_total = num_total
			
			self.save()
			updateResult.save()
	
	def update_status(self, status):
		"""
		Update status of LastUpdateState instance and bound UpdateResult instance
		"""
		with transaction.atomic():
			#get bound updateResult instance
			updateResult = self.update_result_key
			
			self.status = status
			updateResult.status = status
			
			if status in (self.FAIL, self.SUCCESS):
				updateResult.ended_datetime = timezone.now()
			
			if status == self.RUNNING:
				updateResult.started_datetime = timezone.now()
			
			updateResult.save()
			self.save()
	
	@classmethod
	def update_exclusive(cls):
		"""
		Tries to launch update task. If such task is already running,
		throws AlreadyRunning exception
		"""
		# Assume for now that status row already exists
		with transaction.atomic():
			# Setup function to be called on transaction successful commit
			transaction.on_commit(launch_update)
			
			lastUpdateState = LastUpdateState.objects.filter(pk=1).select_for_update()[0]
			if lastUpdateState.status == cls.RUNNING:
				raise AlreadyRunning
			# Task is not running. We can start new task
			# First, create new UpdateResult instance
			updateResult = UpdateResult(status=cls.RUNNING, started_datetime=timezone.now())
			updateResult.save()
			# Now update lastUpdateState instance
			lastUpdateState.update_result_key = updateResult
			lastUpdateState.status = cls.RUNNING
			lastUpdateState.save()

class Banner(models.Model):
	update_result_key = models.ForeignKey(UpdateResult, on_delete=models.CASCADE)
	campaign_id = models.BigIntegerField(db_index=True, default=0)
	banner_id = models.BigIntegerField(default=0)
	# yandex information fields
	title = models.CharField(max_length = 200, default="")
	
	@classmethod
	def getCampaignBannerIds(cls, campaign_id):
		"""
		Returns list of banner_id for Banner objecs with specified campaign_id
		"""
		banners = cls.objects.filter(campaign_id=campaign_id)
		return [banner.banner_id for banner in banners]
	
	@staticmethod
	def fromDict(d, update_res):
		"""
		Returns Banner object with data from passed dict
		"""
		campaign_id = d.get('CampaignID', 0)
		banner_id = d.get('BannerID', 0)
		title = d.get('Title', '')
		
		banner = Banner(
			update_result_key = update_res,
			campaign_id=campaign_id,
			banner_id=banner_id,
			title=title,
		)
		
		return banner

def launch_update():
	"""
	Starts celery task and updates db record with task id
	"""
	last_update_result = LastUpdateState.objects.get(pk=1)
	task = updateBanners.delay()
	last_update_result.task_id = task.id
	last_update_result.save()

class AlreadyRunning(Exception):
	pass
