from AstroAPI.ServiceCatalogAPI.components import *
from AstroAPI.ServiceCatalogAPI.media_services.music.global_io.components.generic import *
from AstroAPI.ServiceCatalogAPI.media_services.music.global_io.components.generic import service as gservice, component as gcomponent

from AstroAPI.ServiceCatalogAPI.media_services.music.global_io.components.search.song import search_song as search_song_music
from AstroAPI.ServiceCatalogAPI.media_services.music.global_io.components.search.collection import search_collection as search_collection_music



async def lookup_collection(service: object, id: str, collection_country_code: str = None, lookup_country_code: str = 'us') -> object:
	# Prepare the request metadata
	request = {'request': 'lookup_collection', 'service': service.service, 'id': id, 'collection_country_code': collection_country_code, 'lookup_country_code': lookup_country_code}
	# Record the start time for processing time calculation
	start_time = current_unix_time_ms()

	try:
		# Look up the collection on its respectative service for its metadata
		collection_reference = await service.lookup_collection(id = id, country_code = collection_country_code)

		# If the collection ref is actually a song single, it'll use the metadata to look it up as a song, then return that data as a song
		if collection_reference.type == 'single':
			return await search_song_music(
				artists = [artist.name for artist in collection_reference.artists],
				title = collection_reference.title,
				song_type = collection_reference.type,
				collection = collection_reference.collection.title,
				is_explicit = collection_reference.is_explicit,
				country_code = lookup_country_code,
				include_premade_media = [collection_reference]
			) 

		# This would usually trigger had an error happened inside the lookup collection function, so we can just return that empty or error object
		if collection_reference.type != 'album' and collection_reference.type != 'ep':
			return collection_reference

		# Make the call to the Global Interface's collection-searching function
		collection = await search_collection_music(
			[artist.name for artist in collection_reference.artists],
			collection_reference.title,
			collection_reference.release_year,
			lookup_country_code,
			[collection_reference]
		)

		# Replace the request dict of the search one with the lookup one
		collection.meta.request = request
		collection.meta.regenerate_json()
		collection.regenerate_json()

		return collection

	# If sinister things happen
	except Exception as error:
		error = Error(
			service = gservice,
			component = gcomponent,
			error_msg = f'Error when searching collection: "{error}"',
			meta = Meta(
				service = gservice,
				request = request,
				http_code = 500,
				filter_confidence_percentage = {gservice: 0.0},
				processing_time = current_unix_time_ms() - start_time
			)
		)
		await log(error)
		return error