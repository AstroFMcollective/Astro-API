from AstroAPI.components import *
from AstroAPI.media_services.music.youtube_music.components.generic import *
from AstroAPI.media_services.music.youtube_music.components.generic import ytm



async def lookup_artist(id: str = None, video_id: str = None, country_code: str = 'us') -> object:
	request = {'request': 'lookup_artist', 'id': id, 'video_id': video_id, 'country_code': country_code}
	start_time = current_unix_time_ms()
	
	try:
		try:
			if video_id == None and id == None:
				return Empty(
					service = service,
					request = {'request': request, 'id': id, 'video_id': video_id, 'country_code': country_code}
				)
			elif video_id != None and id == None:
				id = ytm.get_song(video_id)['videoDetails']['channelId']
			artist = ytm.get_artist(id)

			artist_url = f'https://music.youtube.com/channel/{artist['channelId']}'
			artist_id = artist['channelId']
			artist_name = artist['name']
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
			artist = ytm.get_song(video_id)['videoDetails']

			artist_url = f'https://music.youtube.com/channel/{artist['channelId']}'
			artist_id = artist['channelId']
			artist_name = artist['author']
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