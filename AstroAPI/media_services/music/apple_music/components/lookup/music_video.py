from AstroAPI.components import *
from AstroAPI.media_services.music.apple_music.components.generic import *
from AstroAPI.media_services.music.apple_music.components.lookup.artist import lookup_artist

import aiohttp



async def lookup_music_video(id: str, country_code: str = 'us') -> object:
	request = {'request': 'lookup_music_video', 'id': id, 'country_code': country_code}
	start_time = current_unix_time_ms()

	try:
		async with aiohttp.ClientSession() as session:
			api_url = f'{api}/lookup'
			api_params = {
				'id': id,
				'country': country_code.lower()
			}
			timeout = aiohttp.ClientTimeout(total = 30)

			async with session.get(url = api_url, params = api_params, timeout = timeout) as response:
				if response.status == 200:
					video = await response.json(content_type = 'text/javascript')
					video = video['results'][0]

					mv_url = video['trackViewUrl']
					mv_id = video['trackId']
					mv_title = video['trackName']
					mv_artist = await lookup_artist(id = video['artistId'], country_code = country_code)
					mv_artist = [mv_artist]
					mv_is_explicit = not 'not' in video['trackExplicitness']
					mv_genre = video['primaryGenreName'] if 'primaryGenreName' in video else None

					mv_thumbnail = Cover(
						service = service,
						media_type = 'music_video',
						title = mv_title,
						artists = mv_artist,
						hq_urls = video['artworkUrl100'],
						lq_urls = video['artworkUrl60'],
						color_hex = None,
						meta = Meta(
							service = service,
							request = request,
							processing_time = current_unix_time_ms() - start_time,
							filter_confidence_percentage = {service: 100.0},
							http_code = response.status
						)
					)

					return MusicVideo(
						service = service,
						urls = mv_url,
						ids = mv_id,
						title = mv_title,
						artists = mv_artist,
						is_explicit = mv_is_explicit,
						cover = mv_thumbnail,
						genre = mv_genre,
						meta = Meta(
							service = service,
							request = request,
							processing_time = current_unix_time_ms() - start_time,
							filter_confidence_percentage = {service: 100.0},
							http_code = response.status
						)
					)

				else:
					error = Error(
						service = service,
						component = component,
						error_msg = "HTTP error when looking up music video ID",
						meta = Meta(
							service = service,
							request = request,
							processing_time = current_unix_time_ms() - start_time,
							http_code = response.status
						)
					)
					await log(error)
					return error

	except Exception as error:
		error = Error(
			service = service,
			component = component,
			error_msg = f'Error when looking up collection: "{error}"',
			meta = Meta(
				service = service,
				request = request,
				http_code = 500,
				processing_time = {service: current_unix_time_ms() - start_time}
			)
		)
		await log(error)
		return error