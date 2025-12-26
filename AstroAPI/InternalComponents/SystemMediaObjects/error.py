class Error:

	"""
		# Astro API Error Object

		This is a built-in general-purpose API object which identifies errors.
		Use this to return *a thing* when something internally goes wrong.
		JSON representation available.

		 :param	service: The API service in which the object was formed.
		 :param component: The API service component in which the object was formed.
		 :param error_msg: Optional, but recommended. The error message of the error.
		 :param meta: The technical metadata of this object.
	"""

	def __init__(self, service: str, component: str, meta: object, error_msg: str = None) -> object:
		type = 'error'

		self.service = service
		self.type = type
		self.component = component
		self.error_msg = error_msg
		self.meta = meta
		self.regenerate_json()

	def regenerate_json(self):
		self.json = {
			'service': self.service,
			'type': self.type,
			'component': self.component,
			'error_msg': self.error_msg,
			'meta': self.meta.json
		}
		self.json_lite = {
			'service': self.service,
			'type': self.type,
			'component': self.component,
			'error_msg': self.error_msg,
			'meta': self.meta.json
		}