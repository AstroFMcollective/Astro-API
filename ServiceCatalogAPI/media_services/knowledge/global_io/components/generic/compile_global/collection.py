from ServiceCatalogAPI.components import *
from ServiceCatalogAPI.media_services.knowledge.global_io.components.generic.about import service as gservice, component as gcomponent
from ServiceCatalogAPI.media_services.knowledge.global_io.components.generic import *
from ServiceCatalogAPI.media_services.knowledge.global_io.components.generic.compile_global.artists import compiled_artists
from ServiceCatalogAPI.media_services.knowledge.global_io.components.generic.compile_global.cover import compiled_cover

def compiled_collection(request: dict, unlabeled_collections: list) -> Collection:
	while None in unlabeled_collections:
		unlabeled_collections.remove(None)
	
	labeled_collections = {result.service: result for result in unlabeled_collections}

	unlabeled_artists = [result.artists for result in unlabeled_collections]
	
	# Results order based on service priority
	# Some services have lesser quality or straight-up do not carry certain information, so we prioritize the ones who do
	all_services = [spotify.service, genius.service]
	general_order = [spotify.service, genius.service]
	type_order = [spotify.service, genius.service]
	urls_order = [spotify.service, genius.service]
	ids_order = [spotify.service, genius.service]
	title_order = [spotify.service, genius.service]
	release_date_order = [spotify.service, genius.service]
	genre_order = [spotify.service, genius.service]

	# Removing services from order if there were no results from those services
	for service in all_services:
		if service not in labeled_collections:
			general_order.remove(service)
			type_order.remove(service)
			urls_order.remove(service)
			ids_order.remove(service)
			title_order.remove(service)
			release_date_order.remove(service)
			genre_order.remove(service)

	# Declaring variables to hold the results
	result_type = None
	result_urls = {}
	result_ids = {}
	result_title = None
	result_artists = compiled_artists(request, unlabeled_artists)
	result_cover = compiled_cover(request, unlabeled_collections)
	result_genre = None
	result_release_year = None
	result_processing_time = {}
	result_confidence = {}

	# Iterating through the ordered list to find the first non-None result for each field
	for service_index in range(len(general_order)):
		if result_type is None:
			result_type = labeled_collections[type_order[service_index]].type
		if result_title is None:
			result_title = labeled_collections[title_order[service_index]].title
		if result_genre is None:
			result_genre = labeled_collections[genre_order[service_index]].genre
		if result_release_year is None:
			result_release_year = labeled_collections[release_date_order[service_index]].release_year
		if result_urls == {}:
			for result in unlabeled_collections:
				result_urls[result.service] = result.urls[result.service]
		if result_ids == {}:
			for result in unlabeled_collections:
				result_ids[result.service] = result.ids[result.service]
		if result_processing_time == {}:
			for result in unlabeled_collections:
				result_processing_time[result.service] = result.meta.processing_time
				result_confidence[result.service] = result.meta.filter_confidence_percentage
		if result_confidence == {}:
			for result in unlabeled_collections:
				result_confidence[result.service] = result.meta.filter_confidence_percentage

	# Building the Collection object with the compiled results
	collection = Collection(
		service = gservice,
		type = result_type,
		urls = result_urls,
		ids = result_ids,
		title = result_title,
		artists = result_artists,
		cover = result_cover,
		genre = result_genre,
		release_year = result_release_year,
		meta = Meta(
			service = gservice,
			request = request,
			processing_time = result_processing_time,   
			filter_confidence_percentage = result_confidence,
			http_code = 200
		)
	)

	return collection