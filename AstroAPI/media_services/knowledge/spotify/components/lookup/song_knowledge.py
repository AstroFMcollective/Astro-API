from AstroAPI.components import *
from AstroAPI.components.service_tokens.spotify.token import spotify_token
from AstroAPI.media_services.knowledge.spotify.components.generic import *
from AstroAPI.media_services.music.spotify.components.lookup.song import lookup_song
import aiohttp



async def lookup_song_knowledge(id: str, country_code: str = 'us') -> object:
	request = {'request': 'lookup_song_knowledge', 'id': id, 'country_code': country_code}
	start_time = current_unix_time_ms()
	
	# Try to perform the song knowledge lookup operation
	try:
		# Create an aiohttp session for HTTP requests
		async with aiohttp.ClientSession() as session:
			# Prepare request data and Spotify API endpoint
			api_url = f'{api}/audio-features/{id}'
			api_params = {
				'market': country_code.upper(),
			}
			api_headers = {'Authorization': f'Bearer {await spotify_token.get_token()}'}
			timeout = aiohttp.ClientTimeout(total = 30)

			# Lookup general song data using internal music function
			song_general_data = await lookup_song(id, country_code)

			illegal_results = ['empty_response', 'error']
			# If the song lookup was successful, extract details
			if song_general_data not in illegal_results:
				song_type = song_general_data.type
				song_url = song_general_data.urls
				song_id = song_general_data.ids
				song_title = song_general_data.title
				song_artists = song_general_data.artists
				song_cover = song_general_data.cover
				song_is_explicit = song_general_data.is_explicit
				song_collection = song_general_data.collection

				# Fetch audio features from Spotify API
				async with session.get(url = api_url, headers = api_headers, timeout = timeout, params = api_params) as response:
					if response.status == 200:
						song = await response.json()
						song_bpm = song['bpm']
						song_key = song['key']
						song_time_signature = song['time_signature']
					else:
						song_bpm = None
						song_key = None
						song_time_signature = None

				# Return a Knowledge object with all song details
				return Knowledge(
					service = service,
					media_type = song_type,
					urls = song_url,
					ids = song_id,
					title = song_title,
					artists = song_artists,
					collection = song_collection,
					cover = song_cover,
					is_explicit = song_is_explicit,
					bpm = song_bpm,
					key = song_key,
					length = None,
					time_signature = song_time_signature,
					meta = Meta(
						service = service,
						request = request,
						processing_time = current_unix_time_ms() - start_time,
						filter_confidence_percentage = {service: 100.0},
						http_code = response.status
					)
				)
			
			else:
				# If song lookup failed, return an Error object and log it
				error = Error(
					service = service,
					component = component,
					error_msg = f"Error when looking up song knowledge: {song_general_data.error_msg}",
					meta = Meta(
						service = service,
						request = request,
						processing_time = current_unix_time_ms() - start_time,
						http_code = song_general_data.meta.http_code,
					)
				)
				await log(error)
				return error

	# If sinister things happen
	except Exception as error:
		error = Error(
			service = service,
			component = component,
			error_msg = f'Error when looking up collection: "{error}"',
			meta = Meta(
				service = service,
				request = request,
				http_code = 500,
				processing_time = {service: current_unix_time_ms() - start_time}
			)
		)
		await log(error)
		return error