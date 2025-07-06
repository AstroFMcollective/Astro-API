from AstroAPI.components import *
from AstroAPI.media_services.music.global_io.components.generic import *
from AstroAPI.media_services.music.global_io.components.generic import service as gservice, component as gcomponent

from AstroAPI.media_services.music.global_io.components.search.song import search_song



async def lookup_song(service: object, id: str, song_country_code: str = None, lookup_country_code: str = 'us') -> object:
	request = {'request': 'lookup_song', 'service': service.service, 'id': id, 'song_country_code': song_country_code, 'lookup_country_code': lookup_country_code}
	start_time = current_unix_time_ms()
	
	try:
		# Look up the song on its respectative service for its metadata
		song_reference = await service.lookup_song(id = id, country_code = song_country_code)

		# This would usually trigger had an error happened inside the lookup song function, so we can just return that empty or error object 
		if song_reference.type != 'track' and song_reference.type != 'single' and song_reference.type != 'music_video':
			return song_reference

		# Make the call to the Global Interface's song-searching function
		if song_reference.type == 'music_video': # All we do here is not use anything for the collection parameter, since music videos do not have that data
			song = await search_song(
				artists = [artist.name for artist in song_reference.artists],
				title = song_reference.title,
				is_explicit = song_reference.is_explicit,
				country_code = lookup_country_code,
				include_premade_media = [song_reference] # Include the media from the original call
			)
		else:
			song = await search_song(
				artists = [artist.name for artist in song_reference.artists],
				title = song_reference.title,
				song_type = song_reference.type,
				collection = song_reference.collection.title,
				is_explicit = song_reference.is_explicit,
				country_code = lookup_country_code,
				include_premade_media = [song_reference]
			)

		return song

	# If sinister things happen
	except Exception as error:
		error = Error(
			service = gservice,
			component = gcomponent,
			error_msg = f'Error when searching song: "{error}"',
			meta = Meta(
				service = gservice,
				request = request,
				http_code = 500,
				filter_confidence_percentage = {gservice: 0.0},
				processing_time = current_unix_time_ms() - start_time
			)
		)
		await log(error)
		return error