from AstroAPI.InternalComponents.Legacy import *
from .components.generic import *

from .components.search.song import search_song
from .components.lookup.song import lookup_song



class Spotify:
    def __init__(self):
        self.service = service
        self.component = component

    async def search_song(self, artists: list, title: str, song_type: str = None, collection: str = None, is_explicit: bool = None, country_code: str = 'us') -> Knowledge | Empty | Error:
        """
            # Spotify Song Knowledge Search

            Search for song knowledge on Spotify.

            :param artists: A list of artist names on the song that you're attempting to search.
            :param title: Song title.
            :param song_type: Whether the song is an album track or a single.
            :param collection: The name of the collection (album, EP) the song is a part of.
            :param is_explicit: Whether the song is explicit or not.
            :param country_code: The country code of the country in which you want to conduct the search.
        """
        return await search_song(artists = artists, title = title, song_type = song_type, collection = collection, is_explicit = is_explicit, country_code = country_code)

    async def lookup_song(self, id: str, country_code: str = 'us') -> Knowledge | Empty | Error:
        """
            # Spotify Song Knowledge Lookup

            Lookup for song knowledge on Spotify via song ID.

            :param id: Song ID.
            :param country_code: The country code of the country in which you want to conduct the lookup.
        """
        return await lookup_song(id = id, country_code = country_code)



spotify = Spotify()

print(f'[ServiceCatalogAPI] {component} initialized')
