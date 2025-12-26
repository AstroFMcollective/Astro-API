from AstroAPI.ServiceCatalogAPI.components import *
from AstroAPI.InternalComponents.SystemMediaObjects import *
from AstroAPI.InternalComponents.Legacy import *
from AstroAPI.ServiceCatalogAPI.media_services.knowledge.global_io.components.generic import *
from AstroAPI.ServiceCatalogAPI.media_services.knowledge.global_io.components.generic import service as gservice, component as gcomponent

from AstroAPI.ServiceCatalogAPI.media_services.knowledge.global_io.components.search.song import search_song as search_song_knowledge



async def lookup_song(service: object, id: str, song_country_code: str = None, lookup_country_code: str = 'us') -> object:
	# Build the request dictionary with all relevant parameters
	request = {'request': 'lookup_song', 'service': service.service, 'id': id, 'song_country_code': song_country_code, 'lookup_country_code': lookup_country_code}
	# Record the start time for processing time calculation
	start_time = current_unix_time_ms()
	
	try:
		# Look up the song knowledge on its respective service for its metadata
		knowledge_reference = await service.lookup_song(id = id, country_code = song_country_code)

		# Define which result types are considered legal and compatible
		legal_results = ['knowledge', 'track', 'single'] # Result types that are legal to use for metadata
		compatible_results = ['knowledge'] # Result types that are compatible to use as premade media

		# If the lookup result type is not legal, return the reference as is (could be error or empty)
		if knowledge_reference.type not in legal_results:
			return knowledge_reference


		# Rudimentary check to see if the knowledge object reference has a collection
		# Certain service API-s do not provide a collection for objects, and music videos (which have compatible metadata) do not have a collection in any case
		if 'collection' in knowledge_reference.json:
			if knowledge_reference.collection is not None:
				knowledge_reference_collection_title = knowledge_reference.collection.title
			else: 
				knowledge_reference_collection_title = None
		else:
			knowledge_reference_collection_title = None

		# Call the global song search function with extracted metadata and include the knowledge reference if compatible
		song = await search_song_knowledge(
			artists = [artist.name for artist in knowledge_reference.artists],
			title = knowledge_reference.title,
			song_type = knowledge_reference.type if knowledge_reference.type != 'knowledge' else knowledge_reference.media_type,
			collection = knowledge_reference_collection_title,
			is_explicit = knowledge_reference.is_explicit,
			country_code = lookup_country_code,
			include_premade_media = [knowledge_reference] if knowledge_reference.type in compatible_results else [],
		)

		# Replace the request dict of the search one with the lookup one
		song.meta.request = request
		song.meta.regenerate_json()
		song.regenerate_json()

		return song

	# If sinister things happen
	except Exception as error:
		error = Error(
			service = gservice,
			component = gcomponent,
			error_msg = f'Error when searching song knowledge: "{error}"',
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