from AstroAPI.InternalComponents.Legacy import *
from AstroAPI.SnitchAPI.components.media import *
from AstroAPI.SnitchAPI.detection_services.audio.apple_music.components.get.song_preview import get_song_preview
from AstroAPI.SnitchAPI.detection_services.audio.submithub.components.check.audio import check_audio as submithub_ai
from AstroAPI.SnitchAPI.detection_services.image.sightengine.components.check.image import check_image as sightengine_ai
from AstroAPI.SnitchAPI.components.generic import service as gservice, component as gcomponent

from AstroAPI.ServiceCatalogAPI.media_services.music.global_io import global_io
from AstroAPI.ServiceCatalogAPI.media_services.music import spotify, apple_music, youtube_music, deezer

from asyncio import create_task, gather



async def check_song(service: object, id: str, song_country_code: str = None, lookup_country_code: str = 'us') -> object:
    # Prepare the request metadata
    request = {'request': 'check_song', 'service': service.service, 'id': id, 'song_country_code': song_country_code, 'lookup_country_code': lookup_country_code}
    # Record the start time for processing time calculation
    start_time = current_unix_time_ms()
    
    try:
        legal_results = ['check']
        reference_media = await global_io.lookup_song(service, id, song_country_code, lookup_country_code)

        cover_order = [spotify.service, deezer.service, youtube_music.service, apple_music.service]
        tasks = []
        
        for service in cover_order:
            if service in reference_media.cover.hq_urls:
                tasks.append(
                    create_task(
                        sightengine_ai(reference_media.cover.hq_urls[service])
                    )
                )
                break
        
        if apple_music.service in reference_media.ids:
            tasks.append(
                create_task(
                    submithub_ai(await get_song_preview(reference_media.ids[apple_music.service], song_country_code))
                )
            )

        analysis = await gather(*tasks)
        processing_time = {}

        if analysis != []:
            for item in analysis:
                if item != None:
                    if item.type in legal_results:
                        processing_time[item.service] = item.meta.processing_time[item.service]
                    else:
                        analysis.remove(item)
                        continue

                else:
                    analysis.remove(item)
                    continue

        processing_time[gservice] = current_unix_time_ms() - start_time

        if analysis != []:
            return SnitchAnalysis(
                service = gservice,
                analysis = analysis,
                analysed_media = reference_media,
                meta = Meta(
                    service = gservice,
                    request = request,
                    processing_time = processing_time,
                    http_code = 200
                )
            )
        else:
            return Empty(
                service = gservice,
                meta = Meta(
                    service = gservice,
                    request = request,
                    http_code = 204,
                    processing_time = current_unix_time_ms() - start_time
                )
            )

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
                processing_time = current_unix_time_ms() - start_time
            )
        )
        await log(error)
        return error