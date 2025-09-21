from AstroAPI.ServiceCatalogAPI.components import *
from AstroAPI.InternalComponents.CredentialsManager.media_services.spotify.token import spotify_token
from AstroAPI.ServiceCatalogAPI.media_services.music.spotify.components.generic import *
import aiohttp



async def search_collection(artists: list, title: str, year: int = None, country_code: str = 'us') -> object:
	# Prepare the request dictionary with search parameters
	request = {'request': 'search_collection', 'artists': artists, 'title': title, 'year': year, 'country_code': country_code}
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
			api_url = f'{api}/search'
			api_params = {
				'q': f'artist:{artists[0]} album:{title}',
				'type': 'album',
				'market': country_code.upper(),
				'limit': 50,
				'offset': 0
			}
			api_headers = {'Authorization': f'Bearer {await spotify_token.get_token()}'}
			timeout = aiohttp.ClientTimeout(total = 30) # Set a timeout for the HTTP request

			# Make an asynchronous GET request to the Spotify API
			async with session.get(url = api_url, headers = api_headers, timeout = timeout, params = api_params) as response:
				if response.status == 200:
					# Parse the JSON response
					json_response = await response.json()

					# Iterate over each collection (album) in the response
					for collection in json_response['albums']['items']:
						# Determine the collection type (album or ep)
						collection_type = ('album' if collection['album_type'] != 'single' else 'ep')
						collection_url = collection['external_urls']['spotify']
						collection_id = collection['id']
						collection_title = remove_feat(collection['name'])
						collection_artists = get_artists_of_media(request, collection['artists'])
						collection_year = collection['release_date'][:4]
			
						# Create a Cover object for the collection's artwork
						media_cover = Cover(
							service = service,
							media_type = collection_type,
							title = collection_title,
							artists = collection_artists,
							hq_urls = collection['images'][0]['url'] if collection['images'] != [] else None,
							lq_urls = collection['images'][len(collection['images']) - 1]['url'] if collection['images'] != [] else None,
							meta = Meta(
								service = service,
								request = request,
								processing_time = 0,
								filter_confidence_percentage = 100.0,
								http_code = 200
							)
						)    

						# Create a Collection object and add it to the list
						collections.append(Collection(
							service = service,
							type = collection_type,
							urls = collection_url,
							ids = collection_id,
							title = collection_title,
							artists = collection_artists,
							release_year = collection_year,
							cover = media_cover,
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