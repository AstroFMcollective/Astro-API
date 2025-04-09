from AstroAPI.components import *
from AstroAPI.media_services.music.apple_music.components.generic import *
import aiohttp



async def lookup_song(self, id: str, country_code: str = 'us') -> object:
	async with aiohttp.ClientSession() as session:
		request = {'request': 'lookup_song', 'id': id, 'country_code': country_code, 'url': f'https://music.apple.com/{country_code}/album/{id}'}
		api_url = f'https://itunes.apple.com/lookup'
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
				song_artists = await self.lookup_artist(id = song['artistId'], country_code = country_code)
				song_artists = [song_artists.name] if song_artists.type != 'error' else [song['artistName']]
				song_cover = song['artworkUrl100']
				song_is_explicit = not 'not' in song['trackExplicitness']
				song_collection = remove_feat(clean_up_collection_title(song['collectionName']))
				return Song(
					service = self.service,
					type = song_type,
					url = song_url,
					id = song_id,
					title = song_title,
					artists = song_artists,
					collection = song_collection,
					is_explicit = song_is_explicit,
					cover_url = song_cover,
					meta = Meta(
						service = self.service,
						request = request,
						processing_time = current_unix_time_ms() - start_time,
						filter_confidence_percentage = {self.service: 100.0},
						http_code = response.status
					)
				)

			else:
				error = Error(
					service = self.service,
					component = self.component,
					error_msg = "HTTP error when looking up song ID",
					meta = Meta(
						service = self.service,
						request = request,
						processing_time = current_unix_time_ms() - start_time,
						http_code = response.status
					)
				)
				await log(error)
				return error