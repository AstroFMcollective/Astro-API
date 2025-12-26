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
		self._service = service
		self._type = 'error'
		self._component = component
		self._error_msg = error_msg
		self._meta = meta

	# Service
	@property
	def service(self):
		return self._service

	@service.setter
	def service(self, value: str):
		self._service = value

	# Type (constant)
	@property
	def type(self):
		return self._type

	# Component
	@property
	def component(self):
		return self._component

	@component.setter
	def component(self, value: str):
		self._component = value

	# Error message
	@property
	def error_msg(self):
		return self._error_msg

	@error_msg.setter
	def error_msg(self, value: str):
		self._error_msg = value

	# Meta
	@property
	def meta(self):
		return self._meta

	@meta.setter
	def meta(self, value: object):
		self._meta = value

	# JSON representation
	@property
	def json(self):
		meta_val = self._meta.json if hasattr(self._meta, 'json') else self._meta
		return {
			'service': self._service,
			'type': self._type,
			'component': self._component,
			'error_msg': self._error_msg,
			'meta': meta_val
		}