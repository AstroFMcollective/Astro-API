from AstroAPI.ServiceCatalogAPI.components import *
from AstroAPI.ServiceCatalogAPI.media_services.music.apple_music.components.generic import *
from AstroAPI.ServiceCatalogAPI.media_services.music.apple_music.components.lookup.artist import lookup_artist
from AstroAPI.ServiceCatalogAPI.media_services.music.apple_music.components.lookup.collection import lookup_collection

import aiohttp



async def lookup_song(id: str, country_code: str = 'us') -> object:
	# Prepare the request dictionary with song lookup parameters
	request = {'request': 'lookup_song', 'id': id, 'country_code': country_code}
	# Record the start time for processing time calculation
	start_time = current_unix_time_ms()

	try:
		# Create an aiohttp session
		async with aiohttp.ClientSession() as session:
			# Prepare for API call
			api_url = f'{api}/lookup'
			api_params = {
				'id': id,
				'country': country_code.lower()
			}
			timeout = aiohttp.ClientTimeout(total = 30) # Set a timeout for the HTTP request

			# Make the GET request to the API endpoint
			async with session.get(url = api_url, params = api_params, timeout = timeout) as response:
				if response.status == 200:
					# Parse the JSON response
					song = await response.json(content_type = 'text/javascript')
					
					if song['results'] != []: # Check if there was any song data returned
						song = song['results'][0]
						# Determine the song type based on the collection name
						song_type = 'track' if ' - Single' not in song['collectionName'] else 'single'
						song_url = song['trackViewUrl']
						song_id = song['trackId']
						song_title = song['trackName']
						# Lookup the artist information asynchronously
						song_artists = await lookup_artist(id = song['artistId'], country_code = country_code)
						song_artists = [song_artists]
						# Lookup the collection information asynchronously
						song_collection = await lookup_collection(id = song['collectionId'], country_code = country_code, ignore_single_suffix = True)
						song_is_explicit = not 'not' in song['trackExplicitness']
						song_genre = song['primaryGenreName'] if 'primaryGenreName' in song else None

						# Create a Cover object for the song
						song_cover = Cover(
							service = service,
							media_type = song_type,
							title = song_title,
							artists = song_artists,
							hq_urls = song['artworkUrl100'],
							lq_urls = song['artworkUrl30'],
							meta = Meta(
								service = service,
								request = request,
								processing_time = current_unix_time_ms() - start_time,
								filter_confidence_percentage = {service: 100.0},
								http_code = response.status
							)
						)

						# Return a Song object with all the gathered information
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

					else: # If not, return an empty object and log it
						empty = Empty(
							service = service,
							meta = Meta(
								service = service,
								request = request,
								processing_time = current_unix_time_ms() - start_time,
								http_code = response.status
							)
						)
						await log(empty)
						return empty

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