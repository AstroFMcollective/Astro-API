from AstroAPI.ServiceCatalogAPI.components import *
from AstroAPI.ServiceCatalogAPI.media_services.music.youtube_music.components.generic import *
from AstroAPI.ServiceCatalogAPI.media_services.music.youtube_music.components.lookup.artist import lookup_artist
from AstroAPI.InternalComponents.CredentialsManager.media_services.youtube.credentials import youtube_credentials



async def lookup_song(id: str, country_code: str = 'us') -> object:
	# Initialize ytmusicapi
	# ytm = await youtube_credentials.initialize_ytmusicapi()
	# Prepare request metadata
	request = {'request': 'lookup_song', 'id': id, 'country_code': country_code}
	# Lookup JSON variable for later debugging
	lookup_json = None
	# Record the start time for processing time calculation
	start_time = current_unix_time_ms()



    # Try to perform the song lookup operation
	try:
		# Create an aiohttp session for making HTTP requests
		async with aiohttp.ClientSession() as session:
			# Prepare request data and YouTube Data API endpoint
			api_url = f'{api}/videos'
			api_params = {
				'id': id,
				'key': youtube_credentials.api_key,
				'part': 'snippet,contentDetails,statistics,topicDetails,snippet,status'
			}
			timeout = aiohttp.ClientTimeout(total = 30)

			# Make the GET request to the YouTube Data API
			async with session.get(url = api_url, params = api_params, timeout = timeout) as response:
				if response.status == 200:
					# Parse the JSON response if the request was successful
					song = await response.json()
					# Extract song details
					song_type = 'track'
					song_url = f'https://music.youtube.com/watch?v={song['items'][0]['id']}'
					song_id = song['items'][0]['id']
					song_title = song['items'][0]['snippet']['title']
					song_artists = [await lookup_artist(video_id = song_id, id = song['items'][0]['snippet']['channelId'])]

					# Build the cover object for the song
					thumbnails = song['items'][0]['snippet']['thumbnails']
					if thumbnails != {}:
						media_cover = Cover(
							service = service,
							media_type = 'track',
							title = song_title,
							artists = song_artists,
							hq_urls = thumbnails['maxres']['url'],
							lq_urls = thumbnails['high']['url'],
							meta = Meta(
								service = service,
								request = request,
								processing_time = 0,
								filter_confidence_percentage = 100.0,
								http_code = 200
							)
						)
					else:
						media_cover = None

					# Return the Song object with all extracted details
					return Song(
						service = service,
						type = song_type,
						urls = song_url,
						ids = song_id,
						title = song_title,
						artists = song_artists,
						collection = None,
						is_explicit = None,
						cover = media_cover,
						meta = Meta(
							service = service,
							request = request,
							processing_time = current_unix_time_ms() - start_time,
							filter_confidence_percentage = 100.0,
							http_code = response.status
						)
					)

				else:
					# Handle non-OK HTTP responses by returning an Error object
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

	# If sinister things happen
	except Exception as error:
		error = Error(
			service = service,
			component = component,
			error_msg = f'Error while looking up song {id} on {service}: {error}',
			meta = Meta(
				service = service,
				request = request,
				processing_time = current_unix_time_ms() - start_time,
				http_code = 500
			)
		)
		await log(error, [discord.File(fp = StringIO(json.dumps(lookup_json, indent = 4)), filename = f'{id}.json')])
		return error