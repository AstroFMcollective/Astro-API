from AstroAPI.InternalComponents.Legacy import *
from AstroAPI.ServiceCatalogAPI.media_services.music.spotify.components.generic import *



async def create_song_objects(json_response: dict, request: dict, start_time: int, http_code: int):

    """
        Iterate through Spotify's tracks list in their JSON response and convert all of it into Song objects.
        
        :param json_response: Spotify's JSON response.
        :param request: Request dict.
    """

    songs = []

    # Iterate through each song in the response
    for song in json_response['tracks']['items']:
        # Extract song details
        song_type = ('track' if song['album']['album_type'] != 'single' else 'single')
        song_url = song['external_urls']['spotify']
        song_id = song['id']
        song_title = song['name']
        song_artists = get_artists_of_media(request, song['artists'])
        song_is_explicit = song['explicit']
        
        # Extract collection details
        collection_type = 'album' if song['album']['album_type'] != 'single' else 'ep'
        collection_url = song['album']['external_urls']['spotify']
        collection_id = song['album']['id']
        collection_title = remove_feat(song['album']['name'])
        collection_artists = get_artists_of_media(request, song['album']['artists'])
        collection_year = song['album']['release_date'][:4]

        # Create Cover object for the collection
        media_cover = Cover(
            service = service,
            media_type = collection_type,
            title = collection_title,
            artists = collection_artists,
            hq_urls = song['album']['images'][0]['url'] if song['album']['images'] != [] else None,
            lq_urls = song['album']['images'][len(song['album']['images']) - 1]['url'] if song['album']['images'] != [] else None,
            meta = Meta(
                service = service,
                request = request,
                processing_time = 0,
                filter_confidence_percentage = 100.0,
                http_code = 200
            )
        )

        # Create Collection object for the song's album/EP
        song_collection = Collection(
            service = service,
            type = collection_type,
            urls = collection_url,
            ids = collection_id,
            title = collection_title,
            artists = collection_artists,
            release_year = collection_year,
            cover = media_cover,
            meta = Meta(
                service = service,
                request = request,
                processing_time = 0,
                filter_confidence_percentage = 100.0,
                http_code = 200
            )
        )

        # Append the Song object to the songs list
        songs.append(Song(
            service = service,
            type = song_type,
            urls = song_url,
            ids = song_id,
            title = song_title,
            artists = song_artists,
            collection = song_collection,
            is_explicit = song_is_explicit,
            cover = media_cover,
            meta = Meta(
                service = service,
                request = request,
                processing_time = current_unix_time_ms() - start_time,
                http_code = http_code
            )
        ))
    
    return songs