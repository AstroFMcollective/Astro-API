from AstroAPI.InternalComponents.Legacy import *
from AstroAPI.ServiceCatalogAPI.components import *
from AstroAPI.ServiceCatalogAPI.media_services.music.apple_music.components.generic import *



async def create_collection_objects(json_response: dict, request: dict, start_time: int, http_code: int):
	collections = []

	# Iterate over each collection in the results
	for collection in json_response['results']:
		# Determine if the collection is an album or EP
		collection_type = ('album' if ' - EP' not in collection['collectionName'] else 'ep')
		collection_url = collection['collectionViewUrl']
		collection_id = collection['collectionId']
		collection_title = clean_up_collection_title(collection['collectionName'])
		collection_year = collection['releaseDate'][:4]
		collection_genre = collection['primaryGenreName'] if 'primaryGenreName' in collection else None

		# Build the list of artist objects for the collection
		# This is pretty scuffed due to the way the iTunes API handles artists
		# but it doesn't throw off filtering so it's okay
		collection_artists = [
			Artist(
				service = service,
				urls = collection['artistViewUrl'] if 'artistViewUrl' in collection else f'https://music.apple.com/{request['country_code']}/artist/{collection['artistId']}', # Additional edge case if artistViewUrl is missing... this API is so weird
				ids = collection['artistId'],
				name = artist,
				meta = Meta(
					service = service,
					request = request,
					processing_time = current_unix_time_ms() - start_time,
					filter_confidence_percentage = {service: 100.0},
					http_code = http_code
				)
			) for artist in split_artists(collection['artistName'])
		]

		# Create the cover object for the collection
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
				http_code = http_code
			)
		)

		# Append the constructed Collection object to the collections list
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