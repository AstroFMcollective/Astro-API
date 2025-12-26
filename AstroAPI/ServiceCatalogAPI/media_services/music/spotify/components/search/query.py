from AstroAPI.InternalComponents.Legacy import *
from AstroAPI.ServiceCatalogAPI.components import *
from AstroAPI.InternalComponents.CredentialsManager.media_services.spotify.token import spotify_token
from AstroAPI.ServiceCatalogAPI.media_services.music.spotify.components.generic import *
import aiohttp



async def search_query(query: str, filter_for_best_match: bool = True, media_types: list = None, is_explicit: bool = None, country_code: str = 'us'):
	# Prepare the request dictionary with search parameters
	request = {'request': 'search_query', 'query': query, 'country_code': country_code}
	# Lookup JSON variable for later debugging
	lookup_json = None
	# Record the start time for processing time calculation
	start_time = current_unix_time_ms()
	
	try:
		async with aiohttp.ClientSession() as session:
			# Prepare for API call
			if media_types != None:
				query_media = 'track,album'
			else:
				spotified_types = []
				if 'song' in media_types:
					spotified_types.append('track')
				if 'collection' in media_types:
					spotified_types.append('album')
				query_media = ','.join(spotified_types)

			api_url = f'{api}/search'
			api_params = {
				'q': query,
				'type': query_media,
				'market': country_code.upper(),
				'limit': 50,
				'offset': 0
			}
			api_headers = {'Authorization': f'Bearer {await spotify_token.get_token()}'}
			timeout = aiohttp.ClientTimeout(total = 30) # Set a timeout for the HTTP request

			# Make an asynchronous GET request to the Spotify API
			async with session.get(url = api_url, headers = api_headers, timeout = timeout, params = api_params) as response:
				lookup_json = await response.json()
				if response.status == 200:
					songs = await create_song_objects(
						json_response = lookup_json,
						request = request,
						start_time = start_time,
						http_code = response.status
					)
					collections = await create_collection_objects(
						json_response = lookup_json,
						request = request,
						start_time = start_time,
						http_code = response.status
					)
					if filter_for_best_match == False:
						return Query(
							service = service,
							songs = songs,
							collections = collections,
							meta = Meta(
								service = service,
								request = request,
								processing_time = current_unix_time_ms() - start_time,
								filter_confidence_percentage = 0.0, # Because there was no filtering involved
								http_code = response.status
							)
						)
					
					else:
						items = []
						items.extend(songs)
						items.extend(collections)
						return await filter_query(service = service, query_request = request, items = items, query = query, query_is_explicit = is_explicit, query_country_code = country_code)
					
				else:
					# Handle HTTP errors from the Spotify API
					error = Error(
						service = service,
						component = component,
						error_msg = "HTTP error when searching via query",
						meta = Meta(
							service = service,
							request = request,
							processing_time = current_unix_time_ms() - start_time,
							http_code = response.status
						)
					)
					await log(error, [discord.File(fp = StringIO(json.dumps(lookup_json, indent = 4)), filename = f'{query}.json')])
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
		await log(error, [discord.File(fp = StringIO(json.dumps(lookup_json, indent = 4)), filename = f'{query}.json')])
		return error