from AstroAPI.InternalComponents.Legacy import *
from AstroAPI.ServiceCatalogAPI.components import *
from AstroAPI.InternalComponents.CredentialsManager.media_services.spotify.token import spotify_token
from AstroAPI.ServiceCatalogAPI.media_services.music.spotify.components.generic import *
import aiohttp



async def search_collection(artists: list, title: str, year: int = None, country_code: str = 'us') -> object:
	# Prepare the request dictionary with search parameters
	request = {'request': 'search_collection', 'artists': artists, 'title': title, 'year': year, 'country_code': country_code}
	# Lookup JSON variable for later debugging
	lookup_json = None
	# Record the start time for processing time calculation
	start_time = current_unix_time_ms()

	try:
		# Create an aiohttp session
		async with aiohttp.ClientSession() as session:
			# Optimize strings for query search
			artists = [optimize_for_search(artist) for artist in artists]
			title = clean_up_collection_title(optimize_for_search(title))
			
			collections = []
			# Prepare for API call
			api_url = f'{api}/search'
			api_params = {
				'q': f'artist:{artists[0]} album:{title}',
				'type': 'album',
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
					# Parse the JSON response
					collections = await create_collection_objects(
						json_response = lookup_json,
						request = request,
						start_time = start_time,
						http_code = response.status
					)

					# Filter and return the collection based on the query
					return await filter_collection(service = service, query_request = request, collections = collections, query_artists = artists, query_title = title, query_year = year, query_country_code = country_code)

				else:
					error = Error(
						service = service,
						component = component,
						error_msg = "HTTP error when searching for collection",
						meta = Meta(
							service = service,
							request = request,
							processing_time = current_unix_time_ms() - start_time,
							http_code = response.status
						)
					)
					await log(error, [discord.File(fp = StringIO(json.dumps(lookup_json, indent = 4)), filename = f'{title}.json')])
					return error

	# If sinister things happen
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