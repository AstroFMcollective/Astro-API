from AstroAPI.components import *
from AstroAPI.media_services.music.spotify.components.generic import *
from AstroAPI.media_services.music.spotify.components.generic.get_token import spotify_token
import aiohttp



async def lookup_song(id: str, country_code: str = 'us') -> object:
	request = {'request': 'lookup_song', 'id': id, 'country_code': country_code}
	start_time = current_unix_time_ms()

	try:
		async with aiohttp.ClientSession() as session:
			api_url = f'{api}/tracks/{id}'
			api_params = {
				'market': country_code.upper(),
			}
			api_headers = {'Authorization': f'Bearer {await spotify_token.get_token()}'}
			timeout = aiohttp.ClientTimeout(total = 30)

			async with session.get(url = api_url, headers = api_headers, timeout = timeout, params = api_params) as response:
				if response.status == 200:
					song = await response.json()

					song_type = ('track' if song['album']['album_type'] != 'single' else 'single')
					song_url = song['external_urls']['spotify']
					song_id = song['id']
					song_title = song['name']
					song_artists = get_artists_of_media(request, song['artists'])
					song_is_explicit = song['explicit']
					
					collection_type = 'album' if song['album']['album_type'] != 'single' else 'ep'
					collection_url = song['album']['external_urls']['spotify']
					collection_id = song['album']['id']
					collection_title = remove_feat(song['album']['name'])
					collection_artists = get_artists_of_media(request, song['album']['artists'])
					collection_year = song['album']['release_date'][:4]

					media_cover = Cover(
						service = service,
						media_type = collection_type,
						title = collection_title,
						artists = collection_artists,
						hq_urls = song['album']['images'][0]['url'] if song['album']['images'] != [] else None,
						lq_urls = song['album']['images'][len(song['album']['images']) - 1]['url'] if song['album']['images'] != [] else None,
						meta = Meta(
							service = service,
							request = request,
							processing_time = 0,
							filter_confidence_percentage = 100.0,
							http_code = 200
						)
					)

					song_collection = Collection(
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
							processing_time = 0,
							filter_confidence_percentage = 100.0,
							http_code = 200
						)
					)

					return Song(
						service = service,
						type = song_type,
						urls = song_url,
						ids = song_id,
						title = song_title,
						artists = song_artists,
						collection = song_collection,
						is_explicit = song_is_explicit,
						cover = media_cover,
						meta = Meta(
							service = service,
							request = request,
							processing_time = current_unix_time_ms() - start_time,
							filter_confidence_percentage = 100.0,
							http_code = response.status
						)
					)

				else:
					error = Error(
						service = service,
						component = component,
						error_msg = "HTTP error when looking up song ID",
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