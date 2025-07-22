from ServiceCatalogAPI.components import *
from ServiceCatalogAPI.media_services.music.youtube_music.components.generic import *
from ServiceCatalogAPI.media_services.music.youtube_music.components.generic import ytm



async def lookup_artist(id: str = None, video_id: str = None, country_code: str = 'us') -> object:
	# Build the request dictionary with provided parameters
	request = {'request': 'lookup_artist', 'id': id, 'video_id': video_id, 'country_code': country_code}
	# Record the start time for processing time calculation
	start_time = current_unix_time_ms()
	
	try:
		try:
			# If both video_id and id are None, return an Empty response
			if video_id == None and id == None:
				return Empty(
					service = service,
					request = {'request': request, 'id': id, 'video_id': video_id, 'country_code': country_code}
				)
			# If video_id is provided but id is not, extract artist id from the song's video details
			elif video_id != None and id == None:
				id = ytm.get_song(video_id)['videoDetails']['channelId']
			# Lookup artist information using the artist id
			artist = ytm.get_artist(id)

			artist_url = f'https://music.youtube.com/channel/{artist["channelId"]}'
			artist_id = artist['channelId']
			artist_name = artist['name']

			# Return an Artist object with the gathered information and metadata
			return Artist(
				service = service,
				urls = artist_url,
				ids = artist_id,
				name = artist_name,
				meta = Meta(
					service = service,
					request = request,
					processing_time = current_unix_time_ms() - start_time,
					filter_confidence_percentage = {service: 100.0},
					http_code = 200
				)
			)
		except:
			# If the above fails, fallback to extracting artist info from the song's video details
			artist = ytm.get_song(video_id)['videoDetails']

			artist_url = f'https://music.youtube.com/channel/{artist["channelId"]}'
			artist_id = artist['channelId']
			artist_name = artist['author']

			# Return an Artist object with the gathered information and metadata
			return Artist(
				service = service,
				urls = artist_url,
				ids = artist_id,
				name = artist_name,
				meta = Meta(
					service = service,
					request = request,
					processing_time = current_unix_time_ms() - start_time,
					filter_confidence_percentage = {service: 100.0},
					http_code = 200
				)
			)

	# If sinister things happen
	except Exception as msg:
		error = Error(
			service = service,
			component = component,
			error_msg = f'Error when looking up artist: "{msg}"',
			meta = Meta(
				service = service,
				request = request,
				processing_time = current_unix_time_ms() - start_time,
				http_code = 500
			)
		)
		await log(error)
		return error