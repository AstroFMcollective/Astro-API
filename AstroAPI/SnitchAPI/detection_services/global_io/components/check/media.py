from AstroAPI.SnitchAPI.components import *
from AstroAPI.InternalComponents.SystemMediaObjects import *
from AstroAPI.InternalComponents.Legacy import *
from AstroAPI.SnitchAPI.detection_services.audio.apple_music.components.get.song_preview import get_song_preview
from AstroAPI.SnitchAPI.detection_services.audio.submithub.components.check.audio import check_audio as submithub_ai
from AstroAPI.SnitchAPI.detection_services.image.sightengine.components.check.image import check_image as sightengine_ai
from AstroAPI.SnitchAPI.components.generic import service as gservice, component as gcomponent

from AstroAPI.ServiceCatalogAPI.media_services.music import spotify, apple_music, youtube_music, deezer

from asyncio import create_task, gather



async def check_media(media: dict) -> object:
    # Prepare the request metadata
    request = {'request': 'check_media'}
    # Record the start time for processing time calculation
    start_time = current_unix_time_ms()
    
    try:
        legal_results = ['image', 'audio']
        cover_order = [spotify.service, deezer.service, youtube_music.service, apple_music.service]
        tasks = []
        
        if media['type'] not in ['empty_response', 'error']:
            for service in cover_order:
                if service in media['cover']['hq_urls']:
                    tasks.append(
                        create_task(
                            sightengine_ai(media['cover']['hq_urls'][service])
                        )
                    )
                    break
            
            if apple_music.service in media['ids'] and media['type'] not in ['album', 'ep']:
                if 'song_country_code' in media['meta']['request']:
                    tasks.append(
                        create_task(
                            submithub_ai(await get_song_preview(media['ids'][apple_music.service], media['meta']['request']['song_country_code']))
                        )
                    )
                else:
                    tasks.append(
                        create_task(
                            submithub_ai(await get_song_preview(media['ids'][apple_music.service], media['meta']['request']['country_code']))
                        )
                    )

            analysis = await gather(*tasks)
            processing_time = {}

            if analysis != []:
                for item in analysis:
                    if item != None:
                        if item.media_type in legal_results:
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
                    analysed_media = media,
                    meta = Meta(
                        service = gservice,
                        request = request,
                        http_code = 200,
                        processing_time = processing_time
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
        else:
            error = Error(
                service = gservice,
                component = gcomponent,
                error_msg = f'Bad request: invalid media provided',
                meta = Meta(
                    service = gservice,
                    request = request,
                    http_code = 400,
                    processing_time = current_unix_time_ms() - start_time
                )
            )
            await log(error, [discord.File(fp = StringIO(json.dumps(media, indent = 4)), filename = f'media.json')])
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
                processing_time = current_unix_time_ms() - start_time
            )
        )
        await log(error, [discord.File(fp = StringIO(json.dumps(media, indent = 4)), filename = f'media.json')])
        return error