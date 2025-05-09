from AstroAPI.components import *
from AstroAPI.media_services.music.apple_music.components.generic import *
from AstroAPI.media_services.music.apple_music.components.lookup.artist import lookup_artist

import aiohttp



async def lookup_collection(id: str, country_code: str = 'us') -> object:
	request = {'request': 'lookup_collection', 'id': id, 'country_code': country_code}
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
					collection = await response.json(content_type = 'text/javascript')
					collection = collection['results'][0]

					if ' - Single' not in collection['collectionName']:
						collection_type = ('album' if ' - EP' not in collection['collectionName'] else 'ep')
						collection_url = collection['collectionViewUrl']
						collection_id = collection['collectionId']
						collection_title = clean_up_collection_title(collection['collectionName'])
						collection_artists = await lookup_artist(id = collection['artistId'], country_code = country_code)
						collection_artists = [collection_artists]
						collection_year = collection['releaseDate'][:4]
						collection_genre = collection['primaryGenreName'] if 'primaryGenreName' in collection else None

						collection_cover = Cover(
							service = service,
							media_type = collection_type,
							title = collection_title,
							artists = collection_artists,
							hq_urls = collection['artworkUrl100'],
							lq_urls = collection['artworkUrl60'],
							color_hex = None,
							meta = Meta(
								service = service,
								request = request,
								processing_time = current_unix_time_ms() - start_time,
								filter_confidence_percentage = {service: 100.0},
								http_code = response.status
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
							cover = collection_cover,
							genre = collection_genre,
							meta = Meta(
								service = service,
								request = request,
								processing_time = current_unix_time_ms() - start_time,
								filter_confidence_percentage = {service: 100.0},
								http_code = response.status
							)
						)

					else:
						song_type = 'single'
						song_url = collection['collectionViewUrl']
						song_id = collection['collectionId']
						song_title = clean_up_collection_title(collection['collectionName'])
						song_artists = await lookup_artist(id = collection['artistId'], country_code = country_code)
						song_artists = [song_artists]
						song_is_explicit = not 'not' in collection['collectionExplicitness']
						song_genre = collection['primaryGenreName'] if 'primaryGenreName' in collection else None
						song_cover = Cover(
							service = service,
							media_type = song_type,
							title = song_title,
							artists = song_artists,
							hq_urls = collection['artworkUrl100'],
							lq_urls = collection['artworkUrl60'],
							color_hex = None,
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
							type = song_type,
							urls = song_url,
							ids = song_id,
							title = collection_title,
							artists = collection_artists,
							cover = song_cover,
							release_year = collection['releaseDate'][:4],
							genre = song_genre,
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
							genre = song_genre,
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