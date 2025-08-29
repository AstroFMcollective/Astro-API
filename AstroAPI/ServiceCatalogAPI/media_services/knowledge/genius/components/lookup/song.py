from AstroAPI.ServiceCatalogAPI.components import *
from AstroAPI.ServiceCatalogAPI.components.ini import keys
from AstroAPI.ServiceCatalogAPI.media_services.knowledge.genius.components.generic import *
import requests



async def lookup_song(id: str, country_code: str = 'us') -> object:
	# Prepare the request dictionary with song lookup parameters
	request = {'request': 'lookup_song', 'id': id, 'country_code': country_code}
	# Record the start time for processing time calculation
	start_time = current_unix_time_ms()

	try:
		# Construct everything needed for the API call
		api_url = f'{api}/songs/{id}'
		api_headers = {'Authorization': f'Bearer {keys['genius']['token']}'}
		# For some reason Genius does not like the way aiohttp forms its headers so we stick to requests for HTTP
		# I am not a fan of this but you gotta get it working somehow, I'll figure out a workaround someday
		result = requests.get(api_url, headers = api_headers)
			
		if result.status_code == 200:
			song = result.json()['response']['song'] # Extract the song object from the API response
			song_type = 'track' # Unsure of how Genius differentiates singles from tracks atm, so we treat every song as a track until I do
			song_url = song['url']
			song_id = song['id']
			song_title = song['title']
			# Convert the song's very HTML-like description to a Discord-friendly string while retaining formatting
			song_description = json_to_markdown(song['description'])
			song_release_date = song['release_date_for_display']
			song_is_explicit = None # Explicit flag is not available, set to None

			# Combine primary and featured artists into a single list
			artists_data = song['primary_artists'] + song['featured_artists']

			# Build a list of Artist objects for the song
			song_artists = [
				Artist(
					service = service,
					name = artist['name'],
					urls = artist['url'],
					ids = artist['id'],
					profile_picture = ProfilePicture(
						service = service,
						user_type = 'artist',
						hq_urls = artist['image_url'],
						lq_urls = artist['header_image_url'],
						meta = Meta(
							service = service,
							request = request,
							processing_time = {service: current_unix_time_ms() - start_time},
							http_code = result.status_code,
							filter_confidence_percentage = 100.0
						)
					),
					meta = Meta(
						service = service,
						request = request,
						processing_time = {service: current_unix_time_ms() - start_time},
						http_code = result.status_code,
						filter_confidence_percentage = 100.0
					)
				) for artist in artists_data
			]

			# Build the Cover object for the song
			song_cover = Cover(
				service = service,
				media_type = 'song',
				title = song_title,
				artists = song_artists,
				hq_urls = song['song_art_image_url'],
				lq_urls = song['song_art_image_thumbnail_url'],
				meta = Meta(
					service = service,
					request = request,
					processing_time = {service: current_unix_time_ms() - start_time},
					http_code = result.status_code,
					filter_confidence_percentage = 100.0
				)
			)

			# Build the Collection object for the song's album
			if 'album' in song: # Checks if the collection data even exists
				if song['album'] != None:
					collection_data = song['album'] # Extract collection data from the song
					song_collection = Collection(
						service = service,
						type = 'album',
						urls = collection_data['url'],
						ids = collection_data['id'],
						title = collection_data['name'],
						artists = [
							Artist(
								service = service,
								name = artist['name'],
								urls = artist['url'],
								ids = artist['id'],
								profile_picture = ProfilePicture(
									service = service,
									user_type = 'artist',
									hq_urls = artist['image_url'],
									lq_urls = artist['header_image_url'],
									meta = Meta(
										service = service,
										request = request,
										processing_time = {service: current_unix_time_ms() - start_time},
										http_code = result.status_code,
										filter_confidence_percentage = 100.0
									)
								),
								meta = Meta(
									service = service,
									request = request,
									processing_time = {service: current_unix_time_ms() - start_time},
									http_code = result.status_code,
									filter_confidence_percentage = 100.0
								)
							) for artist in collection_data['primary_artists']
						],
						release_year = collection_data['release_date_for_display'][-4:], # Extract the release year from the album's release date string
						# Build the Cover object for the album
						cover = Cover(
							service = service,
							media_type = 'album',
							title = collection_data['name'],
							artists = song_artists,
							hq_urls = song['song_art_image_url'],
							lq_urls = song['song_art_image_thumbnail_url'],
							meta = Meta(
								service = service,
								request = request,
								processing_time = {service: current_unix_time_ms() - start_time},
								http_code = result.status_code,
								filter_confidence_percentage = 100.0
							)
						),
						meta = Meta(
							service = service,
							request = request,
							processing_time = {service: current_unix_time_ms() - start_time},
							http_code = result.status_code,
							filter_confidence_percentage = 100.0
						)
					)
				else:
					song_collection = None
			else:
				song_collection = None



			# Return a Knowledge object with all the song's knowledge metadata
			return Knowledge(
				service = service,
				media_type = song_type,
				urls = song_url,
				ids = song_id,
				title = song_title,
				artists = song_artists,
				collection = song_collection,
				description = song_description,
				release_date = song_release_date,
				is_explicit = song_is_explicit,
				cover = song_cover,
				meta = Meta(
					service = service,
					request = request,
					processing_time = {service: current_unix_time_ms() - start_time},
					filter_confidence_percentage = {service: 100.0},
					http_code = result.status_code
				)
			)

		else:
			error = Error(
				service = service,
				component = component,
				error_msg = "HTTP error when looking up song knowledge",
				meta = Meta(
					service = service,
					request = request,
					processing_time = {service: current_unix_time_ms() - start_time},
					http_code = result.status_code
				)
			)
			await log(error)
			return error
		
	# If sinister things happen
	except Exception as error:
		error = Error(
			service = service,
			component = component,
			error_msg = f'Error when looking up song knowledge: "{error}"',
			meta = Meta(
				service = service,
				request = request,
				http_code = 500,
				processing_time = {service: current_unix_time_ms() - start_time}
			)
		)
		await log(error)
		return error