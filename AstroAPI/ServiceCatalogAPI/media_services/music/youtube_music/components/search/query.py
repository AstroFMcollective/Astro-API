from AstroAPI.ServiceCatalogAPI.components import *
from AstroAPI.InternalComponents.SystemMediaObjects import *
from AstroAPI.InternalComponents.Legacy import *
from AstroAPI.ServiceCatalogAPI.media_services.music.youtube_music.components.generic import *
from AstroAPI.InternalComponents.CredentialsManager.media_services.youtube.credentials import youtube_credentials



async def search_query(query: str, filter_for_best_match: bool = True, media_types: list = None, is_explicit: bool = None, country_code: str = 'us') -> object:
	# Prepare the request dictionary with query details
	request = {'request': 'search_query', 'query': query, 'country_code': country_code}
	# Lookup JSON variable for later debugging
	lookup_json = None
	# Record the start time for processing time calculation
	start_time = current_unix_time_ms()

	try:
		# Perform the search using ytm (YouTube Music API wrapper)
		results = youtube_credentials.ytmusicapi.search(
			query = query
		)
		# Save the JSON for future debugging if necessary
		lookup_json = results
		
		# Define allowed result types based on media_types parameter
		allowed_types = []
		if media_types:
			if 'track' in media_types or 'song' in media_types:
				allowed_types.append('song')
			if 'album' in media_types or 'collection' in media_types:
				allowed_types.append('album')
			if 'music_video' in media_types or 'video' in media_types:
				allowed_types.append('video')
		else:
			# If no media types specified, allow all standard types
			allowed_types = ['song', 'album', 'video']

		if filter_for_best_match:
			# Iterate through results to find the first one that matches the allowed media types
			result = None
			for potential_result in results:
				if potential_result['resultType'] in allowed_types:
					result = potential_result
					break
			
			# If a valid result was found, process it
			if result:
				result_type = result['resultType']
				
				if result_type == 'song':
					# Build a list of Artist objects for the song's artists
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

					# Create a Cover object for the song
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

					# Return a Song object with all relevant details
					return Song(
						service = service,
						type = 'track',
						urls = f'https://music.youtube.com/watch?v={result["videoId"]}',
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
					# Build a list of Artist objects for the album's artists
					result_artists = [
						Artist(
							service = service,
							urls = f'https://music.youtube.com/playlist?list={result["playlistId"]}',
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

					# Create a Cover object for the album
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

					# Return a Collection object representing the album
					return Collection(
						service = service,
						type = 'album',
						urls = f'https://music.youtube.com/playlist?list={result["playlistId"]}',
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
					# Build a list of Artist objects for the video's artists
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

					# Create a Cover object for the video
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

					# Return a MusicVideo object with all relevant details
					return MusicVideo(
						service = service,
						urls = f'https://music.youtube.com/watch?v={result["videoId"]}',
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
			
			# If no valid result type found, fall through to empty response
			empty_response = Empty(
				service = service,
				meta = Meta(
					service = service,
					request = request,
					processing_time = current_unix_time_ms() - start_time,
					filter_confidence_percentage = {service: 0.0},
					http_code = 204
				)
			)
			await log(empty_response)
			return empty_response

		else:
			# Initialize empty lists
			songs = []
			collections = []
			videos = []

			# Only create objects if they are allowed by the media_types parameter
			if 'song' in allowed_types:
				songs = await create_song_objects(
					results = lookup_json,
					request = request,
					start_time = start_time,
					http_code = 200
				)
			
			if 'album' in allowed_types:
				collections = await create_collection_objects(
					results = lookup_json,
					request = request,
					start_time = start_time,
					http_code = 200
				)
			
			if 'video' in allowed_types:
				videos = await create_music_video_objects(
					results = lookup_json,
					request = request,
					start_time = start_time,
					http_code = 200
				)

			if songs != [] or collections != [] or videos != []:
				return Query(
					service = service,
					songs = songs,
					collections = collections,
					music_videos = videos, # Fixed typo: was previously assigning 'collections'
					meta = Meta(
						service = service,
						request = request,
						processing_time = current_unix_time_ms() - start_time,
						filter_confidence_percentage = 0.0, # Because there was no filtering involved
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
						filter_confidence_percentage = {service: 0.0},
						http_code = 204
					)
				)
				await log(empty_response)
				return empty_response

	# If sinister things happen
	except Exception as msg:
		error = Error(
			service = service,
			component = component,
			error_msg = f'Error when doing general query search: "{msg}"',
			meta = Meta(
				service = service,
				request = request,
				processing_time = current_unix_time_ms() - start_time,
				filter_confidence_percentage = {service: 0.0},
				http_code = 500
			)
		)
		await log(error, [discord.File(fp = StringIO(json.dumps(lookup_json, indent = 4)), filename = f'{query}.json')])
		return error