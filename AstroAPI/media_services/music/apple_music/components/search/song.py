from AstroAPI.components import *
from AstroAPI.media_services.music.apple_music.components.generic import *

import aiohttp



async def search_song(artists: list, title: str, song_type: str = None, collection: str = None, is_explicit: bool = None, country_code: str = 'us') -> object:
	request = {'request': 'search_song', 'artists': artists, 'title': title, 'song_type': song_type, 'collection': collection, 'is_explicit': is_explicit, 'country_code': country_code}
	start_time = current_unix_time_ms()

	try:
		async with aiohttp.ClientSession() as session:
			artists = [optimize_for_search(artist) for artist in artists]
			title = optimize_for_search(replace_with_ascii(title).lower())
			collection = clean_up_collection_title(optimize_for_search(collection)) if collection != None else None

			songs = []
			api_url = f'{api}/search'
			api_params = {
				'term': (f'{artists[0]} "{title}"' if collection == None or song_type == 'single' else f'{artists[0]} "{title}" {collection}'),
				'entity': 'song',
				'limit': 200,
				'country': country_code.lower()
			}
			timeout = aiohttp.ClientTimeout(total = 30)

			async with session.get(url = api_url, timeout = timeout, params = api_params) as response:
				if response.status == 200:
					json_response = await response.json(content_type = 'text/javascript')

					for song in json_response['results']:
						song_type = 'track' if ' - Single' not in song['collectionName'] else 'single'
						song_url = song['trackViewUrl']
						song_id = song['trackId']
						song_title = song['trackName']
						song_is_explicit = not 'not' in song['trackExplicitness']
						song_genre = song['primaryGenreName'] if 'primaryGenreName' in song else None

						song_artists = [
							Artist(
								service = service,
								urls = song['artistViewUrl'],
								ids = song['artistId'],
								name = artist,
								meta = Meta(
									service = service,
									request = request,
									processing_time = current_unix_time_ms() - start_time,
									filter_confidence_percentage = 100.0,
									http_code = response.status
								)
							) for artist in split_artists(song['artistName'])
						]

						song_cover = Cover(
							service = service,
							media_type = song_type,
							title = song_title,
							artists = song_artists,
							hq_urls = song['artworkUrl100'],
							lq_urls = song['artworkUrl60'],
							meta = Meta(
								service = service,
								request = request,
								processing_time = current_unix_time_ms() - start_time,
								filter_confidence_percentage = 100.0,
								http_code = response.status
							)
						)

						song_collection = Collection(
							service = service,
							type = 'album' if ' - EP' not in song['collectionName'] else 'ep' if song_type != 'single' else song_type,
							urls = song['collectionViewUrl'],
							ids = song['collectionId'],
							title = clean_up_collection_title(song['collectionName']),
							artists = song_artists,
							cover = song_cover,
							meta = Meta(
								service = service,
								request = request,
								processing_time = current_unix_time_ms() - start_time,
								filter_confidence_percentage = 100.0,
								http_code = response.status
							)
						)

						songs.append(Song(
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
								http_code = response.status
							)
						))
					return await filter_song(service = service, query_request = request, songs = songs, query_artists = artists, query_title = title, query_song_type = song_type, query_collection = collection, query_is_explicit = is_explicit, query_country_code = country_code)

				else:
					error = Error(
						service = service,
						component = component,
						error_msg = "HTTP error when searching for song",
						meta = Meta(
							service = service,
							request = request,
							processing_time = current_unix_time_ms() - start_time,
							filter_confidence_percentage = 0.0,
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
				filter_confidence_percentage = 0.0,
				processing_time = {service: current_unix_time_ms() - start_time}
			)
		)
		await log(error)
		return error