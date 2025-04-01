from AstroAPI.components import *
from .components.generic import *

from .components.lookup.song import lookup_song



class Spotify:
    def __init__(self):
        self.service = service
        self.component = component

    async def lookup_song(self, id: str, country_code: str = 'us') -> Song | Empty | Error:
        song = await lookup_song(id = id, country_code = country_code)
        return song

spotify = Spotify()