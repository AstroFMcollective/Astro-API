from ServiceCatalogAPI.components import *
from ServiceCatalogAPI.media_services.music.youtube_music.components.generic import *
from ServiceCatalogAPI.media_services.music.youtube_music.components.lookup.artist import lookup_artist
from ServiceCatalogAPI.media_services.music.youtube_music.components.generic import ytm



async def lookup_collection(id: str = None, browse_id: str = None, country_code: str = 'us') -> object:
	# Prepare the request dictionary with lookup details
	request = {'request': 'lookup_collection', 'id': id, 'country_code': country_code}
	# Record the start time for processing time calculation
	start_time = current_unix_time_ms()
	
	try:
		# If id is provided but browse_id is not, fetch browse_id and collection info
		if id is not None and browse_id is None:
			browse_id = ytm.get_album_browse_id(id)
			collection = ytm.get_album(browse_id)
		# If browse_id is provided, fetch collection info directly
		elif browse_id is not None:
			collection = ytm.get_album(browse_id)
		# If neither id nor browse_id is provided, return an error
		elif id is None and browse_id is None:
			return Error(
				service = service,
				component = component,
				error_msg = f'Neither collection id nor browse_id were given',
				meta = Meta(
					service = service,
					request = request,
					processing_time = current_unix_time_ms() - start_time,
					http_code = 500
				)
			)

		# Determine collection type (album or ep)
		collection_type = ('album' if collection['type'] == 'Album' else 'ep')
		collection_url = f'https://music.youtube.com/playlist?list={collection["audioPlaylistId"]}'
		collection_id = collection['audioPlaylistId']
		collection_title = collection['title']
		collection_year = collection['year']

		# Build a list of Artist objects for the collection's artists
		collection_artists = [
			Artist(
				service = service,
				ids = artist['id'],
				name = artist['name'],
				urls = f'https://music.youtube.com/channel/{artist["id"]}',
				meta = Meta(
					service = service,
					request = request,
					processing_time = current_unix_time_ms() - start_time,
					http_code = 200,
					filter_confidence_percentage = {service: 100.0}
				)
			) for artist in collection['artists']
		]

		# Create a Cover object for the collection
		collection_cover = Cover(
			service = service,
			media_type = 'collection',
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

		# Return a Collection object with all gathered information
		return Collection(
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
				filter_confidence_percentage = {service: 100.0},
				http_code = 200
			)
		)

	# If sinister things happen
	except Exception as msg:
		error = Error(
			service = service,
			component = component,
			error_msg = f'Error while looking up collection {id} on {component}: "{msg}"',
			meta = Meta(
				service = service,
				request = request,
				processing_time = current_unix_time_ms() - start_time,
				http_code = 500
			)
		)
		await log(error)
		return error