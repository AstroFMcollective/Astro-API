from AstroAPI.InternalComponents.Legacy import *
from AstroAPI.ServiceCatalogAPI.components import *
from AstroAPI.ServiceCatalogAPI.media_services.music.apple_music.components.generic import *



async def create_music_video_objects(json_response: dict, request: dict, start_time: int, http_code: int):
	videos = []

	# Iterate over each video in the results
	for video in json_response['results']:
		mv_url = video['trackViewUrl']
		mv_id = video['trackId']
		mv_preview = video['previewUrl']
		mv_title = video['trackName']
		# Determine if the video is explicit
		mv_is_explicit = not 'not' in video['trackExplicitness'] # pingu be like
		mv_genre = video['primaryGenreName'] if 'primaryGenreName' in video else None

		# Create Artist objects for each artist in the video
		mv_artists = [
			Artist(
				service = service,
				urls = video['artistViewUrl'] if 'artistViewUrl' in video else f'https://music.apple.com/{request['country_code']}/artist/{video['artistId']}', # Additional edge case if artistViewUrl is missing... this API is so weird
				ids = video['artistId'],
				name = artist,
				meta = Meta(
					service = service,
					request = request,
					processing_time = current_unix_time_ms() - start_time,
					filter_confidence_percentage = 100.0,
					http_code = http_code
				)
			) for artist in split_artists(video['artistName'])
		]

		# Create a Cover object for the music video thumbnail
		mv_thumbnail = Cover(
			service = service,
			media_type = 'music_video',
			title = mv_title,
			artists = mv_artists,
			hq_urls = video['artworkUrl100'],
			lq_urls = video['artworkUrl60'],
			meta = Meta(
				service = service,
				request = request,
				processing_time = current_unix_time_ms() - start_time,
				filter_confidence_percentage = {service: 100.0},
				http_code = http_code
			)
		)

		# Create a MusicVideo object and add it to the list
		videos.append(MusicVideo(
			service = service,
			urls = mv_url,
			ids = mv_id,
			previews = mv_preview,
			title = mv_title,
			artists = mv_artists,
			is_explicit = mv_is_explicit,
			cover = mv_thumbnail,
			genre = mv_genre,
			meta = Meta(
				service = service,
				request = request,
				processing_time = current_unix_time_ms() - start_time,
				filter_confidence_percentage = {service: 100.0},
				http_code = http_code
			)
		))
						
	return videos