from AstroAPI.components import *
from AstroAPI.media_services.music.global_io.components.generic import *
from asyncio import create_task, gather

from AstroAPI.media_services.music.global_io.components.search.song import search_song
# from AstroAPI.media_services.music.global_io.components.search.music_video import search_music_video
# from AstroAPI.media_services.music.global_io.components.search.collection import search_collection
# from AstroAPI.media_services.music.global_io.components.search.query import search_query
# from AstroAPI.media_services.music.global_io.components.lookup.song import lookup_song
# from AstroAPI.media_services.music.global_io.components.lookup.music_video import lookup_music_video
# from AstroAPI.media_services.music.global_io.components.lookup.collection import lookup_collection
# from AstroAPI.media_services.music.global_io.components.lookup.artist import lookup_artist



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
						
		return await search_song(artists, title, song_type, collection, is_explicit, country_code, include_premade_media, exclude_services)
	
global_io = GlobalIO()