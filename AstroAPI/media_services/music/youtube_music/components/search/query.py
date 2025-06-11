from AstroAPI.components import *
from AstroAPI.media_services.music.youtube_music.components.generic import *
from AstroAPI.media_services.music.youtube_music.components.lookup.artist import lookup_artist
from AstroAPI.media_services.music.youtube_music.components.generic import ytm



async def search_query(query: str, country_code: str = 'us') -> object: # TODO: Dovrši
	try:
		request = {'request': 'search_query', 'query': query, 'country_code': country_code}
		start_time = current_unix_time_ms()
		results = ytm.search(
			query = query
		)
		result = results[0]
		result_type = result['resultType']

		if result_type == 'song':
			result_artists = [
				Artist(
					service = service,
					urls = f'https://music.youtube.com/channel/{artist["id"]}',
					ids = artist['id'],
					name = artist['name'],
					meta = Meta(
						service = service,
						request = request,
						processing_time = current_unix_time_ms() - start_time,
						filter_confidence_percentage = {service: 100.0},
						http_code = 200
					)
				) for artist in result['artists']
			]

			result_cover = Cover(
				service = service,
				media_type = 'track',
				title = result['title'],
				artists = result_artists,
				hq_urls = result['thumbnails'][0]['url'],
				lq_urls = result['thumbnails'][len(result['thumbnails'])-1]['url'],
				meta = Meta(
					service = service,
					request = request,
					processing_time = current_unix_time_ms() - start_time,
					filter_confidence_percentage = {service: 100.0},
					http_code = 200
				)
			)

			return Song(
				service = service,
				type = 'track',
				urls = f'https://music.youtube.com/watch?v={result['videoId']}',
				ids = result['videoId'],
				title = result['title'],
				artists = result_artists,
				collection = None,
				is_explicit = None,
				cover = result_cover,
				meta = Meta(
					service = service,
					request = request,
					processing_time = current_unix_time_ms() - start_time,
					filter_confidence_percentage = {service: 100.0},
					http_code = 200
				)
			)
		elif result_type == 'album':
			result_artists = [
				Artist(
					service = service,
					urls = f'https://music.youtube.com/playlist?list={result['playlistId']}',
					ids = 0, # ytmusicapi does not provide artist IDs for albums via query search
					name = artist['name'],
					meta = Meta(
						service = service,
						request = request,
						processing_time = current_unix_time_ms() - start_time,
						filter_confidence_percentage = {service: 100.0},
						http_code = 200
					)
				) for artist in result['artists']
			]

			result_cover = Cover(
				service = service,
				media_type = 'track',
				title = result['title'],
				artists = result_artists,
				hq_urls = result['thumbnails'][0]['url'],
				lq_urls = result['thumbnails'][len(result['thumbnails'])-1]['url'],
				meta = Meta(
					service = service,
					request = request,
					processing_time = current_unix_time_ms() - start_time,
					filter_confidence_percentage = {service: 100.0},
					http_code = 200
				)
			)

			return Collection(
				service = service,
				type = 'album',
				urls = f'https://music.youtube.com/playlist?list={result['playlistId']}',
				ids = result['playlistId'],
				title = result['title'],
				artists = result_artists,
				release_year = None,
				cover = result_cover,
				meta = Meta(
					service = service,
					request = request,
					processing_time = current_unix_time_ms() - start_time,
					filter_confidence_percentage = {service: 100.0},
					http_code = 200
				)
			)
		elif result_type == 'video':
			result_artists = [
				Artist(
					service = service,
					urls = f'https://music.youtube.com/channel/{artist["id"]}',
					ids = artist['id'],
					name = artist['name'],
					meta = Meta(
						service = service,
						request = request,
						processing_time = current_unix_time_ms() - start_time,
						filter_confidence_percentage = {service: 100.0},
						http_code = 200
					)
				) for artist in result['artists']
			]

			result_cover = Cover(
				service = service,
				media_type = 'track',
				title = result['title'],
				artists = result_artists,
				hq_urls = result['thumbnails'][0]['url'],
				lq_urls = result['thumbnails'][len(result['thumbnails'])-1]['url'],
				meta = Meta(
					service = service,
					request = request,
					processing_time = current_unix_time_ms() - start_time,
					filter_confidence_percentage = {service: 100.0},
					http_code = 200
				)
			)

			return MusicVideo(
				service = service,
				urls = f'https://music.youtube.com/watch?v={result['videoId']}',
				ids = result['videoId'],
				title = remove_music_video_declaration(result['title']),
				artists = result_artists,
				is_explicit = None,
				cover = result_cover,
				meta = Meta(
					service = service,
					request = request,
					processing_time = current_unix_time_ms() - start_time,
					filter_confidence_percentage = {service: 100.0},
					http_code = 200
				)
			)
		else:
			empty_response = Empty(
				service = service,
				meta = Meta(
					service = service,
					request = request,
					processing_time = current_unix_time_ms() - start_time,
					http_code = 204
				)
			)
			await log(empty_response)
			return empty_response

	except Exception as msg:
		error = Error(
			service = service,
			component = component,
			error_msg = f'Error when doing general query search: "{msg}"',
			meta = Meta(
				service = service,
				request = request,
				processing_time = current_unix_time_ms() - start_time,
				http_code = 500
			)
		)
		await log(error)
		return error