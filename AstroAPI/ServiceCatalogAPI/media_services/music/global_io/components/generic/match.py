from AstroAPI.ServiceCatalogAPI.components import *
from AstroAPI.InternalComponents.SystemMediaObjects import *
from AstroAPI.InternalComponents.Legacy.text_manipulation import calculate_similarity, bare_bones
from AstroAPI.ServiceCatalogAPI.media_services.music.global_io.components.generic.about import service as gservice
from AstroAPI.ServiceCatalogAPI.media_services.music.global_io.components.generic.compile_global.artists import compiled_artists
from AstroAPI.ServiceCatalogAPI.components.sort_dicts import sort_dicts

async def match_content(request: dict, results_lists: list[list[object]]) -> list[object]:
    """
        Takes lists of media objects from different services, finds matches based on content similarity,
        and merges them into single Global objects.
    """
    
    # Priority for determining "Source of Truth" (Title, Release Year, Explicit status, etc.)
    metadata_priority = ['spotify', 'deezer', 'youtube_music', 'apple_music']
    
    # Order for sorting URLs and IDs in the final object
    display_order = ['spotify', 'apple_music', 'youtube_music', 'deezer']
    
    # Flatten the lists but keep track of their source for easier sorting
    service_buckets = {service: [] for service in metadata_priority}
    
    for result_list in results_lists:
        if not result_list:
            continue
        service_name = result_list[0].service
        if service_name in service_buckets:
            service_buckets[service_name] = result_list
        else:
            if 'other' not in service_buckets:
                service_buckets['other'] = []
            service_buckets['other'].extend(result_list)

    clusters = []

    # Iterate through services in metadata priority order to establish the "base" of clusters
    processing_order = [s for s in metadata_priority if s in service_buckets]
    
    for service in processing_order:
        items = service_buckets[service]
        
        for item in items:
            match_found = False
            
            for cluster in clusters:
                representative = cluster[0]
                
                # SIMILARITY CHECK
                title_sim = calculate_similarity(bare_bones(item.title), bare_bones(representative.title))
                
                artist_sim = 0
                if item.artists and representative.artists:
                    artist_sim = calculate_similarity(bare_bones(item.artists[0].name), bare_bones(representative.artists[0].name))
                
                year_match = True
                if hasattr(item, 'release_year') and hasattr(representative, 'release_year'):
                    if item.release_year and representative.release_year:
                        if abs(item.release_year - representative.release_year) > 1:
                            year_match = False

                if title_sim > 800 and artist_sim > 800 and year_match:
                    cluster.append(item)
                    match_found = True
                    break
            
            if not match_found:
                clusters.append([item])

    global_objects = []

    for cluster in clusters:
        # Sort cluster by metadata priority so the first item determines the metadata
        cluster.sort(key=lambda x: metadata_priority.index(x.service) if x.service in metadata_priority else 999)
        
        primary_obj = cluster[0]
        
        # Merge URLs and IDs
        merged_urls = {}
        merged_ids = {}
        merged_processing_time = {}
        merged_confidence = {}
        
        for obj in cluster:
            if isinstance(obj.urls, dict):
                merged_urls.update(obj.urls)
            if isinstance(obj.ids, dict):
                merged_ids.update(obj.ids)
            
            if obj.meta:
                if isinstance(obj.meta.processing_time, dict):
                    merged_processing_time.update(obj.meta.processing_time)
                if isinstance(obj.meta.filter_confidence_percentage, dict):
                    merged_confidence.update(obj.meta.filter_confidence_percentage)

        # --- KEY CHANGE: Sort using display_order ---
        merged_urls = sort_dicts(merged_urls, display_order)
        merged_ids = sort_dicts(merged_ids, display_order)

        # Merge Artists
        cluster_artists_list = [obj.artists for obj in cluster]
        global_artists = compiled_artists(request, cluster_artists_list)

        global_cover = primary_obj.cover
        
        common_meta = Meta(
            service = gservice,
            request = request,
            processing_time = merged_processing_time,
            filter_confidence_percentage = merged_confidence,
            http_code = 200
        )

        if isinstance(primary_obj, Song):
            # Merge previews
            all_previews = {}
            for obj in cluster:
                if hasattr(obj, 'previews') and obj.previews and isinstance(obj.previews, dict):
                    all_previews.update(obj.previews)
            
            # Sort previews if they exist
            sorted_previews = sort_dicts(all_previews, display_order) if all_previews else None

            global_obj = Song(
                service = gservice,
                type = primary_obj.type,
                urls = merged_urls,
                ids = merged_ids,
                title = primary_obj.title,
                artists = global_artists,
                cover = global_cover,
                meta = common_meta,
                previews = sorted_previews,
                collection = primary_obj.collection,
                genre = primary_obj.genre,
                is_explicit = primary_obj.is_explicit
            )
            global_objects.append(global_obj)

        elif isinstance(primary_obj, Collection):
            global_obj = Collection(
                service = gservice,
                type = primary_obj.type,
                urls = merged_urls,
                ids = merged_ids,
                title = primary_obj.title,
                artists = global_artists,
                cover = global_cover,
                meta = common_meta,
                release_year = primary_obj.release_year,
                genre = primary_obj.genre
            )
            global_objects.append(global_obj)

        elif isinstance(primary_obj, MusicVideo):
            all_previews = {}
            for obj in cluster:
                if obj.previews and isinstance(obj.previews, dict):
                    all_previews.update(obj.previews)
            
            sorted_previews = sort_dicts(all_previews, display_order) if all_previews else None

            global_obj = MusicVideo(
                service = gservice,
                urls = merged_urls,
                ids = merged_ids,
                title = primary_obj.title,
                artists = global_artists,
                cover = global_cover,
                meta = common_meta,
                previews = sorted_previews,
                is_explicit = primary_obj.is_explicit,
                genre = primary_obj.genre
            )
            global_objects.append(global_obj)

    return global_objects