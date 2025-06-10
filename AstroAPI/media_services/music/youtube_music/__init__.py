from AstroAPI.components import *
from .components.generic import *

from .components.search.song import search_song
from .components.search.music_video import search_music_video
from .components.search.collection import search_collection
from .components.search.query import search_query
from .components.lookup.song import lookup_song
from .components.lookup.collection import lookup_collection
from .components.lookup.artist import lookup_artist


class YouTubeMusic:
    def __init__(self):
        self.service = service
        self.component = component

    async def search_song(self, artists: list, title: str, song_type: str = None, collection: str = None, is_explicit: bool = None, country_code: str = 'us') -> Song | Empty | Error:
        return await search_song(artists = artists, title = title, song_type = song_type, collection = collection, is_explicit = is_explicit, country_code = country_code)
    
    async def search_music_video(self, artists: list, title: str, is_explicit: bool = None, country_code: str = 'us') -> MusicVideo | Empty | Error:
        return await search_music_video(artists = artists, title = title, is_explicit = is_explicit, country_code = country_code)

    async def search_collection(self, artists: list, title: str, year: int = None, country_code: str = 'us') -> Collection | Empty | Error:
        return await search_collection(artists = artists, title = title, year = year, country_code = country_code)
    
    async def search_query(self, query: str, country_code: str = 'us') -> Song | Collection | Empty | Error:
        return await search_query(query = query, country_code = country_code)

    async def lookup_song(self, id: str, country_code: str = 'us') -> Song | Empty | Error:
        return await lookup_song(id = id, country_code = country_code)
    
    async def lookup_collection(self, id: str, country_code: str = 'us') -> Collection | Empty | Error:
        return await lookup_collection(id = id, country_code = country_code)
    
    async def lookup_artist(self, id: str = None, video_id: str = None, country_code: str = 'us') -> Artist | Empty | Error:
        return await lookup_artist(id = id, video_id = video_id, country_code = country_code)

youtube_music = YouTubeMusic()