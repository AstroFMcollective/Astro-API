from AstroAPI.InternalComponents.Legacy import *
from AstroAPI.ServiceCatalogAPI.media_services.music.apple_music.components.generic import *
from AstroAPI.ServiceCatalogAPI.media_services.music.apple_music.components.lookup.artist import lookup_artist

import aiohttp



async def lookup_collection(id: str, country_code: str = 'us', ignore_single_suffix: bool = False) -> object:
	# Prepare the request metadata
	request = {'request': 'lookup_collection', 'id': id, 'country_code': country_code}
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
			timeout = aiohttp.ClientTimeout(total = 30)  # Set a timeout for the request

			# Make the GET request to the API
			async with session.get(url = api_url, params = api_params, timeout = timeout) as response:
				if response.status == 200:
					# Parse the JSON response
					collection = await response.json(content_type = 'text/javascript')

					if collection['results'] != []: # Check if there was any collection data returned
						collection = collection['results'][0]
						# Check if the collection is a single or not
						# If an internal toggle for single suffix ignoring is set, treat the collection as a collection regardless if it's a single or not
						if ' - Single' not in collection['collectionName'] or ignore_single_suffix:
							# Determine if it's an album or EP
							collection_type = ('single' if ' - Single' in collection['collectionName'] else 'ep' if ' - EP' in collection['collectionName'] else 'album')
							collection_url = collection['collectionViewUrl']
							collection_id = collection['collectionId']
							collection_title = clean_up_collection_title(collection['collectionName'])
							# Lookup artist information
							collection_artists = await lookup_artist(id = collection['artistId'], country_code = country_code)
							collection_artists = [collection_artists]
							collection_year = collection['releaseDate'][:4]  # Extract release year
							collection_genre = collection['primaryGenreName'] if 'primaryGenreName' in collection else None

							# Create the cover object
							collection_cover = Cover(
								service = service,
								media_type = collection_type,
								title = collection_title,
								artists = collection_artists,
								hq_urls = collection['artworkUrl100'],
								lq_urls = collection['artworkUrl60'],
								meta = Meta(
									service = service,
									request = request,
									processing_time = current_unix_time_ms() - start_time,
									filter_confidence_percentage = {service: 100.0},
									http_code = response.status
								)
							)

							# Return the Collection object
							return Collection(
								service = service,
								type = collection_type,
								urls = collection_url,
								ids = collection_id,
								title = collection_title,
								artists = collection_artists,
								release_year = collection_year,
								cover = collection_cover,
								genre = collection_genre,
								meta = Meta(
									service = service,
									request = request,
									processing_time = current_unix_time_ms() - start_time,
									filter_confidence_percentage = {service: 100.0},
									http_code = response.status
								)
							)

						else:
							# Handle the case where the collection is a single
							song_type = 'single'
							song_url = collection['collectionViewUrl']
							song_id = collection['collectionId']
							song_title = clean_up_collection_title(collection['collectionName'])
							# Lookup artist information
							song_artists = await lookup_artist(id = collection['artistId'], country_code = country_code)
							song_artists = [song_artists]
							# Determine if the song is explicit
							song_is_explicit = not 'not' in collection['collectionExplicitness']
							song_genre = collection['primaryGenreName'] if 'primaryGenreName' in collection else None
							# Create the cover object for the song
							song_cover = Cover(
								service = service,
								media_type = song_type,
								title = song_title,
								artists = song_artists,
								hq_urls = collection['artworkUrl100'],
								lq_urls = collection['artworkUrl60'],
								meta = Meta(
									service = service,
									request = request,
									processing_time = current_unix_time_ms() - start_time,
									filter_confidence_percentage = {service: 100.0},
									http_code = response.status
								)
							)

							# Create a Collection object for the single
							song_collection = Collection(
								service = service,
								type = song_type,
								urls = song_url,
								ids = song_id,
								title = song_title,
								artists = song_artists,
								cover = song_cover,
								release_year = collection['releaseDate'][:4],
								genre = song_genre,
								meta = Meta(
									service = service,
									request = request,
									processing_time = current_unix_time_ms() - start_time,
									filter_confidence_percentage = {service: 100.0},
									http_code = response.status
								)
							)

							# Return the Song object
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
								http_code = 204
							)
						)
						await log(empty)
						return empty

				else:
					error = Error(
						service = service,
						component = component,
						error_msg = "HTTP error when looking up collection ID",
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