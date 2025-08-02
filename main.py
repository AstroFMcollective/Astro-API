import ServiceCatalogAPI as ServiceCatalog
from fastapi import FastAPI

api = FastAPI()

music_media_services = ['spotify', 'apple_music', 'youtube_music', 'deezer']
music_media_services = ['spotify', 'genius']


# TODO: figure out service exclusion for global interface
# Song Search for media services
@api.get("/{media}/{service}/search_song")
async def search_song(media: str, service: str, artist: str, title: str, song_type: str, collection_title: str, is_explicit: str, country_code: str = 'us'):
    if media == 'music':
        service_api = getattr(ServiceCatalog.music, service)
    elif media == 'knowledge':
        service_api = getattr(ServiceCatalog.knowledge, service)
    song_object = await service_api.search_song(
        artists = [artist],
        title = title,
        song_type = song_type,
        collection = collection_title,
        is_explicit = True if is_explicit.lower() == 'true' else False,
        country_code = country_code
    )
    return song_object.json
    
# TODO: add service_id for global interface compatibility and possible service conversion
# Song Lookup for media services
@api.get("/{media}/{service}/lookup_song")
async def lookup_song(media: str, service: str, id: str, country_code: str = 'us'):
    if media == 'music':
        service_api = getattr(ServiceCatalog.music, service)
    elif media == 'knowledge':
        service_api = getattr(ServiceCatalog.knowledge, service)
    song_object = await service_api.lookup_song(id, country_code)
    return song_object.json

# TODO: add service_id for global interface compatibility and possible service conversion
# Collection Lookup for media services
@api.get("/{media}/{service}/lookup_collection")
async def lookup_collection(media: str, service: str, id: str, country_code: str = 'us'):
    if media == 'music':
        service_api = getattr(ServiceCatalog.music, service)
    elif media == 'knowledge':
        service_api = getattr(ServiceCatalog.knowledge, service)
    collection_object = await service_api.lookup_collection(id, country_code)
    return collection_object.json

# TODO: add service_id for global interface compatibility and possible service conversion
# Music Video Lookup for media services
@api.get("/{media}/{service}/lookup_music_video")
async def lookup_music_video(media: str, service: str, id: str, country_code: str = 'us'):
    if media == 'music':
        service_api = getattr(ServiceCatalog.music, service)
    elif media == 'knowledge':
        service_api = getattr(ServiceCatalog.knowledge, service)
    mv_object = await service_api.lookup_music_video(id, country_code)
    return mv_object.json