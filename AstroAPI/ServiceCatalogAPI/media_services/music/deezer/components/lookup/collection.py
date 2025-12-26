from AstroAPI.ServiceCatalogAPI.components import *
from AstroAPI.InternalComponents.SystemMediaObjects import *
from AstroAPI.InternalComponents.Legacy import *
from AstroAPI.ServiceCatalogAPI.media_services.music.deezer.components.generic import *

import aiohttp



async def lookup_collection(id: str, country_code: str = 'us') -> object:
	# Prepare the request dictionary with relevant information
	request = {'request': 'lookup_collection', 'id': id, 'country_code': country_code, 'url': f'https://www.deezer.com/album/{id}'}
	# Lookup JSON variable for later debugging
	lookup_json = None
	# Record the start time for processing time calculation
	start_time = current_unix_time_ms()
	
	try:
		# Create an aiohttp session
		async with aiohttp.ClientSession() as session:
			# Prepare for API call
			api_url = f'{api}/album/{id}'
			api_headers = {
				'Content-Type': 'application/json'
			}
			timeout = aiohttp.ClientTimeout(total = 30)

			# Make a GET request to the Deezer API
			async with session.get(url = api_url, headers = api_headers, timeout = timeout) as response:
				lookup_json = await response.json()
				if response.status == 200:
					# Parse the JSON response
					collection = lookup_json

					# Determine the collection type (album or ep)
					collection_type = ('album' if collection['record_type'] != 'ep' else 'ep')
					collection_url = collection['link']
					collection_id = collection['id']
					collection_title = remove_feat(collection['title'])
					collection_year = collection['release_date'][:4]
					collection_genre = collection['genres']['data'][0]['name']
					collection_artists = get_artists_of_media(request, collection['contributors'])

					# Create a Cover object for the collection
					collection_cover = Cover(
						service = service,
						media_type = collection_type,
						title = collection_title,
						artists = collection_artists,
						hq_urls = collection['cover_xl'],
						lq_urls = collection['cover_medium'],
						meta = Meta(
							service = service,
							request = request,
							processing_time = current_unix_time_ms() - start_time,
							filter_confidence_percentage = {service: 100.0},
							http_code = response.status
						)
					)

					# Return a Collection object with all relevant data
					return Collection(
						service = service,
						type = collection_type,
						urls = collection_url,
						ids = collection_id,
						title = collection_title,
						artists = collection_artists,
						release_year = collection_year,
						cover = collection_cover,
						genre = collection_genre,
						meta = Meta(
							service = service,
							request = request,
							processing_time = current_unix_time_ms() - start_time,
							filter_confidence_percentage = {service: 100.0},
							http_code = response.status
						)
					)
				
				else:
					error = Error(
						service = service,
						component = component,
						error_msg = "HTTP error when looking up collection ID",
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