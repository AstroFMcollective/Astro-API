from AstroAPI.ServiceCatalogAPI.components import *
from AstroAPI.InternalComponents.SystemMediaObjects import *
from AstroAPI.InternalComponents.Legacy import *
from AstroAPI.ServiceCatalogAPI.media_services.music.deezer.components.generic import *

from asyncio import create_task, gather



async def search_query(query: str, filter_for_best_match: bool = True, media_types: list = None, is_explicit: bool = None, country_code: str = 'us'):
	# Prepare the request dictionary with search parameters
	request = {'request': 'search_query', 'query': query, 'country_code': country_code}
	# Lookup JSON variable for later debugging
	lookup_json = None
	# Record the start time for processing time calculation
	start_time = current_unix_time_ms()
	
	try:
		if media_types == None:
			query_media = ['track', 'album']
		else:
			deezer_types = []
			if 'song' in media_types:
				deezer_types.append('track')
			if 'collection' in media_types:
				deezer_types.append('album')
			query_media = deezer_types

		tasks = []
		for media_type in query_media:
			tasks.append(
				create_task(
					get_search_wrapper(
						media = media_type,
						query = query
					)
				)
			)
		
		results = await gather(*tasks)

		lookup_json = [result for result in results]

		songs = []
		collections = []

		for media_type in query_media:
			if media_type == 'song':
				songs = await create_song_objects(
					json_response = results[query_media.index(media_type)],
					request = request,
					start_time = start_time,
					http_code = 200,
					incomplete_artist_info = True
				)
			elif media_type == 'collection':
				songs = await create_collection_objects(
					json_response = results[query_media.index(media_type)],
					request = request,
					start_time = start_time,
					http_code = 200
				)

		if filter_for_best_match == False:
			return Query(
				service = service,
				songs = songs,
				collections = collections,
				meta = Meta(
					service = service,
					request = request,
					processing_time = current_unix_time_ms() - start_time,
					filter_confidence_percentage = 0.0, # Because there was no filtering involved
					http_code = 200
				)
			)
		
		else:
			items = []
			items.extend(songs)
			items.extend(collections)
			return await filter_query(service = service, query_request = request, items = items, query = query, query_is_explicit = is_explicit, query_country_code = country_code)

	# Handle any exceptions that occur during the process
	except Exception as error:
		error = Error(
			service = service,
			component = component,
			error_msg = f'Error when looking up collection: "{error}"',
			meta = Meta(
				service = service,
				request = request,
				http_code = 500,
				processing_time = {service: current_unix_time_ms() - start_time}
			)
		)
		await log(error, [discord.File(fp = StringIO(json.dumps(lookup_json, indent = 4)), filename = f'{query}.json')])
		return error