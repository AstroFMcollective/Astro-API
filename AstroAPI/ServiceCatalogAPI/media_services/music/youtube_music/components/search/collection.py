from AstroAPI.ServiceCatalogAPI.components import *
from AstroAPI.InternalComponents.SystemMediaObjects import *
from AstroAPI.InternalComponents.Legacy import *
from AstroAPI.ServiceCatalogAPI.media_services.music.youtube_music.components.generic import *
from AstroAPI.ServiceCatalogAPI.media_services.music.youtube_music.components.lookup.artist import lookup_artist
from AstroAPI.InternalComponents.CredentialsManager.media_services.youtube.credentials import youtube_credentials



async def search_collection(artists: list, title: str, year: int = None, country_code: str = 'us') -> object:
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
		results = youtube_credentials.ytmusicapi.search(
			query = f'{artists[0]} {title}',
			filter = 'albums'
		)
		# Save the JSON for future debugging if necessary
		lookup_json = results

		# Iterate over each collection result
		collections = await create_collection_objects(
			results = lookup_json,
			request = request,
			start_time = start_time,
			http_code = 200
		)
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