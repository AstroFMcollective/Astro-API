from AstroAPI.ServiceCatalogAPI.components import *
from AstroAPI.InternalComponents.SystemMediaObjects import *
from AstroAPI.InternalComponents.Legacy import *
from AstroAPI.ServiceCatalogAPI.media_services.music.youtube_music.components.generic import *
from AstroAPI.ServiceCatalogAPI.media_services.music.youtube_music.components.lookup.artist import lookup_artist
from AstroAPI.ServiceCatalogAPI.media_services.music.youtube_music.components.generic.classify import classify
from AstroAPI.ServiceCatalogAPI.media_services.music.youtube_music.components.generic.cleanup_mv_title import cleanup_mv_title
from AstroAPI.InternalComponents.CredentialsManager.media_services.youtube.credentials import youtube_credentials



async def lookup_song(id: str, country_code: str = 'us') -> object:
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
				lookup_json = await response.json()
				if response.status == 200:
					# Parse the JSON response if the request was successful
					if lookup_json['items'] != []: # Check if the items list is empty, effectively an empty response
						song = lookup_json['items'][0]

						# Approximate whether the given data was of a song, music video or regular YouTube video
						# If the approximaton concludes as a song:
						if classify(song) == 'song':
							# Extract song details
							song_type = 'track'
							song_url = f'https://music.youtube.com/watch?v={song['id']}'
							song_id = song['id']
							song_title = song['snippet']['title']
							song_artists = [await lookup_artist(video_id = song_id, id = song['snippet']['channelId'])]

							# Build the cover object for the song
							thumbnails = song['snippet']['thumbnails']
							if thumbnails != {}:
								media_cover = Cover(
									service = service,
									media_type = 'track',
									title = song_title,
									artists = song_artists,
									hq_urls = thumbnails[list(thumbnails.keys())[-1]]['url'],
									lq_urls = thumbnails[list(thumbnails.keys())[0]]['url'],
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

						# If the approximaton concludes as a music video:
						elif classify(song) == 'music_video':
							# Extract music video details
							mv_url = f'https://music.youtube.com/watch?v={song['id']}'
							mv_id = song['id']
							mv_title = remove_feat(cleanup_mv_title(song))
							mv_artists = [await lookup_artist(video_id = mv_id, id = song['snippet']['channelId'])]

							# Build the cover object for the music video
							thumbnails = song['snippet']['thumbnails']
							if thumbnails != {}:
								media_cover = Cover(
									service = service,
									media_type = 'music_video',
									title = mv_title,
									artists = mv_artists,
									hq_urls = thumbnails[list(thumbnails.keys())[-1]]['url'],
									lq_urls = thumbnails[list(thumbnails.keys())[0]]['url'],
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

							# Return the music video object with all extracted details
							return MusicVideo(
								service = service,
								urls = mv_url,
								ids = mv_id,
								title = mv_title,
								artists = mv_artists,
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
							# If the approximaton concludes as a regular video, return an empty object
							# DO NOT LOG THIS EVER UNLESS IT'S IN TESTING
							# THAT WILL LOG USER GENERATED CONTENT, COMPROMISING USER PRIVACY
							return Empty(
								service = service,
								meta = Meta(
									service = service,
									request = request,
									processing_time = current_unix_time_ms() - start_time,
									http_code = 204
								)
							)
					
					else: # If the items list is empty, return an empty object
						return Empty(
							service = service,
							meta = Meta(
								service = service,
								request = request,
								processing_time = current_unix_time_ms() - start_time,
								http_code = 204
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