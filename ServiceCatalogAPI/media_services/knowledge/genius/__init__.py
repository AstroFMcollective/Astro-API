from ServiceCatalogAPI.components import *
from .components.generic import *

from .components.search.song import search_song
from .components.search.query import search_query
from .components.lookup.song import lookup_song



class Genius:
    def __init__(self):
        self.service = service
        self.component = component

    async def search_song(self, artists: list, title: str, song_type: str = None, collection: str = None, is_explicit: bool = None, country_code: str = 'us') -> Knowledge | Empty | Error:
        return await search_song(artists = artists, title = title, song_type = song_type, collection = collection, is_explicit = is_explicit, country_code = country_code)
    
    async def search_query(self, query: str, country_code: str = 'us') -> Knowledge | Empty | Error:
        return await search_query(query = query, country_code = country_code)

    async def lookup_song(self, id: str, country_code: str = 'us') -> Knowledge | Empty | Error:
        return await lookup_song(id = id, country_code = country_code)



genius = Genius()