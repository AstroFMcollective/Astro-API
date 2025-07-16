from ServiceCatalogAPI.components import *
from ServiceCatalogAPI.media_services.music.apple_music.components.generic import *

import aiohttp



async def search_collection(artists: list, title: str, year: int = None, country_code: str = 'us') -> object:
	request = {'request': 'search_collection', 'artists': artists, 'title': title, 'year': year, 'country_code': country_code}
	start_time = current_unix_time_ms()
	
	try:
		async with aiohttp.ClientSession() as session:
			artists = [optimize_for_search(artist) for artist in artists]
			title = clean_up_collection_title(optimize_for_search(replace_with_ascii(title)))
				
			collections = []
			api_url = f'{api}/search'
			api_params = {
				'term': f'{artists[0]} "{title}"',
				'entity': 'album',
				'limit': 200,
				'country': country_code.lower()
			}

			timeout = aiohttp.ClientTimeout(total = 30)

			async with session.get(url = api_url, timeout = timeout, params = api_params) as response:
				if response.status == 200:
					json_response = await response.json(content_type = 'text/javascript')

					for collection in json_response['results']:
						collection_type = ('album' if ' - EP' not in collection['collectionName'] else 'ep')
						collection_url = collection['collectionViewUrl']
						collection_id = collection['collectionId']
						collection_title = clean_up_collection_title(collection['collectionName'])
						collection_year = collection['releaseDate'][:4]
						collection_genre = collection['primaryGenreName'] if 'primaryGenreName' in collection else None

						collection_artists = [
							Artist(
								service = service,
								urls = collection['artistViewUrl'],
								ids = collection['artistId'],
								name = artist,
								meta = Meta(
									service = service,
									request = request,
									processing_time = current_unix_time_ms() - start_time,
									filter_confidence_percentage = {service: 100.0},
									http_code = response.status
								)
							) for artist in split_artists(collection['artistName'])
						]

						collection_cover = Cover(
							service = service,
							media_type = collection_type,
							title = collection_title,
							artists = collection_artists,
							hq_urls = collection['artworkUrl100'],
							lq_urls = collection['artworkUrl60'],
							meta = Meta(
								service = service,
								request = request,
								processing_time = current_unix_time_ms() - start_time,
								filter_confidence_percentage = {service: 100.0},
								http_code = response.status
							)
						)

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
					return await filter_collection(service = service, query_request = request, collections = collections, query_artists = artists, query_title = title, query_year = year, query_country_code = country_code)
					
				else:
					error = Error(
						service = service,
						component = component,
						http_code = response.status,
						error_msg = "HTTP error when searching for collection",
						meta = Meta(
							service = service,
							request = request,
							processing_time = current_unix_time_ms() - start_time,
							filter_confidence_percentage = {service: 0.0},
							http_code = response.status
						)
					)
					await log(error)
					return error
				
	except Exception as error:
		error = Error(
			service = service,
			component = component,
			error_msg = f'Error when looking up collection: "{error}"',
			meta = Meta(
				service = service,
				request = request,
				http_code = 500,
				filter_confidence_percentage = {service: 0.0},
				processing_time = {service: current_unix_time_ms() - start_time}
			)
		)
		await log(error)
		return error