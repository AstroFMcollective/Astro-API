from AstroAPI.components import *
from AstroAPI.media_services.music.youtube_music.components.generic import *
from AstroAPI.media_services.music.youtube_music.components.lookup.artist import lookup_artist
from AstroAPI.media_services.music.youtube_music.components.generic import ytm



async def search_music_video(artists: list, title: str, is_explicit: bool = None, country_code: str = 'us') -> object:
	request = {'request': 'search_music_video', 'artists': artists, 'title': title, 'is_explicit': is_explicit, 'country_code': country_code}
	start_time = current_unix_time_ms()

	try:
		artists = [optimize_for_search(artist) for artist in artists]
		title = optimize_for_search(replace_with_ascii(title).lower())
		
		videos = []
		results = ytm.search(
			query = f'{artists[0]} {title}',
			filter = 'videos'
		)

		for video in results:
			mv_url = f'https://music.youtube.com/watch?v={video['videoId']}'
			mv_id = video['videoId']
			mv_title = video['title']
			
			if video['artists'] != []:
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
				mv_artists = [await lookup_artist(video_id = video['videoId'], country_code = country_code)]


			mv_cover = Cover(
				service = service,
				media_type = 'song',
				title = mv_title,
				artists	= mv_artists,
				hq_urls = video['thumbnails'][0]['url'],
				lq_urls = video['thumbnails'][len(video['thumbnails'])-1]['url'],
				meta = Meta(
					service = service,
					request = request,
					processing_time = current_unix_time_ms() - start_time,
					http_code = 200
				)
			)

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
		return await filter_mv(service = service, query_request = request, videos = videos, query_artists = artists, query_title = title, query_is_explicit = is_explicit, query_country_code = country_code)

	except Exception as msg:
		error = Error(
			service = service,
			component = component,
			error_msg = f'Error when searching for music video: "{msg}"',
			meta = Meta(
				service = service,
				request = request,
				processing_time = current_unix_time_ms() - start_time,
			)
		)
		await log(error)
		return error