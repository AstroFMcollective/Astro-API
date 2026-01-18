from AstroAPI.ServiceCatalogAPI.components import *
from AstroAPI.InternalComponents.SystemMediaObjects import *
from AstroAPI.InternalComponents.Legacy import *
from .components.generic import *

from .components.search.song import search_song
from .components.search.collection import search_collection
from .components.search.query import search_query
from .components.lookup.song import lookup_song
from .components.lookup.collection import lookup_collection
from .components.lookup.artist import lookup_artist



class Deezer:
	def __init__(self):
		self.service = service
		self.component = component

	async def search_song(self, artists: list, title: str, song_type: str = None, collection: str = None, is_explicit: bool = None, country_code: str = 'us') -> Song | Empty | Error:
		"""
			# Deezer Song Music Search

			Search for song metadata on Deezer.

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
			# Deezer Collection Music Search

			Search for collection metadata on Deezer.

			:param artists: A list of artist names on the song that you're attempting to search.
			:param title: Song title.
			:param year: The name of the collection (album, EP) the song is a part of.
			:param country_code: The country code of the country in which you want to conduct the search.
		"""
		return await search_collection(artists = artists, title = title, year = year, country_code = country_code)
		
	async def search_query(self, query: str, filter_for_best_match: bool = True, media_types: list = None, is_explicit: bool = None, country_code: str = 'us') -> Query | Song | Collection | Empty | Error:
		"""
			# Deezer Query Music Search

			Search for media metadata on Deezer via query.

			:param query: Your search query.
			:param filter_for_best_match: Whether you want an Astro-style single best match, or all search results regardless of content as a response.
			:param media_types: Which media types you want to be included in the response.
			:param is_explicit: Whether the media is explicit or not.
			:param country_code: The country code of the country in which you want to conduct the search.
		"""
		return await search_query(query = query, filter_for_best_match = filter_for_best_match, media_types = media_types, is_explicit = is_explicit, country_code = country_code)

	async def lookup_song(self, id: str, country_code: str = 'us') -> Song | Empty | Error:
		"""
			# Deezer Song Music Lookup

			Lookup for song metadata on Deezer via song ID.

			:param id: Song ID.
			:param country_code: The country code of the country in which you want to conduct the lookup.
		"""
		return await lookup_song(id = id, country_code = country_code)
	
	async def lookup_collection(self, id: str, country_code: str = 'us') -> Collection | Empty | Error:
		"""
			# Deezer Collection Music Lookup

			Lookup for collection metadata on Deezer via collection ID.

			:param id: Collection ID.
			:param country_code: The country code of the country in which you want to conduct the lookup.
		"""
		return await lookup_collection(id = id, country_code = country_code)
	
	async def lookup_artist(self, id: str, country_code: str = 'us') -> Song | Empty | Error:
		"""
			# Deezer Artist Music Lookup

			Lookup for artist metadata on Deezer via artist ID.

			:param id: Artist ID.
			:param country_code: The country code of the country in which you want to conduct the lookup.
		"""
		return await lookup_artist(id = id, country_code = country_code)
	

	
deezer = Deezer()

print(f'[ServiceCatalogAPI] {component} initialized')
