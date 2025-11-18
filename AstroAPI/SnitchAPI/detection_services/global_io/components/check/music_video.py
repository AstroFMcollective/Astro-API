from AstroAPI.InternalComponents.Legacy import *
from AstroAPI.SnitchAPI.components.media import *
from AstroAPI.SnitchAPI.detection_services.audio.apple_music.components.get.song_preview import get_song_preview
from AstroAPI.SnitchAPI.detection_services.audio.submithub.components.check.audio import check_audio as submithub_ai
from AstroAPI.SnitchAPI.detection_services.image.sightengine.components.check.image import check_image as sightengine_ai
from AstroAPI.SnitchAPI.components.generic import service as gservice, component as gcomponent

from AstroAPI.ServiceCatalogAPI.media_services.music.global_io import global_io
from AstroAPI.ServiceCatalogAPI.media_services.music import apple_music, youtube_music

from asyncio import create_task, gather



async def check_music_video(service: object, id: str, song_country_code: str = None, lookup_country_code: str = 'us') -> object:
    # Prepare the request metadata
    request = {'request': 'check_music_video', 'service': service.service, 'id': id, 'song_country_code': song_country_code, 'lookup_country_code': lookup_country_code}
    # Record the start time for processing time calculation
    start_time = current_unix_time_ms()
    
    try:
        legal_results = ['image', 'audio']
        reference_media = await global_io.lookup_music_video(service, id, song_country_code, lookup_country_code)

        cover_order = [youtube_music.service, apple_music.service]
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
            analysis = [item for item in analysis if item.media_type in legal_results]
            for item in analysis:
                processing_time[item.service] = item.meta.processing_time[item.service]
        processing_time[gservice] = current_unix_time_ms() - start_time

        if analysis != []:
            return SnitchAnalysis(
                service = gservice,
                analysis = analysis,
                analysed_media = reference_media,
                meta = Meta(
                    service = gservice,
                    request = request,
                    processing_time = current_unix_time_ms() - start_time,
                    http_code = 200
                )
            )
        else:
            return Empty(
                service = gservice,
                meta = Meta(
                    service = gservice,
                    request = request,
                    http_code = 500,
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