from AstroAPI.ServiceCatalogAPI.components import *
from AstroAPI.InternalComponents.SystemMediaObjects import *
from AstroAPI.InternalComponents.Legacy import *
from AstroAPI.ServiceCatalogAPI.media_services.music.global_io.components.generic import *
from AstroAPI.ServiceCatalogAPI.media_services.music.global_io.components.generic import service as gservice, component as gcomponent

from AstroAPI.ServiceCatalogAPI.media_services.music.global_io.components.search.music_video import search_music_video as search_music_video_music



async def lookup_music_video(service: object, id: str, mv_country_code: str = None, lookup_country_code: str = 'us') -> object:
	# Prepare the request metadata
	request = {'request': 'lookup_song', 'service': service.service, 'id': id, 'mv_country_code': mv_country_code, 'lookup_country_code': lookup_country_code}
	# Record the start time for processing time calculation
	start_time = current_unix_time_ms()
	
	try:
		# Look up the song on its respectative service for its metadata
		if service == youtube_music:
			video_reference = await youtube_music.lookup_song(id = id, country_code = mv_country_code)
		else:
			video_reference = await service.lookup_music_video(id = id, country_code = mv_country_code)

		# This would usually trigger had an error happened inside the lookup song function, so we can just return that empty or error object 
		if video_reference.type != 'music_video':
			return video_reference

		# Make the call to the Global Interface's song-searching function
		music_video = await search_music_video_music(
			artists = [artist.name for artist in video_reference.artists],
			title = video_reference.title,
			is_explicit = video_reference.is_explicit,
			country_code = lookup_country_code,
			include_premade_media = [video_reference] # Include the media from the original call
		)

		# Replace the request dict of the search one with the lookup one
		music_video.meta.request = request

		return music_video

	# If sinister things happen
	except Exception as error:
		error = Error(
			service = gservice,
			component = gcomponent,
			error_msg = f'Error when searching music video: "{error}"',
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