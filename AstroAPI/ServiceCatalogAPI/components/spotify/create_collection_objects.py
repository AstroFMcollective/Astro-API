from AstroAPI.InternalComponents.Legacy import *
from AstroAPI.ServiceCatalogAPI.media_services.music.spotify.components.generic import *



async def create_collection_objects(json_response: dict, request: dict, start_time: int, http_code: int):

	"""
		Iterate through Spotify's albums list in their JSON response and convert all of it into Collection objects.
		
		:param json_response: Spotify's JSON response.
		:param request: Request dict.
	"""

	collections = []

	# Iterate through each song in the response
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
				http_code = http_code
			)
		))
	
	return collections