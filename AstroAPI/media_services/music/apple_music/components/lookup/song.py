from AstroAPI.components import *
from AstroAPI.media_services.music.apple_music.components.generic import *
from AstroAPI.media_services.music.apple_music.components.lookup.artist import lookup_artist
from AstroAPI.media_services.music.apple_music.components.lookup.collection import lookup_collection

import aiohttp



async def lookup_song(id: str, country_code: str = 'us') -> object:
	async with aiohttp.ClientSession() as session:
		request = {'request': 'lookup_song', 'id': id, 'country_code': country_code, 'url': f'https://music.apple.com/{country_code}/album/{id}'}
		api_url = f'{api}/lookup'
		api_params = {
			'id': id,
			'country': country_code.lower()
		}
		timeout = aiohttp.ClientTimeout(total = 30)
		start_time = current_unix_time_ms()

		async with session.get(url = api_url, params = api_params, timeout = timeout) as response:
			if response.status == 200:
				song = await response.json(content_type = 'text/javascript')
				song = song['results'][0]
				song_type = 'track' if ' - Single' not in song['collectionName'] else 'single'
				song_url = song['trackViewUrl']
				song_id = song['trackId']
				song_title = song['trackName']
				song_artists = await lookup_artist(id = song['artistId'], country_code = country_code)
				song_artists = [song_artists]
				song_is_explicit = not 'not' in song['trackExplicitness']
				song_genre = song['primaryGenreName'] if 'primaryGenreName' in song else None
				song_cover = Cover(
					service = service,
					media_type = song_type,
					title = song_title,
					artists = song_artists,
					hq_urls = song['artworkUrl100'],
					lq_urls = song['artworkUrl30'],
					color_hex = None,
					meta = Meta(
						service = service,
						request = request,
						processing_time = current_unix_time_ms() - start_time,
						filter_confidence_percentage = {service: 100.0},
						http_code = response.status
					)
				)
				song_collection = await lookup_collection(id = song['collectionId'], country_code = country_code)
				return Song(
					service = service,
					type = song_type,
					urls = song_url,
					ids = song_id,
					title = song_title,
					artists = song_artists,
					collection = song_collection,
					is_explicit = song_is_explicit,
					cover = song_cover,
					genre = song_genre,
					meta = Meta(
						service = service,
						request = request,
						processing_time = current_unix_time_ms() - start_time,
						filter_confidence_percentage = {service: 100.0},
						http_code = response.status
					)
				)

			else:
				error = Error(
					service = service,
					component = component,
					error_msg = "HTTP error when looking up song ID",
					meta = Meta(
						service = service,
						request = request,
						processing_time = current_unix_time_ms() - start_time,
						http_code = response.status
					)
				)
				await log(error)
				return error