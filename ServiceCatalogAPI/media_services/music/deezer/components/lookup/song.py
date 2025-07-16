from ServiceCatalogAPI.components import *
from ServiceCatalogAPI.media_services.music.deezer.components.generic import *

import aiohttp



async def lookup_song(id: str, country_code: str = 'us') -> object:
	request = {'request': 'lookup_song', 'id': id, 'country_code': country_code}
	start_time = current_unix_time_ms()
	
	try:
		async with aiohttp.ClientSession() as session:
			api_url = f'{api}/track/{id}'
			api_headers = {
				'Content-Type': 'application/json'
			}
			timeout = aiohttp.ClientTimeout(total = 30)

			async with session.get(url = api_url, headers = api_headers, timeout = timeout) as response:
				if response.status == 200:
					song = await response.json()

					song_type = 'track'
					song_url = song['link']
					song_id = song['id']
					song_title = song['title']
					song_is_explicit = song['explicit_lyrics']
					song_artists = get_artists_of_media(request, song['contributors'])

					song_cover = Cover(
						service = service,
						media_type = song_type,
						title = song_title,
						artists = song_artists,
						hq_urls = song['album']['cover_xl'],
						lq_urls = song['album']['cover_medium'],
						meta = Meta(
							service = service,
							request = request,
							processing_time = current_unix_time_ms() - start_time,
							filter_confidence_percentage = {service: 100.0},
							http_code = response.status
						)
					)

					song_collection = Collection(
						service = service,
						type = 'album' if song['album']['type'] != 'ep' else 'ep',
						urls = song['album']['link'],
						ids = song['album']['id'],
						title = remove_feat(song['album']['title']),
						artists = [song_artists[0]],
						release_year = song['album']['release_date'][:4],
						cover = song_cover,
						meta = Meta(
							service = service,
							request = request,
							processing_time = current_unix_time_ms() - start_time,
							filter_confidence_percentage = {service: 100.0},
							http_code = response.status
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
						cover = song_cover,
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