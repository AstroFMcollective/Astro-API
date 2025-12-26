from AstroAPI.ServiceCatalogAPI.components import *
from AstroAPI.InternalComponents.SystemMediaObjects import *
from AstroAPI.InternalComponents.Legacy import *
from AstroAPI.InternalComponents.CredentialsManager.media_services.genius.credentials import genius_credentials
from AstroAPI.ServiceCatalogAPI.media_services.knowledge.genius.components.generic import *
from AstroAPI.ServiceCatalogAPI.media_services.knowledge.genius.components.lookup.song import lookup_song as lookup_song_knowledge
import requests



async def search_query(query: str, country_code: str = 'us') -> object:
	# Prepare the request metadata
	request = {'request': 'search_query', 'query': query, 'country_code': country_code}
	# Record the start time for processing time calculation
	start_time = current_unix_time_ms()
	
	try:
		# Construct everything needed for the API call
		api_url = f'{api}/search'
		api_params = {
			'q': query
		}
		await genius_credentials.get_credentials()
		api_headers = {'Authorization': f'Bearer {genius_credentials.client_token}'}
		# For some reason Genius does not like the way aiohttp forms its headers so we stick to requests for HTTP
		# I am not a fan of this but you gotta get it working somehow, I'll figure out a workaround someday
		results = requests.get(api_url, api_params, headers = api_headers)

		if results.status_code == 200:
			results_json = results.json()['response'] # Parse the JSON response to get the search results
			# Extract the song ID from the first search result
			song_id = results_json['hits'][0]['result']['id']
			# Shove that sucker into a song knowledge lookup function
			song = await lookup_song_knowledge(id = song_id, country_code = country_code)
			# Record the processing time in the song's metadata
			song.meta.processing_time[service] = current_unix_time_ms() - start_time
			# Regenerate the song's JSON representation
			# P.S. If you haven't read the media.py file; ALWAYS DO THIS WHEN YOU'RE MODDING MEDIA OBJECT VALUES
			return song
		else:
			error = Error(
				service = service,
				component = component,
				error_msg = "HTTP error when searching query knowledge",
				meta = Meta(
					service = service,
					request = request,
					processing_time = {service: current_unix_time_ms() - start_time},
					http_code = results.status_code
				)
			)
			await log(error)
			return error
	
	# If sinister things happen
	except Exception as error:
		error = Error(
			service = service,
			component = component,
			error_msg = f'Error when searching query knowledge: "{error}"',
			meta = Meta(
				service = service,
				request = request,
				http_code = 500,
				processing_time = {service: current_unix_time_ms() - start_time}
			)
		)
		await log(error)
		return error