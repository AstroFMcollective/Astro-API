from AstroAPI.InternalComponents.Legacy import *
from AstroAPI.ServiceCatalogAPI.media_services.music.youtube_music.components.generic import *
from AstroAPI.InternalComponents.CredentialsManager.media_services.youtube.credentials import youtube_credentials
from AstroAPI.ServiceCatalogAPI.media_services.music.youtube_music.components.generic.is_kpop import is_kpop
from AstroAPI.ServiceCatalogAPI.media_services.music.youtube_music.components.generic.cleanup_mv_title import get_kpop_artist_name, devevoify



async def lookup_artist(id: str = None, video_id: str = None, country_code: str = 'us') -> object:
	# Build the request dictionary with provided parameters
	request = {'request': 'lookup_artist', 'id': id, 'video_id': video_id, 'country_code': country_code}
	# Lookup JSON variable for later debugging
	lookup_json = None
	# Record the start time for processing time calculation
	start_time = current_unix_time_ms()
	
	try:
		try:
			# If both video_id and id are None, return an Empty response
			if video_id == None and id == None:
				return Empty(
					service = service,
					request = {'request': request, 'id': id, 'video_id': video_id, 'country_code': country_code}
				)
			# If video_id is provided but id is not, extract artist id from the song's video details
			elif video_id != None and id == None:
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
							lookup_json = await response.json()
							id = lookup_json['items'][0]['snippet']['channelId']
			# Lookup artist information using the artist id
			artist = youtube_credentials.ytmusicapi.get_artist(id)
			lookup_json = id # Save the JSON for future debugging if necessary


			artist_url = f'https://music.youtube.com/channel/{artist["channelId"]}'
			artist_id = artist['channelId']
			artist_name = artist['name']

			# Return an Artist object with the gathered information and metadata
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
			# If the above fails, fallback to extracting artist info from the song's video details
			async with aiohttp.ClientSession() as session:
				# Prepare request data and YouTube Data API endpoint
					api_url = f'{api}/videos'
					api_params = {
						'id': video_id,
						'key': youtube_credentials.api_key,
						'part': 'snippet,contentDetails,statistics,topicDetails,snippet,status'
					}
					timeout = aiohttp.ClientTimeout(total = 30)

					# Make the GET request to the YouTube Data API
					async with session.get(url = api_url, params = api_params, timeout = timeout) as response:
						if response.status == 200:
							# Parse the JSON response if the request was successful
							lookup_json = await response.json()

			song = lookup_json['items'][0]

			artist_url = f'https://music.youtube.com/channel/{song['snippet']['channelId']}'
			artist_id = song['snippet']['channelId']
			if is_kpop(song):
				artist_name = get_kpop_artist_name(song)
			else:
				artist_name = devevoify(song)

			# Return an Artist object with the gathered information and metadata
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

	# If sinister things happen
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
		await log(error, [discord.File(fp = StringIO(json.dumps(lookup_json, indent = 4)), filename = f'{id}.json')])
		return error