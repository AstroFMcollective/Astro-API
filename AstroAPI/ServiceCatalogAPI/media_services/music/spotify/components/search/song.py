from AstroAPI.InternalComponents.Legacy import *
from AstroAPI.ServiceCatalogAPI.components.generic import *
from AstroAPI.ServiceCatalogAPI.components.spotify import *
from AstroAPI.InternalComponents.CredentialsManager.media_services.spotify.token import spotify_token
from AstroAPI.ServiceCatalogAPI.media_services.music.spotify.components.generic import *
import aiohttp



async def search_song(artists: list, title: str, song_type: str = None, collection: str = None, is_explicit: bool = None, country_code: str = 'us') -> object:
	# Prepare the request dictionary with search parameters
	request = {'request': 'search_song', 'artists': artists, 'title': title, 'song_type': song_type, 'collection': collection, 'is_explicit': is_explicit, 'country_code': country_code}
	# Lookup JSON variable for later debugging
	lookup_json = None
	# Record the start time for processing time calculation
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
				lookup_json = await response.json()
				if response.status == 200:
					songs = await create_song_objects(
						json_response = lookup_json,
						request = request,
						start_time = start_time,
						http_code = response.status
					)
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
					await log(error, [discord.File(fp = StringIO(json.dumps(lookup_json, indent = 4)), filename = f'{title}.json')])
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
		await log(error, [discord.File(fp = StringIO(json.dumps(lookup_json, indent = 4)), filename = f'{title}.json')])
		return error