from AstroAPI.ServiceCatalogAPI.components import *
from AstroAPI.InternalComponents.SystemMediaObjects import *
from AstroAPI.InternalComponents.Legacy import *
from AstroAPI.ServiceCatalogAPI.media_services.music.deezer.components.generic import *

import aiohttp



async def search_song(artists: list, title: str, song_type: str = None, collection: str = None, is_explicit: bool = None, country_code: str = 'us', advanced_data_lookup: bool = False) -> object:
	# Prepare the request dictionary with all input parameters
	request = {'request': 'search_song', 'artists': artists, 'title': title, 'song_type': song_type, 'collection': collection, 'is_explicit': is_explicit, 'country_code': country_code}
	# Lookup JSON variable for later debugging
	lookup_json = None
	# Record the start time for processing time calculation
	start_time = current_unix_time_ms()

	try:
		# Create an aiottp session
		async with aiohttp.ClientSession() as session:
			# Optimize strings for query search
			artists = [optimize_for_search(artist) for artist in artists]
			title = optimize_for_search(title)
			collection = clean_up_collection_title(optimize_for_search(collection)) if collection != None else None
			
			songs = []
			# Prepare for API call
			api_url = f'{api}/search/track'
			api_params = {
				'q': f'artist:"{artists[0]}" track:"{title}"',
			}
			api_headers = {
				'Content-Type': 'application/json'
			}
			timeout = aiohttp.ClientTimeout(total = 30)	# Set a timeout for the HTTP request

			# Make the GET request to the Deezer search API
			async with session.get(url = api_url, headers = api_headers, timeout = timeout, params = api_params) as response:
				lookup_json = await response.json()
				if response.status == 200:

					# Iterate over each track in the response data
					songs = await create_song_objects(
						json_response = lookup_json,
						request = request,
						start_time = start_time,
						http_code = response.status,
						advanced_data_lookup = advanced_data_lookup
					)

					# Filter and return the best matching song
					return await filter_song(service = service, query_request = request, songs = songs, query_artists = artists, query_title = title, query_song_type = song_type, query_collection = collection, query_is_explicit = is_explicit, query_country_code = country_code)
				
				else:
					error = Error(
						service = service,
						component = component,
						error_msg = "HTTP error when searching for song",
						meta = Meta(
							service = service,
							request = request,
							processing_time = current_unix_time_ms() - start_time,
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
				processing_time = {service: current_unix_time_ms() - start_time}
			)
		)
		await log(error, [discord.File(fp = StringIO(json.dumps(lookup_json, indent = 4)), filename = f'{title}.json'), discord.File(fp = StringIO(json.dumps(song_json, indent = 4)), filename = f'song.json')])
		return error