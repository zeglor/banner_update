import json, urllib2
from updateBanner.secret import yandex_api_token

def apiRequest(method_name, **kwargs):
	"""
	Calls yandex.direct api method and returns request result. 
	
	Attributes:
		method_name	-- name of api method to be called (ex. "GetCampaignsList")
		**kwargs	-- optional key->value list of parameters to be included into request
			(needed in GetBannersList call to specify campaign id)
	"""
	url = 'https://api.direct.yandex.ru/v4/json'
	# Setup request variables
	data = {
		'method': method_name,
		'token': yandex_api_token,
		'locale': 'ru',
	}
	# If optional parameters passed, add them to request variables
	if len(kwargs) > 0:
		data['param'] = kwargs
	
	jdata = json.dumps(data, ensure_ascii=False).encode('utf8')
	try:
		response = urllib2.urlopen(url, jdata).read()
	except URLError:
		raise ApiGeneralError("Cannot connect to {}".format(url))
	except Exception as e:
		raise ApiGeneralError("Unknown error during request.")
	
	json_response = json.loads(response.decode('utf8'))
	res = []
	try:
		res = json_response["data"]
	except KeyError as e:
		# Maybe api error happened?
		try:
			error_code = json_response[u"error_code"]
			error_str = json_response[u"error_str"]
			raise ApiCallError(error_code, error_str)
		except Exception as e:
			raise ApiGeneralError("Unknown error during request result unpacking. Type: {}; Value: ".\
				format(type(e), e))
	except Exception as e:
		raise ApiGeneralError("Unknown error during request result unpacking. Type: {}; Value: ".\
				format(type(e), e))
	
	return res

def apiGetCampaignsIds():
	"""
	Returns list of all campaign ids.
	"""
	res = apiRequest("GetCampaignsList")
	return [campaign[u"CampaignID"] for campaign in res]

def apiGetBanners(campaign_id):
	"""
	Returns list of banner dicts. More info at 
	https://tech.yandex.ru/direct/doc/dg-v4/reference/GetBanners-docpage/
	"""
	id_list = [campaign_id]
	res = apiRequest("GetBanners", CampaignIDS=id_list)
	return res

class ApiError(Exception):
	"""
	Base class for yandex api module exception.
	
	Attributes:
		msg	-- error description
	"""
	def __init__(self, msg):
		self.msg = msg

class ApiCallError(ApiError):
	"""
	Error happened during api call due to incorrect parameters, ...
	
	Attributes:
		num	-- yandex error number
		msg	-- yandex error description
	More info at https://tech.yandex.ru/direct/doc/dg-v4/reference/ErrorCodes-docpage/
	"""
	def __init__(self, num, msg):
		super().__init__(msg)
		self.num = num

class ApiGeneralError(ApiError):
	"""
	Unknown error.
	"""
	def __init__(self, msg):
		super().__init__(msg)
