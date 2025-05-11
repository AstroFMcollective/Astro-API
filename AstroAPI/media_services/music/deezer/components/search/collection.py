from AstroAPI.components import *
from AstroAPI.media_services.music.deezer.components.generic import *

import aiohttp



async def search_collection(artists: list, title: str, year: int = None, country_code: str = 'us') -> object:
	request = {'request': 'search_collection', 'artists': artists, 'title': title, 'year': year, 'country_code': country_code}
	start_time = current_unix_time_ms()

	try:
		async with aiohttp.ClientSession() as session:
			artists = [optimize_for_search(artist) for artist in artists]
			title = clean_up_collection_title(optimize_for_search(title))
			
			collections = []
			api_url = f'{api}/search/album'
			api_params = {
				'q': f'artist:"{artists[0]}" album:"{title}"',
			}
			api_headers = {
				'Content-Type': 'application/json'
			}
			timeout = aiohttp.ClientTimeout(total = 30)

			async with session.get(url = api_url, headers = api_headers, timeout = timeout, params = api_params) as response:
				if response.status == 200:
					json_response = await response.json()

					for data in json_response['data']:
						async with session.get(url = f'{api}/album/{data['id']}', headers = api_headers) as result:
							collection = await result.json()

							collection_type = 'album' if collection['record_type'] != 'ep' else 'ep'
							collection_url = collection['link']
							collection_id = collection['id']
							collection_title = collection['title']
							collection_year = collection['release_date'][:4]
							collection_genre = collection['genres']['data'][0]['name']

							collection_artists = [
								Artist(
									service = service,
									urls = artist['link'],
									ids = artist['id'],
									name = artist['name'],
									profile_picture = ProfilePicture(
										service = service,
										user_type = 'artist',
										hq_urls = artist['picture_xl'],
										lq_urls = artist['picture_medium'],
										color_hex = None,
										meta = Meta(
											service = service,
											request = request,
											processing_time = current_unix_time_ms() - start_time,
											filter_confidence_percentage = {service: 100.0},
											http_code = response.status
										)
									),
									meta = Meta(
										service = service,
										request = request,
										processing_time = current_unix_time_ms() - start_time,
										filter_confidence_percentage = {service: 100.0},
										http_code = response.status
									)
								) for artist in collection['contributors']
							]

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