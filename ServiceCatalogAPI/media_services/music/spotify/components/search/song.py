from ServiceCatalogAPI.components import *
from ServiceCatalogAPI.components.service_tokens.spotify.token import spotify_token
from ServiceCatalogAPI.media_services.music.spotify.components.generic import *
import aiohttp



async def search_song(artists: list, title: str, song_type: str = None, collection: str = None, is_explicit: bool = None, country_code: str = 'us') -> object:
	request = {'request': 'search_song', 'artists': artists, 'title': title, 'song_type': song_type, 'collection': collection, 'is_explicit': is_explicit, 'country_code': country_code}
	start_time = current_unix_time_ms()

	# Try to perform the song search operation
	try:
		# Create an aiohttp session for making HTTP requests
		async with aiohttp.ClientSession() as session:
			# Remove any special characters from artists and title thay may throw off the search
			artists = [optimize_for_search(artist) for artist in artists]
			title = optimize_for_search(title)
			# Clean up collection title from any suffixes if provided
			collection = clean_up_collection_title(optimize_for_search(collection)) if collection != None else None
				
			songs = []
			api_url = f'{api}/search'

			# Build search query parameters for Spotify API
			api_params = {
				'q': f'artist:{artists[0]} track:{title}' if collection == None or song_type == 'single' else f'artist:{artists[0]} track:{title} album:{collection}',
				'type': 'track',
				'market': country_code.upper(),
				'limit': 50,
				'offset': 0
			}
			# Set authorization header with Spotify token
			api_headers = {'Authorization': f'Bearer {await spotify_token.get_token()}'}
			# Set a timeout for the request
			timeout = aiohttp.ClientTimeout(total = 30)

			# Make the GET request to Spotify API
			async with session.get(url = api_url, headers = api_headers, timeout = timeout, params = api_params) as response:
				if response.status == 200:
					# Parse JSON response if request was successful
					json_response = await response.json()

					# Iterate through each song in the response
					for song in json_response['tracks']['items']:
						# Extract song details
						song_type = ('track' if song['album']['album_type'] != 'single' else 'single')
						song_url = song['external_urls']['spotify']
						song_id = song['id']
						song_title = song['name']
						song_artists = get_artists_of_media(request, song['artists'])
						song_is_explicit = song['explicit']
						
						# Extract collection details
						collection_type = 'album' if song['album']['album_type'] != 'single' else 'ep'
						collection_url = song['album']['external_urls']['spotify']
						collection_id = song['album']['id']
						collection_title = remove_feat(song['album']['name'])
						collection_artists = get_artists_of_media(request, song['album']['artists'])
						collection_year = song['album']['release_date'][:4]

						# Create Cover object for the collection
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

						# Create Collection object for the song's album/EP
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

						# Append the Song object to the songs list
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
					# Filter and return the best matching song
					return await filter_song(service = service, query_request = request, songs = songs, query_artists = artists, query_title = title, query_song_type = song_type, query_collection = collection, query_is_explicit = is_explicit, query_country_code = country_code)

				else:
					# Handle HTTP errors from the Spotify API
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

	# Handle any exceptions that occur during the process
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