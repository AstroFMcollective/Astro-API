from AstroAPI.components import *
from AstroAPI.media_services.music.apple_music.components.generic import *
import aiohttp



async def lookup_artist(id: str, country_code: str = 'us') -> object:
	async with aiohttp.ClientSession() as session:
		request = {'request': 'lookup_artist', 'id': id, 'country_code': country_code}
		api_url = f'{api}/lookup'
		api_params = {
			'id': id,
			'country': country_code.lower()
		}
		timeout = aiohttp.ClientTimeout(total = 30)
		start_time = current_unix_time_ms()

		async with session.get(url = api_url, params = api_params, timeout = timeout) as response:
			if response.status == 200:
				artist = await response.json(content_type = 'text/javascript')
				artist = artist['results'][0]

				artist_url = artist['artistLinkUrl']
				artist_id = artist['artistId']
				artist_name = artist['artistName']
				artist_genres = artist['primaryGenreName'] if 'primaryGenreName' in artist else None
				artist_profile_picture = ProfilePicture(
					service = service,
					user_type = 'artist',
					hq_urls = None,
					lq_urls = None,
					color_hex = None,
					meta = Meta(
						service = service,
						request = request,
						processing_time = current_unix_time_ms() - start_time,
						filter_confidence_percentage = {service: 100.0},
						http_code = response.status
                    )
                )
				
				return Artist(
					service = service,
					urls = artist_url,
					ids = artist_id,
					name = artist_name,
					profile_picture = artist_profile_picture,
					genre = artist_genres,
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