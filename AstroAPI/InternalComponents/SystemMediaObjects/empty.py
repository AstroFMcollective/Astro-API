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
		type = 'empty_response'

		self.service = service
		self.type = type
		self.meta = meta
		self.regenerate_json()

	def regenerate_json(self):
		self.json = {
			'service': self.service,
			'type': self.type,
			'meta': self.meta.json
		}
		self.json_lite = {
			'service': self.service,
			'type': self.type,
			'meta': self.meta.json
		}