from AstroAPI.InternalComponents.SystemMediaObjects import *
from AstroAPI.InternalComponents.Legacy import *
from AstroAPI.ServiceCatalogAPI.media_services.music.deezer.components.generic import *
from AstroAPI.ServiceCatalogAPI.components import *

import aiohttp



async def get_search_wrapper(media: str, query: str):

	"""
		Wrapper for Deezer API search endpoint https://developers.deezer.com/api/search
	"""

	request = {
		'q': query,
	}
	lookup_json = None
	start_time = current_unix_time_ms()
	
	try:
		async with aiohttp.ClientSession() as session:
			api_url = f'{api}/search/{media}'
			api_headers = {
				'Content-Type': 'application/json'
			}
			api_params = request
			timeout = aiohttp.ClientTimeout(total = 30) # Set a timeout for the HTTP request
			async with session.get(url = api_url, timeout = timeout, params = api_params) as response:
				lookup_json = await response.json()
				return lookup_json

	# Handle any exceptions that occur during the process
	except Exception as error:
		error = Error(
			service = service,
			component = component,
			error_msg = f'Error when doing generic GET request: "{error}"',
			meta = Meta(
				service = service,
				request = request,
				http_code = 500,
				processing_time = {service: current_unix_time_ms() - start_time}
			)
		)
		await log(error, [discord.File(fp = StringIO(json.dumps(lookup_json, indent = 4)), filename = f'{query}.json')])
		return error
