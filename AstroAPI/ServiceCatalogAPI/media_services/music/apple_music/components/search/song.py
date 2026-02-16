from AstroAPI.InternalComponents.SystemMediaObjects import *
from AstroAPI.InternalComponents.Legacy import *
from AstroAPI.ServiceCatalogAPI.media_services.music.apple_music.components.generic import *
from AstroAPI.ServiceCatalogAPI.components import *

import aiohttp



async def search_song(artists: list, title: str, song_type: str = None, collection: str = None, is_explicit: bool = None, country_code: str = 'us') -> object:
	# Build the request dictionary with all input parameters
	request = {'request': 'search_song', 'artists': artists, 'title': title, 'song_type': song_type, 'collection': collection, 'is_explicit': is_explicit, 'country_code': country_code}
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
			collection = optimize_for_search(transliterate_to_ascii(clean_up_collection_title(collection)).lower()) if collection != None else None

			songs = []
			# Prepare for API call
			api_url = f'{api}/search'
			api_params = {
				'term': (f'{artists[0]} "{title}"' if collection == None or song_type == 'single' else f'{artists[0]} "{title}" {collection}'),
				'entity': 'song',
				'limit': 200,
				'country': country_code.lower(),
				'explicit': 'Yes' if is_explicit else 'No'
			}
			timeout = aiohttp.ClientTimeout(total = 30) # Set a timeout for the HTTP request

			# Send a GET request to the API endpoint
			async with session.get(url = api_url, timeout = timeout, params = api_params) as response:
				lookup_json = await response.json(content_type = 'text/javascript')
				if response.status == 200:
					if 'results' in lookup_json:
						if len(lookup_json['results']) > 0:
							# Iterate through each song in the results
							songs = await create_song_objects(
								json_response = lookup_json,
								request = request,
								start_time = start_time,
								http_code = response.status
							)
							# Filter and return the best matching song
							return await filter_song(service = service, query_request = request, songs = songs, query_artists = artists, query_title = title, query_song_type = song_type, query_collection = collection, query_is_explicit = is_explicit, query_country_code = country_code)

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
						error_msg = "HTTP error when searching for song",
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