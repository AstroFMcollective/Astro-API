from AstroAPI.components import *
from AstroAPI.media_services.music.global_io.components.generic import *
from AstroAPI.media_services.music.global_io.components.generic import service as gservice, component as gcomponent

from AstroAPI.media_services.music.youtube_music.components.search.query import search_query as ytm_search_query

from AstroAPI.media_services.music.global_io.components.search.song import search_song
from AstroAPI.media_services.music.global_io.components.search.music_video import search_music_video
from AstroAPI.media_services.music.global_io.components.search.collection import search_collection



async def search_query(query: str, country_code: str = 'us', exclude_services: list = []) -> object:
	request = {'request': 'search_query', 'query': query, 'country_code': country_code}
	start_time = current_unix_time_ms()
	
	try:
		song_types = ['track', 'single']
		video_types = ['music_video']
		collection_types = ['album', 'ep']

		query_result = await ytm_search_query(query, country_code)

		if query_result.type in song_types:
			return await search_song(
				[artist.name for artist in query_result.artists],
				query_result.title,
				query_result.type,
				query_result.collection.title,
				query_result.is_explicit,
				country_code,
				[query_result],
				exclude_services
			)

		elif query_result.type in video_types:
			return await search_music_video(
				[artist.name for artist in query_result.artists],
				query_result.title,
				query_result.is_explicit,
				country_code,
				[query_result],
				exclude_services
			)
		
		elif query_result.type in collection_types:
			return await search_collection(
				[artist.name for artist in query_result.artists],
				query_result.title,
				query_result.release_year,
				country_code,
				[query_result],
				exclude_services
			)
		
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