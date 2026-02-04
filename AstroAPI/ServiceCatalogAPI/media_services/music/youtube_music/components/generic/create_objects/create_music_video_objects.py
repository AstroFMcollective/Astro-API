from AstroAPI.InternalComponents.Legacy import *
from AstroAPI.ServiceCatalogAPI.components import *
from AstroAPI.ServiceCatalogAPI.media_services.music.apple_music.components.generic import *
from AstroAPI.ServiceCatalogAPI.media_services.music.youtube_music.components.lookup.artist import lookup_artist



async def create_music_video_objects(results: dict, request: dict, start_time: int, http_code: int):
	videos = []

	# Iterate over each video result
	for video in results:
		if video['resultType'] == 'video':
			mv_url = f'https://music.youtube.com/watch?v={video["videoId"]}'
			mv_id = video['videoId']
			mv_title = video['title']
			
			# If artist information is available in the result
			if 'artists' in video and video['artists'] != []:
				# Build a list of Artist objects from the result's artists
				mv_artists = [
					Artist(
						service = service,
						urls = f'https://music.youtube.com/channel/{artist["id"]}',
						ids = artist['id'],
						name = artist['name'],
						meta = Meta(
							service = service,
							request = request,
							processing_time = current_unix_time_ms() - start_time,
							http_code = 200,
							filter_confidence_percentage = 100.0
						)
					) for artist in video['artists']]
			else:
				# If no artist info, look up the artist using the video ID
				# Because apparently that's a thing that can happen????????
				# I should probably make an issue on the API's repo
				mv_artists = [await lookup_artist(video_id = video['videoId'], country_code = 'us')]

			# Create a Cover object for the music video
			mv_cover = Cover(
				service = service,
				media_type = 'song',
				title = mv_title,
				artists = mv_artists,
				hq_urls = video['thumbnails'][0]['url'],
				lq_urls = video['thumbnails'][len(video['thumbnails'])-1]['url'],
				meta = Meta(
					service = service,
					request = request,
					processing_time = current_unix_time_ms() - start_time,
					http_code = 200
				)
			)

			# Append a MusicVideo object to the videos list
			videos.append(MusicVideo(
				service = service,
				urls = mv_url,
				ids = mv_id,
				title = mv_title,
				artists = mv_artists,
				is_explicit = None,
				cover = mv_cover,
				meta = Meta(
					service = service,
					request = request,
					processing_time = current_unix_time_ms() - start_time,
					http_code = 200
				)
			))
						
	return videos