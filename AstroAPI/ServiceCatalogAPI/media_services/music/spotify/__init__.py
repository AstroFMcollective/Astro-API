from AstroAPI.ServiceCatalogAPI.components import *
from .components.generic import *

from .components.search.song import search_song
from .components.search.collection import search_collection
from .components.lookup.song import lookup_song
from .components.lookup.collection import lookup_collection



class Spotify:
    def __init__(self):
        self.service = service
        self.component = component

    async def search_song(self, artists: list, title: str, song_type: str = None, collection: str = None, is_explicit: bool = None, country_code: str = 'us') -> Song | Empty | Error:
        """
            # Spotify Song Music Search

            Search for song metadata on Spotify.

            :param artists: A list of artist names on the song that you're attempting to search.
            :param title: Song title.
            :param song_type: Whether the song is an album track or a single.
            :param collection: The name of the collection (album, EP) the song is a part of.
            :param is_explicit: Whether the song is explicit or not.
            :param country_code: The country code of the country in which you want to conduct the search.
        """
        return await search_song(artists = artists, title = title, song_type = song_type, collection = collection, is_explicit = is_explicit, country_code = country_code)

    async def search_collection(self, artists: list, title: str, year: int = None, country_code: str = 'us') -> Collection | Empty | Error:
        """
            # Spotify Collection Music Search

            Search for collection metadata on Spotify.

            :param artists: A list of artist names on the song that you're attempting to search.
            :param title: Song title.
            :param year: The name of the collection (album, EP) the song is a part of.
            :param country_code: The country code of the country in which you want to conduct the search.
        """
        return await search_collection(artists = artists, title = title, year = year, country_code = country_code)

    async def lookup_song(self, id: str, country_code: str = 'us') -> Song | Empty | Error:
        """
            # Spotify Song Music Lookup

            Lookup for song metadata on Spotify via song ID.

            :param id: Song ID.
            :param country_code: The country code of the country in which you want to conduct the lookup.
        """
        return await lookup_song(id = id, country_code = country_code)
    
    async def lookup_collection(self, id: str, country_code: str = 'us') -> Collection | Empty | Error:
        """
            # Spotify Collection Music Lookup

            Lookup for collection metadata on Spotify via collection ID.

            :param id: Collection ID.
            :param country_code: The country code of the country in which you want to conduct the lookup.
        """
        return await lookup_collection(id = id, country_code = country_code)



spotify = Spotify()

print(f'[ServiceCatalogAPI] {component} initialized')
