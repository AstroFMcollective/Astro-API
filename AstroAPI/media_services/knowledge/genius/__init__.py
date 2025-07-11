from AstroAPI.components import *
from .components.generic import *

from .components.search.song_knowledge import search_song_knowledge
from .components.search.query_knowledge import search_query_knowledge
from .components.lookup.song_knowledge import lookup_song_knowledge



class Genius:
    def __init__(self):
        self.service = service
        self.component = component

    async def search_song_knowledge(self, artists: list, title: str, song_type: str = None, collection: str = None, is_explicit: bool = None, country_code: str = 'us') -> Knowledge | Empty | Error:
        return await search_song_knowledge(artists = artists, title = title, song_type = song_type, collection = collection, is_explicit = is_explicit, country_code = country_code)
    
    async def search_query_knowledge(self, query: str, country_code: str = 'us') -> Knowledge | Empty | Error:
        return await search_query_knowledge(query = query, country_code = country_code)

    async def lookup_song_knowledge(self, id: str, country_code: str = 'us') -> Knowledge | Empty | Error:
        return await lookup_song_knowledge(id = id, country_code = country_code)



genius = Genius()