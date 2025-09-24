from AstroAPI.InternalComponents.Legacy import *
from AstroAPI.ServiceCatalogAPI.media_services.music.youtube_music.components.generic import *
from AstroAPI.ServiceCatalogAPI.media_services.music.youtube_music.components.lookup.artist import lookup_artist
from AstroAPI.InternalComponents.CredentialsManager.media_services.youtube.credentials import youtube_credentials



async def search_collection(artists: list, title: str, year: int = None, country_code: str = 'us') -> object:
	# Initialize ytmusicapi
	ytm = await youtube_credentials.initialize_ytmusicapi()
	# Prepare the request dictionary with input parameters
	request = {'request': 'search_collection', 'artists': artists, 'title': title, 'year': year, 'country_code': country_code}
	# Lookup JSON variable for later debugging
	lookup_json = None
	# Record the start time for processing time calculation
	start_time = current_unix_time_ms()
	
	try:
		# Optimize strings for query search
		artists = [optimize_for_search(artist) for artist in artists]
		title = optimize_for_search(title)

		collections = []
		# Perform a search on YouTube Music for albums matching the first artist and title
		results = ytm.search(
			query = f'{artists[0]} {title}',
			filter = 'albums'
		)
		# Save the JSON for future debugging if necessary
		lookup_json = results

		# Iterate over each collection result
		for collection in results:
			# Determine if the collection is an album or EP
			collection_type = ('album' if collection['type'] == 'Album' else 'ep')
			collection_url = f'https://music.youtube.com/playlist?list={collection["playlistId"]}'
			collection_id = collection['playlistId']
			collection_title = collection['title']
			collection_year = collection['year']

			# Build a list of Artist objects for the collection
			collection_artists = [
				Artist(
					service = service,
					urls = f'https://music.youtube.com/channel/{artist["id"]}',
					ids = artist['id'],
					name = artist['name'],
					meta = Meta(
						service = service,
						request = request,
						processing_time = current_unix_time_ms() - start_time,
						http_code = 200,
						filter_confidence_percentage = 100.0
					)
				) for artist in collection['artists']]

			# Create a Cover object for the collection
			collection_cover = Cover(
				service = service,
				media_type = collection_type,
				title = collection_title,
				artists = collection_artists,
				hq_urls = collection['thumbnails'][0]['url'],
				lq_urls = collection['thumbnails'][len(collection['thumbnails'])-1]['url'],
				meta = Meta(
					service = service,
					request = request,
					processing_time = current_unix_time_ms() - start_time,
					http_code = 200
				)
			)

			# Append the Collection object to the collections list
			collections.append(Collection(
				service = service,
				type = collection_type,
				urls = collection_url,
				ids = collection_id,
				title = collection_title,
				artists = collection_artists,
				release_year = collection_year,
				cover = collection_cover,
				meta = Meta(
					service = service,
					request = request,
					processing_time = current_unix_time_ms() - start_time,
					http_code = 200
				)
			))
		# Filter and return the collection based on the query parameters
		return await filter_collection(service = service, query_request = request, collections = collections, query_artists = artists, query_title = title, query_year = year, query_country_code = country_code)

	# If sinister things happen
	except Exception as msg:
		error = Error(
			service = service,
			component = component,
			error_msg = f'Error when searching for collection: "{msg}"',
			meta = Meta(
				service = service,
				request = request,
				processing_time = current_unix_time_ms() - start_time,
				http_code = 500
			)
		)
		await log(error, [discord.File(fp = StringIO(json.dumps(lookup_json, indent = 4)), filename = f'{title}.json')])
		return error