from AstroAPI.components import *
from AstroAPI.components.ini import keys
from AstroAPI.media_services.knowledge.genius.components.generic import *
from AstroAPI.media_services.knowledge.genius.components.lookup.song_knowledge import lookup_song_knowledge
import requests



async def search_query_knowledge(query: str, country_code: str = 'us') -> object:
	request = {'request': 'search_query', 'query': query, 'country_code': country_code}
	start_time = current_unix_time_ms()
	
	try:
		api_url = f'{api}/search'
		api_params = {
			'q': query
		}
		api_headers = {'Authorization': f'Bearer {keys['genius']['token']}'}
		results = requests.get(api_url, api_params, headers = api_headers)

		if results.status_code == 200:
			results_json = results.json()['response']
			song_id = results_json['hits'][0]['result']['id']
			song = await lookup_song_knowledge(id = song_id, country_code = country_code)
			song.meta.processing_time[service] = current_unix_time_ms() - start_time
			song.regenerate_json()
			return song
		else:
			error = Error(
				service = service,
				component = component,
				error_msg = "HTTP error when looking up song knowledge",
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