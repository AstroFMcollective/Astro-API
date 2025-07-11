from AstroAPI.components import *
from .components.generic import *

from .components.search.song_knowledge import search_song_knowledge
from .components.lookup.song_knowledge import lookup_song_knowledge



class Spotify:
    def __init__(self):
        self.service = service
        self.component = component

    async def search_song_knowledge(self, artists: list, title: str, song_type: str = None, collection: str = None, is_explicit: bool = None, country_code: str = 'us') -> Knowledge | Empty | Error:
        song = await search_song_knowledge(artists = artists, title = title, song_type = song_type, collection = collection, is_explicit = is_explicit, country_code = country_code)
        return song

    async def lookup_song_knowledge(self, id: str, country_code: str = 'us') -> Knowledge | Empty | Error:
        song = await lookup_song_knowledge(id = id, country_code = country_code)
        return song



spotify = Spotify()