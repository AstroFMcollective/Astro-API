from AstroAPI.components import *
from AstroAPI.media_services.music.spotify.components.generic import *
from AstroAPI.media_services.music.spotify.components.generic.get_token import spotify_token
import aiohttp



async def search_song(artists: list, title: str, song_type: str = None, collection: str = None, is_explicit: bool = None, country_code: str = 'us') -> object:
	request = {'request': 'search_song', 'artists': artists, 'title': title, 'song_type': song_type, 'collection': collection, 'is_explicit': is_explicit, 'country_code': country_code}
	start_time = current_unix_time_ms()
	try:
		async with aiohttp.ClientSession() as session:
			artists = [optimize_for_search(artist) for artist in artists]
			title = optimize_for_search(title)
			collection = clean_up_collection_title(optimize_for_search(collection)) if collection != None else None
				
			songs = []
			api_url = f'{api}/search'
			api_params = {
				'q': f'artist:{artists[0]} track:{title}' if collection == None or song_type == 'single' else f'artist:{artists[0]} track:{title} album:{collection}',
				'type': 'track',
				'market': country_code.upper(),
				'limit': 50,
				'offset': 0
			}
			api_headers = {'Authorization': f'Bearer {await spotify_token.get_token()}'}
			timeout = aiohttp.ClientTimeout(total = 30)

			async with session.get(url = api_url, headers = api_headers, timeout = timeout, params = api_params) as response:
				if response.status == 200:
					json_response = await response.json()

					for song in json_response['tracks']['items']:
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

						songs.append(Song(
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