from AstroAPI.InternalComponents.Legacy import *
from AstroAPI.ServiceCatalogAPI.components import *
from AstroAPI.ServiceCatalogAPI.media_services.music.youtube_music.components.generic import *



async def create_collection_objects(results: dict, request: dict, start_time: int, http_code: int):

	"""
		Iterate through YouTube Music's albums list in their JSON response and convert all of it into Collection objects.
		
		:param json_response: YouTube Music's JSON response.
		:param request: Request dict.
	"""

	collections = []

	# Iterate over each collection result
	for collection in results:
		if collection['resultType'] == 'album':
			# Determine if the collection is an album or EP
			collection_type = ('album' if collection['type'] == 'Album' else 'ep')
			collection_url = f'https://music.youtube.com/playlist?list={collection["playlistId"]}'
			collection_id = collection['playlistId']
			collection_title = collection['title']
			collection_year = collection['year']

			# Build a list of Artist objects for the collection
			collection_artists = [
				Artist(
					service = service,
					urls = f'https://music.youtube.com/channel/{artist["id"]}',
					ids = artist['id'],
					name = artist['name'],
					meta = Meta(
						service = service,
						request = request,
						processing_time = current_unix_time_ms() - start_time,
						http_code = 200,
						filter_confidence_percentage = 100.0
					)
				) for artist in collection['artists']]

			# Create a Cover object for the collection
			collection_cover = Cover(
				service = service,
				media_type = collection_type,
				title = collection_title,
				artists = collection_artists,
				hq_urls = collection['thumbnails'][0]['url'],
				lq_urls = collection['thumbnails'][len(collection['thumbnails'])-1]['url'],
				meta = Meta(
					service = service,
					request = request,
					processing_time = current_unix_time_ms() - start_time,
					http_code = 200
				)
			)

			# Append the Collection object to the collections list
			collections.append(Collection(
				service = service,
				type = collection_type,
				urls = collection_url,
				ids = collection_id,
				title = collection_title,
				artists = collection_artists,
				release_year = collection_year,
				cover = collection_cover,
				meta = Meta(
					service = service,
					request = request,
					processing_time = current_unix_time_ms() - start_time,
					http_code = 200
				)
			))
	
	return collections