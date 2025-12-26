class Empty:
	"""
		# Astro API Empty Object

		This is a built-in Service Catalog API object which identifies empty responses.
		Use this to return *a thing* when a service you're using doesn't end up
		returning anything/returns an empty response.
		JSON representation available.

		 :param	service: The API service in which the object was formed.
		 :param meta: The technical metadata of this object.
	"""

	def __init__(self, service: str, meta: object) -> object:
		self._service = service
		self._type = 'empty_response'
		self._meta = meta

	# Service
	@property
	def service(self):
		return self._service

	@service.setter
	def service(self, value: str):
		self._service = value

	# Type
	@property
	def type(self):
		return self._type

	@type.setter
	def type(self, value: str):
		self._type = value

	# Metadata
	@property
	def meta(self):
		return self._meta

	@meta.setter
	def meta(self, value: object):
		self._meta = value

	# Compatibility method (kept for API parity)
	def regenerate_json(self):
		# no-op because json/json_lite are properties
		return self.json, self.json_lite

	# JSON representation
	@property
	def json(self):
		meta_val = self._meta.json if hasattr(self._meta, 'json') else self._meta
		return {
			'service': self._service,
			'type': self._type,
			'meta': meta_val
		}