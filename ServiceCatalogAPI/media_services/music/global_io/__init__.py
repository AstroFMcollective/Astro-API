from ServiceCatalogAPI.components import *
from ServiceCatalogAPI.media_services.music.global_io.components.generic import *

from ServiceCatalogAPI.media_services.music.global_io.components.search.song import search_song as search_song_music
from ServiceCatalogAPI.media_services.music.global_io.components.search.music_video import search_music_video as search_music_video_music
from ServiceCatalogAPI.media_services.music.global_io.components.search.collection import search_collection as search_collection_music
from ServiceCatalogAPI.media_services.music.global_io.components.search.query import search_query as search_query_music
from ServiceCatalogAPI.media_services.music.global_io.components.lookup.song import lookup_song as lookup_song_music
from ServiceCatalogAPI.media_services.music.global_io.components.lookup.music_video import lookup_music_video as lookup_music_video_music
from ServiceCatalogAPI.media_services.music.global_io.components.lookup.collection import lookup_collection as lookup_collection_music



class GlobalIO:
	def __init__(self):
		self.service = service
		self.component = component
		self.exclude_services = []

	async def search_song(self, artists: list, title: str, song_type: str = None, collection: str = None, is_explicit: bool = None, country_code: str = 'us', include_premade_media: list = [], exclude_services: list = []) -> Song | Empty | Error:
		exclude_services.extend(self.exclude_services)
		exclude_services = remove_duplicates(exclude_services)
		for premade in include_premade_media:
			if premade.service not in exclude_services:
				exclude_services.append(premade.service)
		return await search_song_music(artists, title, song_type, collection, is_explicit, country_code, include_premade_media, exclude_services)
	
	async def search_music_video(self, artists: list, title: str, is_explicit: bool = None, country_code: str = 'us', include_premade_media: list = [], exclude_services: list = []) -> MusicVideo | Empty | Error:
		exclude_services.extend(self.exclude_services)
		exclude_services = remove_duplicates(exclude_services)
		for premade in include_premade_media:
			if premade.service not in exclude_services:
				exclude_services.append(premade.service)
		return await search_music_video_music(artists, title, is_explicit, country_code, include_premade_media, exclude_services)
	
	async def search_collection(self, artists: list, title: str, year: int = None, country_code: str = 'us', include_premade_media: list = [], exclude_services: list = []) -> Collection | Song | Empty | Error:
		exclude_services.extend(self.exclude_services)
		exclude_services = remove_duplicates(exclude_services)
		for premade in include_premade_media:
			if premade.service not in exclude_services:
				exclude_services.append(premade.service)
		return await search_collection_music(artists, title, year, country_code, include_premade_media, exclude_services)

	async def search_query(self, query: str, country_code: str = 'us', exclude_services: list = []) -> Song | MusicVideo | Collection | Empty | Error:
		exclude_services.extend(self.exclude_services)
		exclude_services = remove_duplicates(exclude_services)
		return await search_query_music(query, country_code, exclude_services)
	
	async def lookup_song(self, service: object, id: str, song_country_code: str = None, lookup_country_code: str = 'us') -> Song | Empty | Error:
		return await lookup_song_music(service = service, id = id, song_country_code = song_country_code, lookup_country_code = lookup_country_code)
	
	async def lookup_music_video(self, service: object, id: str, mv_country_code: str = None, lookup_country_code: str = 'us') -> MusicVideo | Empty | Error:
		return await lookup_music_video_music(service = service, id = id, mv_country_code = mv_country_code, lookup_country_code = lookup_country_code)
	
	async def lookup_collection(self, service: object, id: str, collection_country_code: str = None, lookup_country_code: str= 'us') -> Collection | Song | Empty | Error:
		return await lookup_collection_music(service = service, id = id, collection_country_code = collection_country_code, lookup_country_code = lookup_country_code)


	
global_io = GlobalIO()