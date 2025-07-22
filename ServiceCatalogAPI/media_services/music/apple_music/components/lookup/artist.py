from ServiceCatalogAPI.components import *
from ServiceCatalogAPI.media_services.music.apple_music.components.generic import *

import aiohttp



async def lookup_artist(id: str, country_code: str = 'us') -> object:
	# Prepare the request metadata
	request = {'request': 'lookup_artist', 'id': id, 'country_code': country_code}
	# Record the start time for processing time calculation
	start_time = current_unix_time_ms()

	try:
		# Create an aiohttp session
		async with aiohttp.ClientSession() as session:
			# Prepare for API call
			api_url = f'{api}/lookup'
			api_params = {
				'id': id,
				'country': country_code.lower()
			}
			timeout = aiohttp.ClientTimeout(total = 30) # Set a timeout for the HTTP request

			# Make the GET request to the API endpoint
			async with session.get(url = api_url, params = api_params, timeout = timeout) as response:
				# Check if the response status is OK
				if response.status == 200:
					# Parse the JSON response
					artist = await response.json(content_type = 'text/javascript')
					# Extract the first artist result
					artist = artist['results'][0]

					# Extract artist details from the response
					artist_url = artist['artistLinkUrl']
					artist_id = artist['artistId']
					artist_name = artist['artistName']
					artist_genre = artist['primaryGenreName'] if 'primaryGenreName' in artist else None

					# Return an Artist object with the extracted data and metadata
					return Artist(
						service = service,
						urls = artist_url,
						ids = artist_id,
						name = artist_name,
						genre = artist_genre,
						meta = Meta(
							service = service,
							request = request,
							processing_time = current_unix_time_ms() - start_time,
							filter_confidence_percentage = {service: 100.0},
							http_code = response.status
						)
					)

				else:
					# Handle non-200 HTTP responses by returning an Error object
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