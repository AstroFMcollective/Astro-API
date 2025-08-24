from ServiceCatalogAPI.components import *
from ServiceCatalogAPI.media_services.music.youtube_music.components.generic import *
from ServiceCatalogAPI.media_services.music.youtube_music.components.lookup.artist import lookup_artist
from ServiceCatalogAPI.media_services.music.youtube_music.components.generic import ytm



async def search_query(query: str, country_code: str = 'us') -> object: # TODO: Dovrši
	# Prepare the request dictionary with query details
	request = {'request': 'search_query', 'query': query, 'country_code': country_code}
	# Lookup JSON variable for later debugging
	lookup_json = None
	# Record the start time for processing time calculation
	start_time = current_unix_time_ms()

	try:
		# Perform the search using ytm (YouTube Music API wrapper)
		results = ytm.search(
			query = query
		)
		# Save the JSON for future debugging if necessary
		lookup_json = results
		# Take the first result from the search results
		result = results[0]
		# Get the type of the result (song, album, video, etc.)
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
					ids = 0, # ytmusicapi does not provide artist IDs for albums via query search, WHY?????????????
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
		await log(error, [discord.File(fp = StringIO(json.dumps(lookup_json, indent = 4)), filename = f'{id}.json')])
		return error