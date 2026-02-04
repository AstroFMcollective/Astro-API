from AstroAPI.InternalComponents.Legacy import *
from AstroAPI.ServiceCatalogAPI.components import *
from AstroAPI.ServiceCatalogAPI.media_services.music.youtube_music.components.generic import *
from AstroAPI.ServiceCatalogAPI.media_services.music.youtube_music.components.lookup.artist import lookup_artist



async def create_song_objects(results: dict, request: dict, start_time: int, http_code: int):

    """
        Iterate through YouTube Music's tracks list in their JSON response and convert all of it into Song objects.
        
        :param results: YouTube Music's JSON response.
        :param request: Request dict.
    """

    songs = []

    # Iterate through each song in the response
    for song in results:
        if song['resultType'] == 'song':
            song_type = 'track' # Set song type to 'track' because AFAIK there is nothing differentiating singles from tracks inside the metadata
            song_url = f'https://music.youtube.com/watch?v={song['videoId']}'
            song_id = song['videoId']
            song_title = song['title']
            song_is_explicit = song['isExplicit']
            
            # If artist info is available in the song result
            if 'artists' in song and song['artists'] != []:
                # Build Artist objects for each artist in the result
                song_artists = [
                    Artist(
                        service = service,
                        urls = f'https://music.youtube.com/channel/{artist["id"]}',
                        ids = artist['id'],
                        name = artist['name'],
                        meta = Meta(
                            service = service,
                            request = request,
                            processing_time = current_unix_time_ms() - start_time,
                            http_code = http_code,
                            filter_confidence_percentage = 100.0
                        )
                    ) for artist in song['artists']
                ]
            else:
                # If no artist info, look up the artist using the video ID
                # Because apparently that's a thing that can happen????????
                # I should probably make an issue on the API's repo
                song_artists = [await lookup_artist(video_id = song['videoId'], country_code = 'us')]

            # Build Cover object for the song
            song_cover = Cover(
                service = service,
                media_type = 'song',
                title = song_title,
                artists = song_artists,
                hq_urls = song['thumbnails'][len(song['thumbnails'])-1]['url'],
                lq_urls = song['thumbnails'][0]['url'],
                meta = Meta(
                    service = service,
                    request = request,
                    processing_time = current_unix_time_ms() - start_time,
                    http_code = http_code
                )
            )

            # Build Collection object for the song's album
            if song['album'] != None:
                song_collection = Collection(
                    service = service,
                    type = 'album',
                    urls = f'https://music.youtube.com/playlist?list={song['album']['id']}',
                    ids = song['album']['id'],
                    title = song['album']['name'],
                    artists = [song_artists[0]],
                    release_year = song['album']['year'] if 'year' in song['album'] else None,
                    cover = song_cover,
                    meta = Meta(
                        service = service,
                        request = request,
                        processing_time = current_unix_time_ms() - start_time,
                        http_code = http_code,
                        filter_confidence_percentage = 100.0
                    )
                )
            else:
                song_collection = None

            # Append the constructed Song object to the songs list
            songs.append(Song(
                service = service,
                type = song_type,
                urls = song_url,
                ids = song_id,
                title = song_title,
                artists = song_artists,
                collection = song_collection,
                is_explicit = song_is_explicit,
                cover = song_cover,
                meta = Meta(
                    service = service,
                    request = request,
                    processing_time = current_unix_time_ms() - start_time,
                    http_code = http_code
                )
            ))
    
    return songs