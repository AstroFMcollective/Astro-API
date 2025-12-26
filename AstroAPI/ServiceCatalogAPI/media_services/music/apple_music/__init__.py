from AstroAPI.ServiceCatalogAPI.components import *
from AstroAPI.InternalComponents.SystemMediaObjects import *
from AstroAPI.InternalComponents.Legacy import *
from .components.generic import *

from .components.search.song import search_song
from .components.search.collection import search_collection
from .components.search.music_video import search_music_video
from .components.lookup.song import lookup_song
from .components.lookup.collection import lookup_collection
from .components.lookup.music_video import lookup_music_video
from .components.lookup.artist import lookup_artist

class AppleMusic:
	def __init__(self):
		self.service = service
		self.component = component

	async def search_song(self, artists: list, title: str, song_type: str = None, collection: str = None, is_explicit: bool = None, country_code: str = 'us') -> Song | Empty | Error:
		"""
            # Apple Music Song Music Search

            Search for song metadata on Apple Music (via the iTunes API).

            :param artists: A list of artist names on the song that you're attempting to search.
            :param title: Song title.
            :param song_type: Whether the song is an album track or a single.
            :param collection: The name of the collection (album, EP) the song is a part of.
            :param is_explicit: Whether the song is explicit or not.
            :param country_code: The country code of the country in which you want to conduct the search.
        """
		return await search_song(artists = artists, title = title, song_type = song_type, collection = collection, is_explicit = is_explicit, country_code = country_code)
	
	async def search_music_video(self, artists: list, title: str, is_explicit: bool = None, country_code: str = 'us') -> MusicVideo | Empty | Error:
		"""
            # Apple Music Music Video Music Search

            Search for music video metadata on Apple Music (via the iTunes API).

            :param artists: A list of artist names on the music video that you're attempting to search.
            :param title: Music video title.
            :param is_explicit: Whether the music video is explicit or not.
            :param country_code: The country code of the country in which you want to conduct the search.
        """
		return await search_music_video(artists = artists, title = title, is_explicit = is_explicit, country_code = country_code)

	async def search_collection(self, artists: list, title: str, year: int = None, country_code: str = 'us') -> Collection | Empty | Error:
		"""
            # Apple Music Collection Music Search

            Search for collection metadata on Apple Music (via the iTunes API).

            :param artists: A list of artist names on the song that you're attempting to search.
            :param title: Song title.
            :param year: The name of the collection (album, EP) the song is a part of.
            :param country_code: The country code of the country in which you want to conduct the search.
        """
		return await search_collection(artists = artists, title = title, year = year, country_code = country_code)

	async def lookup_song(self, id: str, country_code: str = 'us') -> Song | Empty | Error:
		"""
            # Apple Music Song Music Lookup

            Lookup for song metadata on Apple Music (via the iTunes API) via song ID.

            :param id: Song ID.
            :param country_code: The country code of the country in which you want to conduct the lookup.
        """
		return await lookup_song(id = id, country_code = country_code)
	
	async def lookup_music_video(self, id: str, country_code: str = 'us') -> MusicVideo | Empty | Error:
		"""
            # Apple Music Music Video Music Lookup

            Lookup for music video metadata on Apple Music (via the iTunes API) via video ID.

            :param id: Video ID.
            :param country_code: The country code of the country in which you want to conduct the lookup.
        """
		return await lookup_music_video(id = id, country_code = country_code)

	async def lookup_collection(self, id: str, country_code: str = 'us') -> Collection | Empty | Error:
		"""
            # Apple Music Collection Music Lookup

            Lookup for collection metadata on Apple Music (via the iTunes API) via collection ID.

            :param id: Collection ID.
            :param country_code: The country code of the country in which you want to conduct the lookup.
        """
		return await lookup_collection(id = id, country_code = country_code)

	async def lookup_artist(self, id: str, country_code: str = 'us') -> Song | Empty | Error:
		"""
            # Apple Music Artist Music Lookup

            Lookup for artist metadata on Apple Music (via the iTunes API) via artist ID.

            :param id: Artist ID.
            :param country_code: The country code of the country in which you want to conduct the lookup.
        """
		return await lookup_artist(id = id, country_code = country_code)



apple_music = AppleMusic()

print(f'[ServiceCatalogAPI] {component} initialized')
