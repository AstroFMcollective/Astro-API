from AstroAPI.ServiceCatalogAPI.components import *
from AstroAPI.InternalComponents.SystemMediaObjects import *
from AstroAPI.InternalComponents.Legacy import *
from AstroAPI.ServiceCatalogAPI.media_services.music.deezer.components.generic import *

import aiohttp



async def search_collection(artists: list, title: str, year: int = None, country_code: str = 'us') -> object:
	# Prepare the request dictionary with search parameters
	request = {'request': 'search_collection', 'artists': artists, 'title': title, 'year': year, 'country_code': country_code}
	# Lookup JSON variable for later debugging
	lookup_json = None
	collection_json = None
	# Record the start time for processing time calculation
	start_time = current_unix_time_ms()

	try:
		# Create an aiohttp session
		async with aiohttp.ClientSession() as session:
			# Optimize strings for query search
			artists = [optimize_for_search(artist) for artist in artists]
			title = clean_up_collection_title(optimize_for_search(title))
			
			collections = []
			# Prepare for API call
			api_url = f'{api}/search/album'
			api_params = {
				'q': f'artist:"{artists[0]}" album:"{title}"',
			}
			api_headers = {
				'Content-Type': 'application/json'
			}
			timeout = aiohttp.ClientTimeout(total = 30)	# Set a timeout for the HTTP request

			# Make an asynchronous GET request to the search endpoint
			async with session.get(url = api_url, headers = api_headers, timeout = timeout, params = api_params) as response:
				lookup_json = await response.json()
				if response.status == 200:
					# Parse the JSON response
					json_response = lookup_json

					# Iterate over each album found in the response data
					for data in json_response['data']:
						# Fetch detailed album information by album ID because the base results don't have much artist info needed for accurate filtering
						async with session.get(url = f'{api}/album/{data["id"]}', headers = api_headers) as result:
							# Parse the album details
							collection_json = await result.json()
							collection = collection_json

							# Determine the collection type (album or ep)
							collection_type = 'album' if collection['record_type'] != 'ep' else 'ep'
							collection_url = collection['link']
							collection_id = collection['id']
							collection_title = remove_feat(collection['title'])
							collection_year = collection['release_date'][:4]
							collection_genre = collection['genres']['data'][0]['name'] if collection['genres']['data'] != [] else None
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

							# Append the collection object to the collections list
							collections.append(Collection(
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
									http_code = response.status
								)
							))
					# Filter and return the collection based on the query
					return await filter_collection(service = service, query_request = request, collections = collections, query_artists = artists, query_title = title, query_year = year, query_country_code = country_code)
				
				else:
					error = Error(
						service = service,
						component = component,
						error_msg = "HTTP error when searching for collection",
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
		await log(error, [discord.File(fp = StringIO(json.dumps(lookup_json, indent = 4)), filename = f'{title}.json'), discord.File(fp = StringIO(json.dumps(collection_json, indent = 4)), filename = f'collection.json')])
		return error