from AstroAPI.components import *
from AstroAPI.media_services.knowledge.spotify.components.generic import *
from AstroAPI.media_services.music.spotify.components.search.song import search_song as search_song_music
from AstroAPI.media_services.knowledge.spotify.components.lookup.song import lookup_song as lookup_song_knowledge



async def search_song(artists: list, title: str, song_type: str = None, collection: str = None, is_explicit: bool = None, country_code: str = 'us') -> object:
	# Just a wrapper for search_song to get the song knowledge
	song = await search_song_music(artists, title, song_type, collection, is_explicit, country_code)
		
	illegal_results = ['empty_response', 'error']
	if song.type not in illegal_results:
		return await lookup_song_knowledge(song.ids[service], country_code)
	else:
		return song