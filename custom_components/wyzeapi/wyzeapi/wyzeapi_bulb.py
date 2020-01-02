import logging

_LOGGER = logging.getLogger(__name__)

class WyzeBulb():
	def __init__(self, api, device_mac, friendly_name, state):
		self._api = api
		self._device_mac = device_mac
		self._friendly_name = friendly_name
		self._state = state
		self._brightness = self._colortemp = None
		self._just_changed_state = False

	def turn_on(self):
		_LOGGER.debug("Turning on: " + self._device_mac + " with brightness: " + str(self._brightness) + " and color temp: " + str(self._colortemp))

		if self._colortemp is not None or self._brightness is not None:
			url = 'https://api.wyzecam.com/app/v2/device/set_property_list'

			property_list = [{"pid": "P3", "pvalue": "1"}]

			if self._brightness:
				brightness = self.translate(self._brightness, 1, 255, 1, 100)
				property_list.append({"pid": "P1501", "pvalue": brightness})

			if self._colortemp:
				colortemp = self.translate(self._colortemp, 500, 140, 2700, 6500)
				property_list.append({"pid": "P1502", "pvalue": colortemp})

			payload = {
				"phone_id": self._api._device_id,
				"property_list": property_list,
				"device_model": "WLPA19",
				"app_name": "com.hualai.WyzeCam",
				"app_version": "2.6.62",
				"sc": "01dd431d098546f9baf5233724fa2ee2",
				"sv": "a8290b86080a481982b97045b8710611",
				"device_mac": self._device_mac,
				"app_ver": "com.hualai.WyzeCam___2.6.62",
				"ts": "1575951274357",
				"access_token": self._api._access_token
			}

		else:
			url = 'https://api.wyzecam.com/app/v2/device/set_property'

			payload = {
				'phone_id': self._api._device_id,
				'access_token': self._api._access_token,
				'device_model': 'WLPA19',
				'ts': '1575948896791',
				'sc': '01dd431d098546f9baf5233724fa2ee2',
				'sv': '107693eb44244a948901572ddab807eb',
				'device_mac': self._device_mac,
				'pvalue': "1",
				'pid': 'P3',
				'app_ver': 'com.hualai.WyzeCam___2.6.62'
			}

		self._api._request_man.do_request(url, payload)

		self._state = True
		self._just_changed_state = True

	def turn_off(self):
		_LOGGER.debug("Turning off: " + self._device_mac)

		url = 'https://api.wyzecam.com/app/v2/device/set_property'

		payload = {
			'phone_id': self._api._device_id,
			'access_token': self._api._access_token,
			'device_model': 'WLPA19',
			'ts': '1575948896791',
			'sc': '01dd431d098546f9baf5233724fa2ee2',
			'sv': '107693eb44244a948901572ddab807eb',
			'device_mac': self._device_mac,
			'pvalue': "0",
			'pid': 'P3',
			'app_ver': 'com.hualai.WyzeCam___2.6.62'
		}

		self._api._request_man.do_request(url, payload)

		self._state = False
		self._just_changed_state = True

	def is_on(self):
		return self._state

	def update(self):
		if self._just_changed_state:
			self._just_changed_state = False
		else:
			url = "https://api.wyzecam.com/app/v2/device/get_property_list"

			payload = {
				"target_pid_list":[],
				"phone_id": self._api._device_id,
				"device_model":"WLPA19",
				"app_name":"com.hualai.WyzeCam",
				"app_version":"2.6.62",
				"sc":"01dd431d098546f9baf5233724fa2ee2",
				"sv":"22bd9023a23b4b0b9977e4297ca100dd",
				"device_mac": self._device_mac,
				"app_ver":"com.hualai.WyzeCam___2.6.62",
				"phone_system_type":"1",
				"ts":"1575955054511",
				"access_token": self._api._access_token
			}

			data = self._api._request_man.do_blocking_request(url, payload)

			for item in data['data']['property_list']:
				if item['pid'] == "P3":
					self._state = True if int(item['value']) == 1 else False
				elif item['pid'] == "P1501":
					self._brightness = self.translate(int(item['value']), 0, 100, 0, 255)
				elif item['pid'] == "P1502":
					self._colortemp = self.translate(int(item['value']), 2700, 6500, 500, 153)

	def translate(self, value, leftMin, leftMax, rightMin, rightMax):
		# Figure out how 'wide' each range is
		leftSpan = leftMax - leftMin
		rightSpan = rightMax - rightMin

		# Convert the left range into a 0-1 range (float)
		valueScaled = float(value - leftMin) / float(leftSpan)

		# Convert the 0-1 range into a value in the right range.
		return rightMin + (valueScaled * rightSpan)
