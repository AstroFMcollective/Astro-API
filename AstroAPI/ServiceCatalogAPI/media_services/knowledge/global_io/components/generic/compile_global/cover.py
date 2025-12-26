from AstroAPI.ServiceCatalogAPI.components import *
from AstroAPI.InternalComponents.SystemMediaObjects import *
from AstroAPI.InternalComponents.Legacy import *
from AstroAPI.ServiceCatalogAPI.media_services.knowledge.global_io.components.generic.about import service as gservice, component as gcomponent
from AstroAPI.ServiceCatalogAPI.media_services.knowledge.global_io.components.generic import *
from AstroAPI.ServiceCatalogAPI.media_services.knowledge.global_io.components.generic.compile_global.artists import compiled_artists
from AstroAPI.ServiceCatalogAPI.components.global_io.sort_dicts import sort_dicts



def compiled_cover(request: dict, unlabeled_results: list) -> Cover:
    labeled_results = {result.service: result for result in unlabeled_results}

    unlabeled_artists = [result.artists for result in unlabeled_results]

    # Results order based on service priority
    # Some services have lesser quality or straight-up do not carry certain information, so we prioritize the ones who do
    all_services = [spotify.service, genius.service]
    general_order = [spotify.service, genius.service]
    ids_order = [spotify.service, genius.service]
    name_order = [spotify.service, genius.service]
    type_order = [spotify.service, genius.service]

    # Removing services from order if there were no results from those services
    for service in all_services:
        if service not in labeled_results:
            general_order.remove(service)
            ids_order.remove(service)
            name_order.remove(service)
            type_order.remove(service)

    # Declaring variables to hold the results
    result_type = None
    result_title = None
    result_artists = compiled_artists(request, unlabeled_artists)
    result_cover_hq_urls = {}
    result_cover_lq_urls = {}
    result_processing_time = {}
    result_confidence = {}

    # Iterating through the ordered list to find the first non-None result for each field
    for service_index in range(len(general_order)):
        if result_type is None:
            result_type = labeled_results[type_order[service_index]].type
        if result_title is None:
            result_title = labeled_results[name_order[service_index]].title
        if result_cover_hq_urls == {}:
            for result in unlabeled_results:
                result_cover_hq_urls[result.service] = result.cover.hq_urls[result.service]
            result_cover_hq_urls = sort_dicts(result_cover_hq_urls, general_order)
        if result_cover_lq_urls == {}:
            for result in unlabeled_results:
                result_cover_lq_urls[result.service] = result.cover.lq_urls[result.service]
            result_cover_lq_urls = sort_dicts(result_cover_lq_urls, general_order)
        if result_processing_time == {}:
            for result in unlabeled_results:
                result_processing_time[result.service] = result.meta.processing_time[result.service]
                result_confidence[result.service] = result.meta.filter_confidence_percentage[result.service]
            result_processing_time = sort_dicts(result_processing_time, general_order)

    # Creating the Cover object
    cover = Cover(
        service = gservice,
        media_type = result_type,
        title = result_title,
        artists = result_artists,
        hq_urls = result_cover_hq_urls,
        lq_urls = result_cover_lq_urls,
        meta = Meta(
            service = gservice,
            request = request,
            processing_time = 0,
            filter_confidence_percentage = 0,
            http_code = 200,
        )
    )

    return cover

