from io import StringIO
from ServiceCatalogAPI.components import *
from ServiceCatalogAPI.media_services.music.youtube_music.components.generic import *
from ServiceCatalogAPI.media_services.music.youtube_music.components.lookup.artist import lookup_artist
from ServiceCatalogAPI.media_services.music.youtube_music.components.generic import ytm



async def lookup_song(id: str, country_code: str = 'us') -> object:
	# List of allowed music video types
	allowed_video_types = [
		'MUSIC_VIDEO_TYPE_ATV',
		'MUSIC_VIDEO_TYPE_OMV',
		'MUSIC_VIDEO_TYPE_OFFICIAL_SOURCE_MUSIC'
	]
	# Prepare request metadata
	request = {'request': 'lookup_song', 'id': id, 'country_code': country_code}
	# Record the start time for processing time calculation
	start_time = current_unix_time_ms()

	try:
		# Fetch song data from YouTube Music API
		song_data = ytm.get_song(id)
		# Extract video details from the response
		if 'videoDetails' not in song_data:
			save_json(song_data)
		song = song_data['videoDetails']

		# Check if the song has a music video type
		if 'musicVideoType' in song:
			# Check if the music video type is allowed (filter user-generated content)
			if song['musicVideoType'] in allowed_video_types:
				song_url = f'https://music.youtube.com/watch?v={song['videoId']}'
				song_id = song['videoId']
				song_title = song['title']
				song_artists = [await lookup_artist(video_id = song['videoId'])]
				thumbnails = song_data['microformat']['microformatDataRenderer']['thumbnail']['thumbnails']
				song_cover = Cover(
					service = service,
					media_type = 'track' if song['musicVideoType'] == 'MUSIC_VIDEO_TYPE_ATV' else 'music_video',
					title = song_title,
					artists = song_artists,
					hq_urls = thumbnails[0]['url'],
					lq_urls = thumbnails[len(thumbnails)-1]['url'],
					meta = Meta(
						service = service,
						request = request,
						processing_time = current_unix_time_ms() - start_time,
						filter_confidence_percentage = {service: 100.0},
						http_code = 200
					)
				)
				# If the video type is an audio track video
				if song['musicVideoType'] == 'MUSIC_VIDEO_TYPE_ATV':
					# Return a Song object with all relevant metadata
					return Song(
						service = service,
						type = 'track',
						urls = song_url,
						ids = song_id,
						title = song_title,
						artists = song_artists,
						collection = None,
						is_explicit = None,
						cover = song_cover,
						meta = Meta(
							service = service,
							request = request,
							processing_time = current_unix_time_ms() - start_time,
							filter_confidence_percentage = {service: 100.0},
							http_code = 200
						)
					)

				else:
					song_title = remove_music_video_declaration(song_title)
					# Return a MusicVideo object with all relevant metadata
					return MusicVideo(
						service = service,
						urls = song_url,
						ids = song_id,
						title = song_title,
						artists = song_artists,
						is_explicit = None,
						cover = song_cover,
						meta = Meta(
							service = service,
							request = request,
							processing_time = current_unix_time_ms() - start_time,
							filter_confidence_percentage = {service: 100.0},
							http_code = 200
						)
					)
				
			else:
				# If the music video type is not allowed, return an Empty object
				# DO NOT LOG THIS EVER UNLESS IT'S IN TESTING
				# THAT WILL LOG USER GENERATED CONTENT, COMPROMISING USER PRIVACY
				return Empty(
					service = service,
					meta = Meta(
						service = service,
						request = request,
						processing_time = current_unix_time_ms() - start_time,
						http_code = 204
					)
				)
		else:
			# If there is no music video type, return an Empty object
			# DO NOT LOG THIS EVER UNLESS IT'S IN TESTING
			# THAT WILL LOG USER GENERATED CONTENT, COMPROMISING USER PRIVACY
			return Empty(
				service = service,
				meta = Meta(
					service = service,
					request = request,
					processing_time = current_unix_time_ms() - start_time,
					http_code = 204
				)
			)

	# If sinister things happen
	except Exception as error:
		error = Error(
			service = service,
			component = component,
			error_msg = f'Error while looking up song {id} on {service}: {error}',
			meta = Meta(
				service = service,
				request = request,
				processing_time = current_unix_time_ms() - start_time,
				http_code = 500
			)
		)
		song_data = ytm.get_song(id)
		await log(error)
		return error