from AstroAPI.InternalComponents.Legacy import *
from AstroAPI.ServiceCatalogAPI.components.generic import *
from AstroAPI.ServiceCatalogAPI.components.spotify import *
from AstroAPI.InternalComponents.CredentialsManager.media_services.spotify.token import spotify_token
from AstroAPI.ServiceCatalogAPI.media_services.music.spotify.components.generic import *
import aiohttp



async def lookup_song(id: str, country_code: str = 'us') -> object:
	# Prepare the request dictionary with search parameters
	request = {'request': 'lookup_song', 'id': id, 'country_code': country_code}
	# Lookup JSON variable for later debugging
	lookup_json = None
	# Record the start time for processing time calculation
	start_time = current_unix_time_ms()

	# Try to perform the song lookup operation
	try:
		# Create an aiohttp session for making HTTP requests
		async with aiohttp.ClientSession() as session:
			# Prepare request data and Spotify API endpoint
			api_url = f'{api}/tracks/{id}'
			api_params = {
				'market': country_code.upper(),
			}
			api_headers = {'Authorization': f'Bearer {await spotify_token.get_token()}'}
			timeout = aiohttp.ClientTimeout(total = 30)

			# Make the GET request to the Spotify API
			async with session.get(url = api_url, headers = api_headers, timeout = timeout, params = api_params) as response:
				lookup_json = await response.json()
				if response.status == 200:
					# Parse the JSON response if the request was successful
					song = lookup_json

					# Extract song details
					song_type = ('track' if song['album']['album_type'] != 'single' else 'single') # Determine the song type (track or single)
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

					# Build the cover object for the collection
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

					# Build the collection object
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

					# Return the Song object with all extracted details
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
					# Handle non-OK HTTP responses by returning an Error object
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
					await log(error, [discord.File(fp = StringIO(json.dumps(lookup_json, indent = 4)), filename = f'{id}.json')])
					return error

	# Handle any exceptions that occur during the lookup process
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
		await log(error, [discord.File(fp = StringIO(json.dumps(lookup_json, indent = 4)), filename = f'{id}.json')])
		return error