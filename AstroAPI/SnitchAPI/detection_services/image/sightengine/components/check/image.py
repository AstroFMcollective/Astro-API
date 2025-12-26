from AstroAPI.SnitchAPI.components import *
from AstroAPI.InternalComponents.SystemMediaObjects import *
from AstroAPI.InternalComponents.Legacy import *
from AstroAPI.InternalComponents.CredentialsManager.snitch_services.sightengine.credentials import sightengine_credentials
from AstroAPI.SnitchAPI.detection_services.image.sightengine.components.generic import *

import aiohttp



async def check_image(image_url: str) -> object:
	# Prepare the request dictionary with search parameters
	request = {'request': 'check_image', 'image_url': image_url}
	# Lookup JSON variable for later debugging
	lookup_json = None
	# Record the start time for processing time calculation
	start_time = current_unix_time_ms()

	try:
		async with aiohttp.ClientSession() as session:
			# Prepare request data and SightEngine API endpoint
			await sightengine_credentials.get_credentials()
			api_url = f'{api}'
			api_params = {
				'url': image_url,
				'models': 'genai',
				'api_user': sightengine_credentials.client_id,
				'api_secret': sightengine_credentials.client_secret
			}
			timeout = aiohttp.ClientTimeout(total = 30)
			
			async with session.get(url = api_url, timeout = timeout, params = api_params) as response:
				lookup_json = await response.json()
				if response.status == 200:
					return Analysis(
						service = service,
						media_type = 'image',
						ai_generated_confidence = lookup_json['type']['ai_generated'] * 100,
						meta = Meta(
							service = service,
							request = request,
							processing_time = current_unix_time_ms() - start_time,
							http_code = response.status
						)
					)
				else:
					error = Error(
						service = service,
						component = component,
						error_msg = f'HTTP Error when checking image for gen AI',
						meta = Meta(
							service = service,
							request = request,
							http_code = response.status,
							processing_time = {service: current_unix_time_ms() - start_time}
						)
					)
					await log(error, [discord.File(fp = StringIO(json.dumps(lookup_json, indent = 4)), filename = f'{image_url}.json')])


	except Exception as error:
		error = Error(
			service = service,
			component = component,
			error_msg = f'Error when checking image for gen AI: "{error}"',
			meta = Meta(
				service = service,
				request = request,
				http_code = 500,
				processing_time = {service: current_unix_time_ms() - start_time}
			)
		)
		await log(error, [discord.File(fp = StringIO(json.dumps(lookup_json, indent = 4)), filename = f'{image_url}.json')])
		return error