from AstroAPI.InternalComponents.Legacy import *
from AstroAPI.ServiceCatalogAPI.components import *
from AstroAPI.ServiceCatalogAPI.media_services.music.deezer.components.generic import *



async def create_collection_objects(json_response: dict, request: dict, start_time: int, http_code: int):

	"""
		Iterate through Deezer's albums list in their JSON response and convert all of it into Collection objects.
		
		:param json_response: Deezer's JSON response.
		:param request: Request dict.
	"""

	collections = []

	# Iterate through each song in the response
	for data in json_response['data']:
		async with aiohttp.ClientSession() as session:
			api_headers = {
				'Content-Type': 'application/json'
			}
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
						http_code = http_code
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
						http_code = http_code
					)
				))
	
	return collections