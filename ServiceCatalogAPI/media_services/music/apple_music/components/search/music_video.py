from ServiceCatalogAPI.components import *
from ServiceCatalogAPI.media_services.music.apple_music.components.generic import *

import aiohttp



async def search_music_video(artists: list, title: str, is_explicit: bool = None, country_code: str = 'us') -> object:
	request = {'request': 'search_music_video', 'artists': artists, 'title': title, 'is_explicit': is_explicit, 'country_code': country_code}
	start_time = current_unix_time_ms()

	try:
		async with aiohttp.ClientSession() as session:
			artists = [optimize_for_search(artist) for artist in artists]
			title = optimize_for_search(replace_with_ascii(title).lower())
				
			videos = []
			api_url = f'{api}/search'
			api_params = {
				'term': f'{artists[0]} "{title}"',
				'entity': 'musicVideo',
				'limit': 200,
				'country': country_code.lower()
			}
			timeout = aiohttp.ClientTimeout(total = 30)

			async with session.get(url = api_url, timeout = timeout, params = api_params) as response:
				if response.status == 200:
					json_response = await response.json(content_type = 'text/javascript')

					for video in json_response['results']:
						mv_url = video['trackViewUrl']
						mv_id = video['trackId']
						mv_title = video['trackName']
						mv_is_explicit = not 'not' in video['trackExplicitness']
						mv_genre = video['primaryGenreName'] if 'primaryGenreName' in video else None

						mv_artists = [
							Artist(
								service = service,
								urls = video['artistViewUrl'],
								ids = video['artistId'],
								name = artist,
								meta = Meta(
									service = service,
									request = request,
									processing_time = current_unix_time_ms() - start_time,
									filter_confidence_percentage = 100.0,
									http_code = response.status
								)
							) for artist in split_artists(video['artistName'])
						]

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
								http_code = response.status
							)
						)

						videos.append(MusicVideo(
							service = service,
							urls = mv_url,
							ids = mv_id,
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
								http_code = response.status
							)
						))
					return await filter_mv(service = service, query_request = request, videos = videos, query_artists = artists, query_title = title, query_is_explicit = is_explicit, query_country_code = country_code)
					
				else:
					error = Error(
						service = service,
						component = component,
						error_msg = "HTTP error when searching for music video",
						meta = Meta(
							service = service,
							request = request,
							processing_time = current_unix_time_ms() - start_time,
							filter_confidence_percentage = 0.0,
							http_code = response.status
						)
					)
					await log(error)
					return error

	except Exception as error:
		error = Error(
			service = service,
			component = component,
			error_msg = f'Error when looking up collection: "{error}"',
			meta = Meta(
				service = service,
				request = request,
				http_code = 500,
				filter_confidence_percentage = 0.0,
				processing_time = {service: current_unix_time_ms() - start_time}
				
			)
		)
		await log(error)
		return error
		  