from AstroAPI.components import *
from AstroAPI.media_services.knowledge.global_io.components.generic import *
from AstroAPI.media_services.knowledge.global_io.components.generic import service as gservice, component as gcomponent

from AstroAPI.media_services.knowledge.global_io.components.search.song import search_song as search_song_knowledge



async def lookup_song(service: object, id: str, song_country_code: str = None, lookup_country_code: str = 'us') -> object:
	request = {'request': 'lookup_song', 'service': service.service, 'id': id, 'song_country_code': song_country_code, 'lookup_country_code': lookup_country_code}
	start_time = current_unix_time_ms()
	
	try:
		# Look up the song knowledge on its respectative service for its metadata
		knowledge_reference = await service.lookup_song(id = id, country_code = song_country_code)

		legal_results = ['knowledge', 'track', 'single']
		compatible_results = ['knowledge']

		# This would usually trigger had an error happened inside the lookup knowledge function, so we can just return that empty or error object 
		if knowledge_reference.type not in legal_results:
			return knowledge_reference

		# Make the call to the Global Interface's song-searching function
		song = await search_song_knowledge(
			artists = [artist.name for artist in knowledge_reference.artists],
			title = knowledge_reference.title,
			song_type = knowledge_reference.type if knowledge_reference.type != 'knowledge' else knowledge_reference.media_type,
			collection = knowledge_reference.collection.title,
			is_explicit = knowledge_reference.is_explicit,
			country_code = lookup_country_code,
			include_premade_media = [knowledge_reference] if knowledge_reference.type in compatible_results else [],
		)

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