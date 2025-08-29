from AstroAPI.ServiceCatalogAPI.components import *
from AstroAPI.ServiceCatalogAPI.media_services.music.global_io.components.generic import *
from AstroAPI.ServiceCatalogAPI.media_services.music.global_io.components.generic import service as gservice, component as gcomponent

from AstroAPI.ServiceCatalogAPI.media_services.music.youtube_music.components.search.query import search_query as ytm_search_query

from AstroAPI.ServiceCatalogAPI.media_services.music.global_io.components.search.song import search_song as search_song_music
from AstroAPI.ServiceCatalogAPI.media_services.music.global_io.components.search.music_video import search_music_video as search_music_video_music
from AstroAPI.ServiceCatalogAPI.media_services.music.global_io.components.search.collection import search_collection as search_collection_music



async def search_query(query: str, country_code: str = 'us', exclude_services: list = []) -> object:
	# Prepare the request metadata
	request = {'request': 'search_query', 'query': query, 'country_code': country_code}
	# Record the start time for processing time calculation
	start_time = current_unix_time_ms()	

	try:
		song_types = ['track', 'single']
		video_types = ['music_video']
		collection_types = ['album', 'ep']

		query_result = await ytm_search_query(query, country_code)

		if query_result.type in song_types:
			obj = await search_song_music(
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

		elif query_result.type in video_types:
			obj = await search_music_video_music(
				[artist.name for artist in query_result.artists],
				query_result.title,
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
		
		elif query_result.type in collection_types:
			obj = await search_collection_music(
				[artist.name for artist in query_result.artists],
				query_result.title,
				query_result.release_year,
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


	except Exception as error:
		error = Error(
			service = gservice,
			component = gcomponent,
			error_msg = f'Error when searching for collection: "{error}"',
			meta = Meta(
				service = gservice,
				request = request,
				processing_time = {service: current_unix_time_ms() - start_time},
				filter_confidence_percentage = {gservice: 0.0},
				http_code = 500
			)
		)
		await log(error)
		return error