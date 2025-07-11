from AstroAPI.components import *
from AstroAPI.media_services.music.global_io.components.generic import *
from AstroAPI.media_services.music.global_io.components.generic import service as gservice, component as gcomponent

from AstroAPI.media_services.music.global_io.components.generic.compile_global.artists import compiled_artists
from AstroAPI.media_services.music.global_io.components.generic.compile_global.collection import compiled_collection
from AstroAPI.media_services.music.global_io.components.generic.compile_global.cover import compiled_cover

from asyncio import create_task, gather



async def search_song(artists: list, title: str, song_type: str = None, collection: str = None, is_explicit: bool = None, country_code: str = 'us', include_premade_media: list = [], exclude_services: list = []) -> object:
	request = {'request': 'search_song', 'artists': artists, 'title': title, 'song_type': song_type, 'collection': collection, 'is_explicit': is_explicit, 'country_code': country_code, 'exclude_services': exclude_services}
	start_time = current_unix_time_ms()

	# Try to perform the song search operation
	try:
		# Define service objects
		service_objs = [spotify, apple_music, youtube_music, deezer]
		services = [obj.service for obj in service_objs]

		legal_results = ['track', 'single']

		# Exclude services if they already have a premade media object
		# This is to prevent duplicate searches, increasing performance
		ignore_in_excluded_services = []
		for premade in include_premade_media:
			if premade.service in exclude_services:
				if premade.service not in exclude_services:
					exclude_services.append(premade.service)
				ignore_in_excluded_services.append(premade.service)

		# Search services for songs
		tasks = []
		for obj in service_objs:
			if obj.service not in exclude_services:
				tasks.append(
					create_task(
						obj.search_song(
							artists, title, song_type, collection, is_explicit, country_code
						),
						name = obj.service
					)
				)

		unlabeled_results = await gather(*tasks)

		# Redefine exluded services to only include those that are not in the ignore list
		exclude_services = [service for service in exclude_services if service not in ignore_in_excluded_services]
		for premade in include_premade_media:
			unlabeled_results.append(premade) # Add premade media objects to the results
		for service in exclude_services: # If a service is excluded, we add an Empty result for it so it can still be processed later
			if service not in ignore_in_excluded_services:
				unlabeled_results.append(
					Empty(
						service = service,
						meta = Meta(
							service = gservice, # We use the Global IO service for the metadata so we know it generated the Empty result
							request = request,
							processing_time = current_unix_time_ms() - start_time,
							filter_confidence_percentage = {service: 0.0},
							http_code = 204 # No Content HTTP status code
						)
					)
				)

		labeled_results = {result.service: result for result in unlabeled_results}

		# Results order based on service priority
		# Some services have lesser quality or straight-up do not carry certain information, so we prioritize the ones who do
		general_order = [spotify.service, apple_music.service, youtube_music.service, deezer.service]
		type_order = [apple_music.service, spotify.service, deezer.service, youtube_music.service]
		title_order = [spotify.service, apple_music.service, deezer.service, youtube_music.service]
		explicitness_order = [spotify.service, apple_music.service, deezer.service, youtube_music.service]
		genre_order = [apple_music.service, spotify.service, deezer.service, youtube_music.service]

		# Removing errors and empty results from the order lists and results
		for service in services:
			if labeled_results[service].type not in legal_results:
				general_order.remove(service)
				type_order.remove(service)
				title_order.remove(service)
				explicitness_order.remove(service)
				genre_order.remove(service)
				del unlabeled_results[list(labeled_results.keys()).index(service)]
				del labeled_results[service]

		# Declaring variables to hold the results
		result_type = None
		result_urls = {}
		result_ids = {}
		result_title = None
		result_artists = compiled_artists(request, [song.artists for song in unlabeled_results])
		result_collection = compiled_collection(request, [collection.collection for collection in unlabeled_results])
		result_is_explicit = None
		result_genre = None
		result_cover = compiled_cover(request, unlabeled_results)
		result_processing_time = {}
		result_confidence = {}

		# Iterating through the ordered list to find the first non-None result for each field
		for service_index in range(len(general_order)):
			if result_type is None:
				result_type = labeled_results[type_order[service_index]].type
			if result_title is None:
				result_title = labeled_results[title_order[service_index]].title
			if result_is_explicit is None:
				result_is_explicit = labeled_results[explicitness_order[service_index]].is_explicit
			if result_genre is None:
				result_genre = labeled_results[genre_order[service_index]].genre
			if result_urls == {}:
				for result in unlabeled_results:
					result_urls[result.service] = result.urls[result.service]
			if result_ids == {}:
				for result in unlabeled_results:
					result_ids[result.service] = result.ids[result.service]
			if result_processing_time == {}:
				for result in unlabeled_results:
					result_processing_time[result.service] = result.meta.processing_time[result.service]
			if result_confidence == {}:
				for result in unlabeled_results:
					result_confidence[result.service] = result.meta.filter_confidence_percentage[result.service]

		# If everything went right, we create a Song object with the results and return it
		if result_type is not None:
			song = Song(
				service = gservice,
				type = result_type,
				urls = result_urls,
				ids = result_ids,
				title = result_title,
				artists = result_artists,
				collection = result_collection,
				is_explicit = result_is_explicit,
				genre = result_genre,
				cover = result_cover,
				meta = Meta(
					service = gservice,
					request = request,
					processing_time = current_unix_time_ms() - start_time,
					filter_confidence_percentage = {gservice: 100.0},
					http_code = 200
				)
			)
			return song
		else:
			error = Empty(
				service = gservice,
				meta = Meta(
					service = gservice,
					request = request,
					processing_time = current_unix_time_ms() - start_time,
					filter_confidence_percentage = {gservice: 0.0},
					http_code = 204
				)
			)
			await log(error)
			return error

	# If sinister things happen
	except Exception as error:
		error = Error(
			service = gservice,
			component = gcomponent,
			error_msg = f'Error when searching song: "{error}"',
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