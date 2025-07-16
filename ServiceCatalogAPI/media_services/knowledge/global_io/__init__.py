from ServiceCatalogAPI.components import *
from ServiceCatalogAPI.media_services.knowledge.global_io.components.generic import *

from ServiceCatalogAPI.media_services.knowledge.global_io.components.search.song import search_song as search_song_knowledge
from ServiceCatalogAPI.media_services.knowledge.global_io.components.search.query import search_query as search_query_knowledge
from ServiceCatalogAPI.media_services.knowledge.global_io.components.lookup.song import lookup_song as lookup_song_knowledge



class GlobalIO:
	def __init__(self):
		self.service = service
		self.component = component
		self.exclude_services = []

	async def search_song(self, artists: list, title: str, song_type: str = None, collection: str = None, is_explicit: bool = None, country_code: str = 'us', include_premade_media: list = [], exclude_services: list = []) -> Knowledge | Empty | Error:
		exclude_services.extend(self.exclude_services)
		exclude_services = remove_duplicates(exclude_services)
		for premade in include_premade_media:
			if premade.service not in exclude_services:
				exclude_services.append(premade.service)
		return await search_song_knowledge(artists, title, song_type, collection, is_explicit, country_code, include_premade_media, exclude_services)

	async def search_query(self, query: str, country_code: str = 'us', exclude_services: list = []) -> Knowledge | Empty | Error:
		exclude_services.extend(self.exclude_services)
		exclude_services = remove_duplicates(exclude_services)
		return await search_query_knowledge(query, country_code, exclude_services)

	async def lookup_song(self, service: object, id: str, song_country_code: str = None, lookup_country_code: str = 'us') -> Knowledge | Empty | Error:
		return await lookup_song_knowledge(service = service, id = id, song_country_code = song_country_code, lookup_country_code = lookup_country_code)



global_io = GlobalIO()