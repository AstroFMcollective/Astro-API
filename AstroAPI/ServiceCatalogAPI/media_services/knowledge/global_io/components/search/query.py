from AstroAPI.ServiceCatalogAPI.components import *
from AstroAPI.ServiceCatalogAPI.media_services.knowledge.global_io.components.generic import *
from AstroAPI.ServiceCatalogAPI.media_services.knowledge.global_io.components.generic import service as gservice, component as gcomponent

from AstroAPI.ServiceCatalogAPI.media_services.knowledge.global_io.components.search.song import search_song as search_song_knowledge

async def search_query(query: str, country_code: str = 'us', exclude_services: list = []) -> object:
	# Prepare the request dictionary with query details
	request = {'request': 'search_query', 'query': query, 'country_code': country_code}
	# Record the start time for processing time calculation
	start_time = current_unix_time_ms()

	try:
		# Define the types considered as 'knowledge'
		knowledge_types = ['knowledge']
		
		# Perform the search query using the genius module
		query_result = await genius.search_query(query, country_code)
		
		# If the result type is in knowledge_types, process as a song knowledge search
		if query_result.type in knowledge_types:
			obj = await search_song_knowledge(
				[artist.name for artist in query_result.artists],
				query_result.title,
				query_result.type,
				query_result.collection.title if query_result.collection is not None else None,
				query_result.is_explicit,
				country_code,
				[query_result],
				exclude_services
			)
		
			# Replace the request dict of the search one with the query one
			obj.meta.request = request
			obj.meta.regenerate_json()
			obj.regenerate_json()

			return obj
		
		else:
			empty_response = Empty(
				service = gservice,
				meta = Meta(
					service = gservice,
					request = request,
					processing_time = query_result.meta.processing_time,
					filter_confidence_percentage = query_result.meta.filter_confidence_percentage,
					http_code = 204
				)
			)
			await log(empty_response)
			return empty_response

	# If sinister things happen
	except Exception as msg:
		error = Error(
			service = gservice,
			component = gcomponent,
			error_msg = f'Error when doing general query knowledge search: "{msg}"',
			meta = Meta(
				service = gservice,
				request = request,
				processing_time = {gservice: current_unix_time_ms() - start_time},
				http_code = 500,
				filter_confidence_percentage = {gservice: 0.0}
			)
		)
		await log(error)
		return error