from AstroAPI.InternalComponents.Legacy import *
from AstroAPI.SnitchAPI.components.media import Meta, Analysis
from AstroAPI.InternalComponents.CredentialsManager.snitch_services.submithub.credentials import submithub_credentials
from AstroAPI.SnitchAPI.detection_services.audio.submithub.components.generic import *

import aiohttp



async def check_audio(audio_url: str) -> object:
	# Prepare the request dictionary with search parameters
	request = {'request': 'check_audio', 'audio_url': audio_url}
	# Lookup JSON variable for later debugging
	lookup_json = None
	# Record the start time for processing time calculation
	start_time = current_unix_time_ms()

	try:
		async with aiohttp.ClientSession() as session:
			# Prepare request data and SubmitHub API endpoint
			await submithub_credentials.get_credentials()
			api_url = f'{api}/detect'
			api_headers = {
				'X-API-Key': submithub_credentials.client_key,
				'Content-Type': 'application/json',
			}
			api_payload = {
				'audioUrl': audio_url
			}
			timeout = aiohttp.ClientTimeout(total = 30)

			async with session.post(url = api_url, timeout = timeout, headers = api_headers, json = api_payload) as response:
				lookup_json = await response.json()
				if response.status == 200:
					return Analysis(
						service = service,
						media_type = 'audio',
						ai_generated_confidence = lookup_json['result']['probability_ai_generated'],
						meta = Meta(
							service = service,
							request = request,
							processing_time = current_unix_time_ms() - start_time,
							http_code = response.status
						)
					)
				else:
					# Handle non-OK HTTP responses by returning an Error object
					error = Error(
						service = service,
						component = component,
						error_msg = "HTTP error when checking audio for gen AI",
						meta = Meta(
							service = service,
							request = request,
							processing_time = current_unix_time_ms() - start_time,
							http_code = response.status 
						)
					)
					await log(error, [discord.File(fp = StringIO(json.dumps(lookup_json, indent = 4)), filename = f'{audio_url}.json')])
					return error



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
		await log(error, [discord.File(fp = StringIO(json.dumps(lookup_json, indent = 4)), filename = f'{audio_url}.json')])
		return error