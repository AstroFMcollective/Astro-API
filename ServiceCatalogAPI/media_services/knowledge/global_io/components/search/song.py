from ServiceCatalogAPI.components import *
from ServiceCatalogAPI.media_services.knowledge.global_io.components.generic import *
from ServiceCatalogAPI.media_services.knowledge.global_io.components.generic import service as gservice, component as gcomponent

from ServiceCatalogAPI.media_services.knowledge.global_io.components.generic.compile_global.artists import compiled_artists
from ServiceCatalogAPI.media_services.knowledge.global_io.components.generic.compile_global.collection import compiled_collection
from ServiceCatalogAPI.media_services.knowledge.global_io.components.generic.compile_global.cover import compiled_cover

from asyncio import create_task, gather



async def search_song(artists: list, title: str, song_type: str = None, collection: str = None, is_explicit: bool = None, country_code: str = 'us', include_premade_media: list = None, exclude_services: list = None) -> object:
	# SINCE WHEN ARE PARAMETER VARIABLES PERSISTENT??????
	if include_premade_media is None:
		include_premade_media = []
	if exclude_services is None:
		exclude_services = []
	# Build the request dictionary with all parameters
	request = {'request': 'search_song', 'artists': artists, 'title': title, 'song_type': song_type, 'collection': collection, 'is_explicit': is_explicit, 'country_code': country_code, 'exclude_services': exclude_services}
	# Record the start time for processing time calculation
	start_time = current_unix_time_ms()

	try:
		# Define the service objects to use for searching
		service_objs = [spotify, genius]
		# Extract the service names from the service objects
		services = [obj.service for obj in service_objs]

		# Define which result types are considered valid
		legal_results = ['knowledge']

		# Exclude services if they already have a premade media object
		# This is to prevent duplicate searches and increase performance
		ignore_in_excluded_services = []
		for premade in include_premade_media:
			# If the premade media's service is not already excluded, add it to the exclusion list
			# Do this so we don't query the premade's service
			if premade.service not in exclude_services:
				exclude_services.append(premade.service)
			# Track which services are being ignored in the exclusion process
			ignore_in_excluded_services.append(premade.service)

		# Prepare asynchronous search tasks for each service not excluded
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

		# Run all search tasks concurrently and collect their results
		# This will be our list of unlabeled results
		unlabeled_results = await gather(*tasks)

		# Redefine excluded services to only include those not in the ignore list
		exclude_services = [service for service in exclude_services if service not in ignore_in_excluded_services]
		# Add premade media objects to the results
		for premade in include_premade_media:
			unlabeled_results.append(premade)
		# For each excluded service not in the ignore list, add an Empty result for later processing
		for service in exclude_services:
			if service not in ignore_in_excluded_services:
				unlabeled_results.append(
					Empty(
						service = service,
						meta = Meta(
							service = gservice, # Use Global IO service for metadata to indicate Empty result
							request = request,
							processing_time = current_unix_time_ms() - start_time,
							filter_confidence_percentage = {service: 0.0},
							http_code = 204 # No Content HTTP status code
						)
					)
				)

		# Create a dictionary mapping service names to their results
		labeled_results = {result.service: result for result in unlabeled_results}

		# Define the order of preference for each field from different services
		general_order = [spotify.service, genius.service]
		type_order = [spotify.service, genius.service]
		title_order = [spotify.service, genius.service]
		artists_order = [spotify.service, genius.service]
		collection_order = [spotify.service, genius.service]
		description_order = [genius.service, spotify.service]
		explicitness_order = [spotify.service, genius.service]
		release_date_order = [genius.service, spotify.service]
		cover_order = [genius.service, spotify.service]
		cover_single_order = [genius.service, spotify.service]
		bpm_order = [spotify.service, genius.service]
		key_order = [spotify.service, genius.service]
		length_order = [spotify.service, genius.service]
		time_signature_order = [spotify.service, genius.service]

		# Remove results that are not of a legal type from all order lists and results
		for service in services:
			if labeled_results[service].type not in legal_results:
				general_order.remove(service)
				type_order.remove(service)
				title_order.remove(service)
				artists_order.remove(service)
				collection_order.remove(service)
				explicitness_order.remove(service)
				cover_order.remove(service)
				cover_single_order.remove(service)
				bpm_order.remove(service)
				key_order.remove(service)
				length_order.remove(service)
				time_signature_order.remove(service)
				del unlabeled_results[list(labeled_results.keys()).index(service)]
				del labeled_results[service]

		# Initialize variables for the final compiled result
		result_type = None
		result_media_type = None
		result_urls = {}
		result_ids = {}
		result_processing_time = {}
		result_confidence = {}
		result_title = None
		# Compile artists from all results
		result_artists = compiled_artists(request, [song.artists for song in unlabeled_results])
		# Compile collection from all results
		result_collection = compiled_collection(request, [collection.collection for collection in unlabeled_results])
		result_description = None
		result_is_explicit = None
		result_release_date = None
		# Compile cover from all results
		result_cover = compiled_cover(request, unlabeled_results)
		result_bpm = None
		result_key = None
		result_length = None
		result_time_signature = None

		# For each service in the preferred order, fill in the result fields if not already set
		for service_index in range(len(general_order)):
			if result_type == None:
				result_type = labeled_results[type_order[service_index]].type
			if result_media_type == None:
				result_media_type = labeled_results[type_order[service_index]].media_type
			if result_urls == {}:
				for result in unlabeled_results:
					result_urls[result.service] = result.urls[result.service]
				result_urls = sort_dicts(result_urls, general_order)
			if result_ids == {}:
				for result in unlabeled_results:
					result_ids[result.service] = result.ids[result.service]
				result_ids = sort_dicts(result_ids, general_order)
			if result_processing_time == {}:
				for result in unlabeled_results:
					result_processing_time[result.service] = result.meta.processing_time[result.service]
				result_processing_time = sort_dicts(result_processing_time, general_order)
			if result_confidence == {}:
				for result in unlabeled_results:
					result_confidence[result.service] = result.meta.filter_confidence_percentage[result.service]
				result_confidence = sort_dicts(result_confidence, general_order)
			if result_title == None:
				result_title = labeled_results[title_order[service_index]].title
			if result_description == None:
				result_description = labeled_results[description_order[service_index]].description
			if result_is_explicit == None:
				result_is_explicit = labeled_results[explicitness_order[service_index]].is_explicit
			if result_release_date == None:
				result_release_date = labeled_results[release_date_order[service_index]].release_date
			if result_bpm == None:
				result_bpm = labeled_results[bpm_order[service_index]].bpm
			if result_key == None:
				result_key = labeled_results[key_order[service_index]].key
			if result_length == None:
				result_length = labeled_results[length_order[service_index]].length
			if result_time_signature == None:
				result_time_signature = labeled_results[time_signature_order[service_index]].time_signature

		# If a valid result type was found, return a compiled Knowledge object
		if result_type is not None:
			return Knowledge(
				service = gservice,
				media_type = result_media_type,
				urls = result_urls,
				ids = result_ids,
				title = result_title,
				collection = result_collection,
				artists = result_artists,
				description = result_description,
				release_date = result_release_date,
				cover = result_cover,
				is_explicit = result_is_explicit,
				bpm = result_bpm,
				key = result_key,
				length = result_length,
				time_signature = result_time_signature,
				meta = Meta(
					service = gservice,
					request = request,
					processing_time = result_processing_time,
					filter_confidence_percentage = {gservice: 100.0},
					http_code = 200
				)
			)
		else:
			empty_response = Empty(
				service = gservice,
				meta = Meta(
					service = gservice,
					request = request,
					processing_time = current_unix_time_ms() - start_time,
					filter_confidence_percentage = {gservice: 0.0},
					http_code = 204
				)
			)
			await log(empty_response)
			return empty_response

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