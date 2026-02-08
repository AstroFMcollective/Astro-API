from AstroAPI.ServiceCatalogAPI.components import *
from AstroAPI.InternalComponents.SystemMediaObjects import *
from AstroAPI.InternalComponents.Legacy import *
from AstroAPI.ServiceCatalogAPI.media_services.music.global_io.components.generic import *
from AstroAPI.ServiceCatalogAPI.media_services.music.global_io.components.generic import service as gservice, component as gcomponent

# Import search queries from all services
from AstroAPI.ServiceCatalogAPI.media_services.music.spotify.components.search.query import search_query as search_spotify
from AstroAPI.ServiceCatalogAPI.media_services.music.apple_music.components.search.query import search_query as search_apple
from AstroAPI.ServiceCatalogAPI.media_services.music.youtube_music.components.search.query import search_query as search_ytm
from AstroAPI.ServiceCatalogAPI.media_services.music.deezer.components.search.query import search_query as search_deezer

# Import the content matching function
from AstroAPI.ServiceCatalogAPI.media_services.music.global_io.components.generic.match import match_content
from AstroAPI.ServiceCatalogAPI.components.filtering.filter import filter_query

from asyncio import create_task, gather



async def search_query(query: str, filter_for_best_match: bool = True, media_types: list = None, is_explicit: bool = None, country_code: str = 'us', exclude_services: list = []) -> object:
	# Prepare the request metadata
	request = {'request': 'search_query', 'query': query, 'country_code': country_code}
	start_time = current_unix_time_ms()

	try:
		# Define tasks for all services, checking exclude_services
		# We pass False for filtering because we want raw lists to aggregate ourselves
		tasks = []
		
		if 'spotify' not in exclude_services:
			tasks.append(create_task(search_spotify(query, False, media_types, is_explicit, country_code)))
		
		if 'apple_music' not in exclude_services:
			tasks.append(create_task(search_apple(query, False, media_types, is_explicit, country_code)))
			
		if 'youtube_music' not in exclude_services:
			tasks.append(create_task(search_ytm(query, False, media_types, is_explicit, country_code)))
			
		if 'deezer' not in exclude_services:
			tasks.append(create_task(search_deezer(query, False, media_types, is_explicit, country_code)))

		# Execute searches in parallel
		results = await gather(*tasks, return_exceptions=True)

		# Containers for raw objects from all services
		raw_songs = []
		raw_videos = []
		raw_collections = []

		# Process results from each service
		for result in results:
			if isinstance(result, Query):
				if result.songs:
					raw_songs.append(result.songs)
				if result.music_videos:
					raw_videos.append(result.music_videos)
				if result.collections:
					raw_collections.append(result.collections)
			elif isinstance(result, Error):
				# Log error but continue with other services
				await log(result)
			elif isinstance(result, Exception):
				# Handle unexpected crashes in tasks
				await log(Error(service=gservice, error_msg=f"Task failed: {result}", meta=Meta(service=gservice, request=request, processing_time=0, http_code=500)))

		# Content Matching: Merge raw lists into Global objects
		global_songs = []
		global_videos = []
		global_collections = []

		if raw_songs:
			global_songs = await match_content(request, raw_songs)
		
		if raw_videos:
			global_videos = await match_content(request, raw_videos)
			
		if raw_collections:
			global_collections = await match_content(request, raw_collections)

		# Calculate total processing time
		total_time = current_unix_time_ms() - start_time

		# Add Global IO processing time to the metadata of all results
		for item in global_songs + global_videos + global_collections:
			item.meta.processing_time[gservice] = total_time

		# Return Logic
		if filter_for_best_match:
			# If the user wants the single best match, we use the filter_query module
			# We combine all our matched global objects and let the filter decide the best one
			all_items = global_songs + global_videos + global_collections
			
			if not all_items:
				empty_response = Empty(
					service = gservice,
					meta = Meta(
						service = gservice,
						request = request,
						processing_time = total_time,
						filter_confidence_percentage = 0.0,
						http_code = 204
					)
				)
				await log(empty_response)
				return empty_response

			return await filter_query(
				service = gservice, 
				query_request = request, 
				items = all_items, 
				query = query, 
				query_is_explicit = is_explicit, 
				query_country_code = country_code
			)
		
		else:
			# Return a Query object containing all global results
			return Query(
				service = gservice,
				songs = global_songs,
				music_videos = global_videos,
				collections = global_collections,
				meta = Meta(
					service = gservice,
					request = request,
					processing_time = total_time,
					filter_confidence_percentage = 0.0,
					http_code = 200
				)
			)

	except Exception as error:
		error_obj = Error(
			service = gservice,
			component = gcomponent,
			error_msg = f'Error when searching query globally: "{error}"',
			meta = Meta(
				service = gservice,
				request = request,
				processing_time = current_unix_time_ms() - start_time,
				filter_confidence_percentage = 0.0,
				http_code = 500
			)
		)
		await log(error_obj)
		return error_obj