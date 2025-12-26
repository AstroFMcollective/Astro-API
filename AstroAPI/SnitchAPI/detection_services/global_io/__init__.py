from AstroAPI.SnitchAPI.components import *
from AstroAPI.InternalComponents.SystemMediaObjects import *
from AstroAPI.InternalComponents.Legacy import *
from AstroAPI.SnitchAPI.detection_services.global_io.components.generic import *

from AstroAPI.SnitchAPI.detection_services.global_io.components.check.song import check_song as check_song_ai
from AstroAPI.SnitchAPI.detection_services.global_io.components.check.music_video import check_music_video as check_mv_ai
from AstroAPI.SnitchAPI.detection_services.global_io.components.check.collection import check_collection as check_collection_ai
from AstroAPI.SnitchAPI.detection_services.global_io.components.check.media import check_media as check_media_ai

class GlobalIO:
	def __init__(self):
		self.service = service
		self.component = component
	
	async def check_song(self, service: object, id: str, song_country_code: str = None, lookup_country_code: str = 'us') -> SnitchAnalysis | Empty | Error:
		"""
			# Global Interface Song AI Check

			Check whether a song is AI-generated on every detection service via song ID.

			:param service: Search Catalog API Music service from which the ID originates from.
			:param id: Song ID.
			:param song_country_code: The country code of the country this ID is from.
			:param lookup_country_code: The country code of the country in which you want to conduct the check.
		"""
		return await check_song_ai(service = service, id = id, song_country_code = song_country_code, lookup_country_code = lookup_country_code)
	
	async def check_music_video(self, service: object, id: str, mv_country_code: str = None, lookup_country_code: str = 'us') -> SnitchAnalysis | Empty | Error:
		"""
			# Global Interface Music Video AI Check

			Check whether a music video is AI-generated on every detection service via video ID.

			:param service: Search Catalog API Music service from which the ID originates from.
			:param id: Video ID.
			:param song_country_code: The country code of the country this ID is from.
			:param lookup_country_code: The country code of the country in which you want to conduct the check.
		"""
		return await check_mv_ai(service = service, id = id, mv_country_code = mv_country_code, lookup_country_code = lookup_country_code)
	
	async def check_collection(self, service: object, id: str, collection_country_code: str = None, lookup_country_code: str= 'us') -> SnitchAnalysis | Empty | Error:
		"""
			# Global Interface Collection AI Check

			Check whether a collection is AI-generated on every detection service via collection ID.

			:param service: Search Catalog API Music service from which the ID originates from.
			:param id: Collection ID.
			:param song_country_code: The country code of the country this ID is from.
			:param lookup_country_code: The country code of the country in which you want to conduct the check.
		"""
		return await check_collection_ai(service = service, id = id, collection_country_code = collection_country_code, lookup_country_code = lookup_country_code)
	
	async def check_media(self, media: dict):
		"""
			# Global Interface Media AI Check

			Check whether an arbitrary Astro media object is AI-generated on every detection service.

			:param media: Astro media object JSON dict of the objecy you want to check.
			:param country_code: The country code of the country in which you want to conduct the check.
		"""
		return await check_media_ai(media = media)


	
global_io = GlobalIO()

print(f'[SnitchAPI] {component} initialized')
