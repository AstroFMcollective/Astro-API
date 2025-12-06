from AstroAPI.InternalComponents.Legacy import *
from AstroAPI.ServiceCatalogAPI.components.spotify import *
from AstroAPI.InternalComponents.CredentialsManager.media_services.spotify.token import spotify_token
from AstroAPI.ServiceCatalogAPI.media_services.music.spotify.components.generic import *
import aiohttp



async def search_query(query: str, filter_for_best_match: bool = True, country_code: str = 'us'):
	# Prepare the request dictionary with search parameters
	request = {'request': 'search_query', 'query': query, 'country_code': country_code}
	# Lookup JSON variable for later debugging
	lookup_json = None
	# Record the start time for processing time calculation
	start_time = current_unix_time_ms()
	
	try:
		async with aiohttp.ClientSession() as session:
			# Prepare for API call
			api_url = f'{api}/search'
			api_params = {
				'q': query,
				'type': 'track,album',
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
					json_response = await response.json()
					songs = await create_song_objects(
						json_response = json_response,
						request = request,
						start_time = start_time,
						http_code = response.status
					)
					collections = await create_collection_objects(
						json_response = json_response,
						request = request,
						start_time = start_time,
						http_code = response.status
					)
					if filter_for_best_match == False:
						return [songs, collections]
					
				else:
					print(f"error code {response.status}")
	except:
		pass