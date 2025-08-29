from AstroAPI.ServiceCatalogAPI.components import *
from AstroAPI.ServiceCatalogAPI.components.ini import keys
from AstroAPI.ServiceCatalogAPI.media_services.knowledge.genius.components.generic import *
from AstroAPI.ServiceCatalogAPI.media_services.knowledge.genius.components.lookup.song import lookup_song
import requests



async def search_song(artists: list, title: str, song_type: str = None, collection: str = None, is_explicit: bool = None, country_code: str = 'us') -> object:
	# Prepare the request dictionary with all input parameters
	request = {'request': 'search_song', 'artists': artists, 'title': title, 'song_type': song_type, 'collection': collection, 'is_explicit': is_explicit, 'country_code': country_code}
	# Record the start time for processing time calculation
	start_time = current_unix_time_ms()

	try:
		# Optimize strings for search
		artists = [optimize_for_search(artist) for artist in artists]
		title = optimize_for_search(title)
		collection = clean_up_collection_title(optimize_for_search(collection)) if collection != None else None
				
		songs = []
		# Construct everything needed for the API call
		api_url = f'{api}/search'
		api_params = {
			'q': f'{artists[0]} {title}'
		}
		api_headers = {'Authorization': f'Bearer {keys["genius"]["token"]}'}
		# For some reason Genius does not like the way aiohttp forms its headers so we stick to requests for HTTP
		# I am not a fan of this but you gotta get it working somehow, I'll figure out a workaround someday
		results = requests.get(api_url, api_params, headers = api_headers)

		if results.status_code == 200:
			results_json = results.json()['response'] # Parse the JSON response
			# Iterate through each search result (hit as Genius calls it)
			for result in results_json['hits']:
				song_url = result['result']['url']
				song_id = result['result']['id']
				song_title = result['result']['title']
				song_is_explicit = None # Explicit flag not provided
				song_collection = None # Collection info not provided

				# Combine primary and featured artists
				artists_data = result['result']['primary_artists'] + result['result']['featured_artists']

				# Build list of Artist objects for the song
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
								http_code = results.status_code,
								filter_confidence_percentage = 100.0
							)
						),
						meta = Meta(
							service = service,
							request = request,
							processing_time = {service: current_unix_time_ms() - start_time},
							http_code = results.status_code,
							filter_confidence_percentage = 100.0
						)
					) for artist in artists_data
				]

				# Build Cover object for the song
				song_cover = Cover(
					service = service,
					media_type = 'song',
					title = song_title,
					artists = song_artists,
					hq_urls = result['result']['song_art_image_url'],
					lq_urls = result['result']['song_art_image_thumbnail_url'],
					meta = Meta(
						service = service,
						request = request,
						processing_time = {service: current_unix_time_ms() - start_time},
						http_code = results.status_code,
						filter_confidence_percentage = 100.0
					)
				)

				# Append the Song object to the songs list
				songs.append(Song(
					service = service,
					type = 'track',
					urls = song_url,
					ids = song_id,
					title = song_title,
					artists = song_artists,
					collection = song_collection,
					is_explicit = song_is_explicit,
					cover = song_cover,
					meta = Meta(
						service = service,
						request = request,
						processing_time = {service: current_unix_time_ms() - start_time},
						http_code = results.status_code,
						filter_confidence_percentage = 100.0 
					)
				))
			# Filter the found songs based on the query
			filtered_song = await filter_song(service = service, query_request = request, songs = songs, query_artists = artists, query_title = title, query_song_type = song_type, query_collection = collection, query_is_explicit = is_explicit, query_country_code = country_code)
			if filtered_song.type == 'track' or filtered_song.type == 'single': # Check if the media type is valid before parsing data for a detailed lookup
				# Lookup the filtered song for more details cuz the query search is VERY limited in knowledge
				filtered_song = await lookup_song(id = filtered_song.ids['genius'], country_code = country_code)
				# Update processing time in the song's metadata
				filtered_song.meta.processing_time[service] = current_unix_time_ms() - start_time
				# Regenerate the song's JSON representation
				# P.S. If you haven't read the media.py file; ALWAYS DO THIS WHEN YOU'RE MODDING MEDIA OBJECT VALUES
				filtered_song.regenerate_json()
			return filtered_song
			
		else:
			error = Error(
				service = service,
				component = component,
				error_msg = "HTTP error when searching for song",
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