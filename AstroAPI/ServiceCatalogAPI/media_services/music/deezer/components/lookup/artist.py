from AstroAPI.ServiceCatalogAPI.components import *
from AstroAPI.InternalComponents.SystemMediaObjects import *
from AstroAPI.InternalComponents.Legacy import *
from AstroAPI.ServiceCatalogAPI.media_services.music.deezer.components.generic import *

import aiohttp



async def lookup_artist(id: str, country_code: str = 'us') -> object:
	# Prepare the request metadata
	request = {'request': 'lookup_artist', 'id': id, 'country_code': country_code}
	# Lookup JSON variable for later debugging
	lookup_json = None
	# Record the start time for processing time calculation
	start_time = current_unix_time_ms()
	
	try:
		async with aiohttp.ClientSession() as session:
			# Prepare for API call
			api_url = f'{api}/artist/{id}'
			api_headers = {
				'Content-Type': 'application/json'
			}
			timeout = aiohttp.ClientTimeout(total = 30)

			# Make an asynchronous GET request to the API
			async with session.get(url = api_url, headers = api_headers, timeout = timeout) as response:
				lookup_json = await response.json()
				if response.status == 200:
					# Parse the JSON response for the artist data
					artist = get_artists_of_media(request, [lookup_json])

					return artist
				
				else:
					error = Error(
						service = service,
						component = component,
						error_msg = "HTTP error when looking up artist ID",
						meta = Meta(
							service = service,
							request = request,
							processing_time = current_unix_time_ms() - start_time,
							http_code = response.status
						)
					)
					await log(error, [discord.File(fp = StringIO(json.dumps(lookup_json, indent = 4)), filename = f'{id}.json')])
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
		await log(error, [discord.File(fp = StringIO(json.dumps(lookup_json, indent = 4)), filename = f'{id}.json')])
		return error