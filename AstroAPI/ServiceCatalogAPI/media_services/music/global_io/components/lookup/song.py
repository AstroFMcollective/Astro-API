from AstroAPI.ServiceCatalogAPI.components import *
from AstroAPI.ServiceCatalogAPI.media_services.music.global_io.components.generic import *
from AstroAPI.ServiceCatalogAPI.media_services.music.global_io.components.generic import service as gservice, component as gcomponent

from AstroAPI.ServiceCatalogAPI.media_services.music.global_io.components.search.song import search_song as search_song_music



async def lookup_song(service: object, id: str, song_country_code: str = None, lookup_country_code: str = 'us') -> object:
	# Prepare the request metadata
	request = {'request': 'lookup_song', 'service': service.service, 'id': id, 'song_country_code': song_country_code, 'lookup_country_code': lookup_country_code}
	# Record the start time for processing time calculation
	start_time = current_unix_time_ms()
	
	try:
		# Look up the song on its respectative service for its metadata
		song_reference = await service.lookup_song(id = id, country_code = song_country_code)

		legal_results = ['track', 'single', 'music_video', 'knowledge']
		compatible_results = ['track', 'single', 'music_video']

		# This would usually trigger had an error happened inside the lookup song function, so we can just return that empty or error object 
		if song_reference.type not in legal_results:
			return song_reference
		
		# Rudimentary check to see if the song object reference has a collection
		# Certain service API-s do not provide a collection for objects, and music videos (which have compatible metadata) do not have a collection in any case
		if 'collection' in song_reference.json:
			if song_reference.collection is not None:
				song_reference_collection_title = song_reference.collection.title
			else: 
				song_reference_collection_title = None
		else:
			song_reference_collection_title = None

		# Make the call to the Global Interface's song-searching function
		song = await search_song_music(
			artists = [artist.name for artist in song_reference.artists],
			title = song_reference.title,
			song_type = song_reference.type if song_reference.type != 'knowledge' else song_reference.media_type,
			collection = song_reference_collection_title,
			is_explicit = song_reference.is_explicit,
			country_code = lookup_country_code,
			include_premade_media = [song_reference] if song_reference.type in compatible_results else []  # Include the media from the original call unless it's a knowledge result
		)

		# Replace the request dict of the search one with the lookup one
		song.meta.request = request
		song.meta.regenerate_json()
		song.regenerate_json()

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