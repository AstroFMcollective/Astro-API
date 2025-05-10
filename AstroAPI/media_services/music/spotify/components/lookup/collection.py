from AstroAPI.components import *
from AstroAPI.media_services.music.spotify.components.generic import *
from AstroAPI.media_services.music.spotify.components.generic.get_token import spotify_token
import aiohttp



async def lookup_collection(id: str, country_code: str = 'us') -> object:
	request = {'request': 'lookup_collection', 'id': id, 'country_code': country_code}
	start_time = current_unix_time_ms()

	try:
		async with aiohttp.ClientSession() as session:
			api_url = f'{api}/albums/{id}'
			api_params = {
				'market': country_code.upper(),
			}
			api_headers = {'Authorization': f'Bearer {await spotify_token.get_token()}'}
			timeout = aiohttp.ClientTimeout(total = 30)

			async with session.get(url = api_url, headers = api_headers, timeout = timeout, params = api_params) as response:
				if response.status == 200:
					collection = await response.json()

					collection_type = ('album' if collection['album_type'] != 'single' else 'ep')
					collection_url = collection['external_urls']['spotify']
					collection_id = collection['id']
					collection_title = remove_feat(collection['name'])
					collection_artists = get_artists_of_media(request, collection['artists'])
					collection_year = collection['release_date'][:4]
					
					media_cover = Cover(
						service = service,
						media_type = collection_type,
						title = collection_title,
						artists = collection_artists,
						hq_urls = collection['images'][0]['url'] if collection['images'] != [] else None,
						lq_urls = collection['images'][len(collection['images']) - 1]['url'] if collection['images'] != [] else None,
						meta = Meta(
							service = service,
							request = request,
							processing_time = 0,
							filter_confidence_percentage = 100.0,
							http_code = 200
						)
					)

					return Collection(
						service = service,
						type = collection_type,
						urls = collection_url,
						ids = collection_id,
						title = collection_title,
						artists = collection_artists,
						release_year = collection_year,
						cover = media_cover,
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
						error_msg = "HTTP error when looking up collection ID",
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