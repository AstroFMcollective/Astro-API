from AstroAPI.InternalComponents.SystemMediaObjects import *
from AstroAPI.InternalComponents.Legacy import *
from AstroAPI.ServiceCatalogAPI.media_services.music.apple_music.components.generic import *
from AstroAPI.ServiceCatalogAPI.components import *

import aiohttp



async def search_music_video(artists: list, title: str, is_explicit: bool = None, country_code: str = 'us') -> object:
	# Prepare the request dictionary with search parameters
	request = {'request': 'search_music_video', 'artists': artists, 'title': title, 'is_explicit': is_explicit, 'country_code': country_code}
	# Lookup JSON variable for later debugging
	lookup_json = None
	# Record the start time for processing time calculation
	start_time = current_unix_time_ms()

	try:
		# Create an aiohttp session
		async with aiohttp.ClientSession() as session:
			# Optimize strings for query search
			artists = [optimize_for_search(artist) for artist in artists]
			title = optimize_for_search(transliterate_to_ascii(title).lower())
				
			videos = []
			# Prepare for API call
			api_url = f'{api}/search'
			api_params = {
				'term': f'{artists[0]} "{title}"',
				'entity': 'musicVideo',
				'limit': 200,
				'country': country_code.lower(),
				'explicit': 'Yes' if is_explicit else 'No'
			}
			timeout = aiohttp.ClientTimeout(total = 30)  # Set a timeout for the request

			# Make an asynchronous GET request to the API
			async with session.get(url = api_url, timeout = timeout, params = api_params) as response:
				lookup_json = await response.json(content_type = 'text/javascript')
				if response.status == 200:
					if 'results' in lookup_json:
						if len(lookup_json['results']) > 0:
							# Iterate through each song in the results
							videos = await create_music_video_objects(
								json_response = lookup_json,
								request = request,
								start_time = start_time,
								http_code = response.status
							)
							# Filter and return a music video
							return await filter_mv(service = service, query_request = request, videos = videos, query_artists = artists, query_title = title, query_is_explicit = is_explicit, query_country_code = country_code)

						else:
							empty = Empty(
								service = service,
								meta = Meta(
									service = service,
									request = request,
									processing_time = current_unix_time_ms() - start_time,
									filter_confidence_percentage = 0.0,
									http_code = response.status
								)
							)
							await log(empty)
							return empty

					else:
						error = Error(
							service = service,
							component = component,
							error_msg = "Error when checking for results",
							meta = Meta(
								service = service,
								request = request,
								processing_time = current_unix_time_ms() - start_time,
								filter_confidence_percentage = 0.0,
								http_code = response.status
							)
						)
						await log(error, [discord.File(fp = StringIO(json.dumps(lookup_json, indent = 4)), filename = f'{title}.json')])
						return error
							
				else:
					error = Error(
						service = service,
						component = component,
						error_msg = "HTTP error when searching for music video",
						meta = Meta(
							service = service,
							request = request,
							processing_time = current_unix_time_ms() - start_time,
							filter_confidence_percentage = 0.0,
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
				filter_confidence_percentage = 0.0,
				processing_time = {service: current_unix_time_ms() - start_time}
				
			)
		)
		await log(error, [discord.File(fp = StringIO(json.dumps(lookup_json, indent = 4)), filename = f'{title}.json')])
		return error