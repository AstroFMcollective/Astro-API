from AstroAPI.components import *
from .components.generic import *

from .components.search.song import search_song
from .components.search.collection import search_collection
from .components.lookup.song import lookup_song
from .components.lookup.collection import lookup_collection



class Deezer:
    def __init__(self):
        self.service = service
        self.component = component

    async def search_song(self, artists: list, title: str, song_type: str = None, collection: str = None, is_explicit: bool = None, country_code: str = 'us') -> Song | Empty | Error:
        song = await search_song(artists = artists, title = title, song_type = song_type, collection = collection, is_explicit = is_explicit, country_code = country_code)
        return song
    
    async def search_collection(self, artists: list, title: str, year: int = None, country_code: str = 'us') -> Collection | Empty | Error:
        collection = await search_collection(artists = artists, title = title, year = year, country_code = country_code)
        return collection

    async def lookup_song(self, id: str, country_code: str = 'us') -> Song | Empty | Error:
        song = await lookup_song(id = id, country_code = country_code)
        return song
    
    async def lookup_collection(self, id: str, country_code: str = 'us') -> Collection | Empty | Error:
        collection = await lookup_collection(id = id, country_code = country_code)
        return collection
    

    
deezer = Deezer()