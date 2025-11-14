from AstroAPI.InternalComponents.Legacy import *
from AstroAPI.SnitchAPI.components.media import *
from AstroAPI.SnitchAPI.tools.audio.apple_music.components.get_song_preview import get_song_preview
from AstroAPI.SnitchAPI.tools.audio.submithub.components.audio import check_audio_for_generative_ai as submithub_ai
from AstroAPI.SnitchAPI.tools.image.sightengine.components.image import check_image_for_generative_ai as sightengine_ai
from AstroAPI.SnitchAPI.components.generic import service as gservice, component as gcomponent

from AstroAPI.ServiceCatalogAPI.media_services.music.global_io import global_io
from AstroAPI.ServiceCatalogAPI.media_services.music import spotify, apple_music, youtube_music, deezer

from asyncio import create_task, gather



class SnitchAPI:
	def __init__(self):
		self.service = gservice
		self.component = gcomponent



	async def lookup_media(self, media: dict, lookup_country_code: str = 'us') -> object:
		# Prepare the request metadata
		request = {'request': 'snitch_media', 'lookup_country_code': lookup_country_code}
		# Record the start time for processing time calculation
		start_time = current_unix_time_ms()
		
		try:
			cover_order = [spotify.service, deezer.service, youtube_music.service, apple_music.service]
			tasks = []
			
			if media['type'] not in ['empty_response', 'error']:
				for service in cover_order:
					if service in media['cover']['hq_urls']:
						tasks.append(
							create_task(
								sightengine_ai(media['cover']['hq_urls'][service])
							)
						)
						break
				
				if apple_music.service in media['ids'] and media['type'] not in ['album', 'ep']:
					tasks.append(
						create_task(
							submithub_ai(await get_song_preview(media['ids'][apple_music.service], lookup_country_code))
						)
					)

				analysis = await gather(*tasks)

				if analysis != []:
					analysis = [item for item in analysis if item.media_type in ['image', 'audio']]

				if analysis != []:
					return SnitchAnalysis(
						service = gservice,
						analysis = analysis,
						analysed_media = media,
						meta = Meta(
							service = gservice,
							request = request,
							processing_time = current_unix_time_ms() - start_time,
							http_code = 200
						)
					)
				else:
					return Empty(
						service = self.service,
						meta = Meta(
							service = self.service,
							request = request,
							http_code = 204,
							processing_time = current_unix_time_ms() - start_time
						)
					)
			else:
				error = Error(
					service = gservice,
					component = gcomponent,
					error_msg = f'Bad request: invalid media provided',
					meta = Meta(
						service = self.service,
						request = request,
						http_code = 401,
						processing_time = current_unix_time_ms() - start_time
					)
				)
				await log(error)
				return error

		# If sinister things happen
		except Exception as error:
			error = Error(
				service = gservice,
				component = gcomponent,
				error_msg = f'Error when searching song: "{error}"',
				meta = Meta(
					service = self.service,
					request = request,
					http_code = 500,
					processing_time = current_unix_time_ms() - start_time
				)
			)
			await log(error, [discord.File(fp = StringIO(json.dumps(media, indent = 4)), filename = f'media.json')])
			return error



	async def lookup_song(self, service: object, id: str, song_country_code: str = None, lookup_country_code: str = 'us') -> object:
		# Prepare the request metadata
		request = {'request': 'snitch_song', 'service': service.service, 'id': id, 'song_country_code': song_country_code, 'lookup_country_code': lookup_country_code}
		# Record the start time for processing time calculation
		start_time = current_unix_time_ms()
		
		try:
			reference_media = await global_io.lookup_song(service, id, song_country_code, lookup_country_code)

			cover_order = [spotify.service, deezer.service, youtube_music.service, apple_music.service]
			tasks = []
			
			for service in cover_order:
				if service in reference_media.cover.hq_urls:
					tasks.append(
						create_task(
							sightengine_ai(reference_media.cover.hq_urls[service])
						)
					)
					break
			
			if apple_music.service in reference_media.ids:
				tasks.append(
					create_task(
						submithub_ai(await get_song_preview(reference_media.ids[apple_music.service], lookup_country_code))
					)
				)

			analysis = await gather(*tasks)

			if analysis != []:
				analysis = [item for item in analysis if item.media_type in ['image', 'audio']]

			if analysis != []:
				return SnitchAnalysis(
					service = gservice,
					analysis = analysis,
					analysed_media = reference_media,
					meta = Meta(
						service = gservice,
						request = request,
						processing_time = current_unix_time_ms() - start_time,
						http_code = 200
					)
				)
			else:
				return Empty(
					service = self.service,
					meta = Meta(
						service = self.service,
						request = request,
						http_code = 204,
						processing_time = current_unix_time_ms() - start_time
					)
				)

		# If sinister things happen
		except Exception as error:
			error = Error(
				service = gservice,
				component = gcomponent,
				error_msg = f'Error when searching song: "{error}"',
				meta = Meta(
					service = self.service,
					request = request,
					http_code = 500,
					processing_time = current_unix_time_ms() - start_time
				)
			)
			await log(error)
			return error
		
	

	async def lookup_collection(self, service: object, id: str, song_country_code: str = None, lookup_country_code: str = 'us') -> object:
		# Prepare the request metadata
		request = {'request': 'snitch_collection', 'service': service.service, 'id': id, 'song_country_code': song_country_code, 'lookup_country_code': lookup_country_code}
		# Record the start time for processing time calculation
		start_time = current_unix_time_ms()
		
		try:
			reference_media = await global_io.lookup_collection(service, id, song_country_code, lookup_country_code)

			cover_order = [spotify.service, deezer.service, youtube_music.service, apple_music.service]
			tasks = []
			
			for service in cover_order:
				if service in reference_media.cover.hq_urls:
					tasks.append(
						create_task(
							sightengine_ai(reference_media.cover.hq_urls[service])
						)
					)
					break

			analysis = await gather(*tasks)

			if analysis != []:
				analysis = [item for item in analysis if item.media_type in ['image', 'audio']]

			if analysis != []:
				return SnitchAnalysis(
					service = gservice,
					analysis = analysis,
					analysed_media = reference_media,
					meta = Meta(
						service = gservice,
						request = request,
						processing_time = current_unix_time_ms() - start_time,
						http_code = 200
					)
				)
			else:
				return Empty(
					service = self.service,
					meta = Meta(
						service = self.service,
						request = request,
						http_code = 500,
						processing_time = current_unix_time_ms() - start_time
					)
				)

		# If sinister things happen
		except Exception as error:
			error = Error(
				service = gservice,
				component = gcomponent,
				error_msg = f'Error when searching song: "{error}"',
				meta = Meta(
					service = self.service,
					request = request,
					http_code = 500,
					processing_time = current_unix_time_ms() - start_time
				)
			)
			await log(error)
			return error
		
	

	async def lookup_music_video(self, service: object, id: str, song_country_code: str = None, lookup_country_code: str = 'us') -> object:
		# Prepare the request metadata
		request = {'request': 'snitch_music_video', 'service': service.service, 'id': id, 'song_country_code': song_country_code, 'lookup_country_code': lookup_country_code}
		# Record the start time for processing time calculation
		start_time = current_unix_time_ms()
		
		try:
			reference_media = await global_io.lookup_music_video(service, id, song_country_code, lookup_country_code)

			cover_order = [youtube_music.service, apple_music.service]
			tasks = []
			
			for service in cover_order:
				if service in reference_media.cover.hq_urls:
					tasks.append(
						create_task(
							sightengine_ai(reference_media.cover.hq_urls[service])
						)
					)
					break

			if apple_music.service in reference_media.ids:
				tasks.append(
					create_task(
						submithub_ai(await get_song_preview(reference_media.ids[apple_music.service], lookup_country_code))
					)
				)

			analysis = await gather(*tasks)

			if analysis != []:
				analysis = [item for item in analysis if item.media_type in ['image', 'audio']]

			if analysis != []:
				return SnitchAnalysis(
					service = gservice,
					analysis = analysis,
					analysed_media = reference_media,
					meta = Meta(
						service = gservice,
						request = request,
						processing_time = current_unix_time_ms() - start_time,
						http_code = 200
					)
				)
			else:
				return Empty(
					service = self.service,
					meta = Meta(
						service = self.service,
						request = request,
						http_code = 500,
						processing_time = current_unix_time_ms() - start_time
					)
				)

		# If sinister things happen
		except Exception as error:
			error = Error(
				service = gservice,
				component = gcomponent,
				error_msg = f'Error when searching song: "{error}"',
				meta = Meta(
					service = self.service,
					request = request,
					http_code = 500,
					processing_time = current_unix_time_ms() - start_time
				)
			)
			await log(error)
			return error
		


snitch = SnitchAPI()
print("[SnitchAPI] Snitch API initialized")
