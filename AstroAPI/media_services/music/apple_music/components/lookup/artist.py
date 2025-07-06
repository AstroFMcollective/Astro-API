from AstroAPI.components import *
from AstroAPI.media_services.music.apple_music.components.generic import *

import aiohttp



async def lookup_artist(id: str, country_code: str = 'us') -> object:
	request = {'request': 'lookup_artist', 'id': id, 'country_code': country_code}
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
					artist = await response.json(content_type = 'text/javascript')
					artist = artist['results'][0]

					artist_url = artist['artistLinkUrl']
					artist_id = artist['artistId']
					artist_name = artist['artistName']
					artist_genre = artist['primaryGenreName'] if 'primaryGenreName' in artist else None

					return Artist(
						service = service,
						urls = artist_url,
						ids = artist_id,
						name = artist_name,
						genre = artist_genre,
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
						error_msg = "HTTP error when looking up artist ID",
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