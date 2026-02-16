from AstroAPI.ServiceCatalogAPI.components import *
from AstroAPI.InternalComponents.SystemMediaObjects import *
from AstroAPI.InternalComponents.Legacy import *
from AstroAPI.ServiceCatalogAPI.media_services.music.youtube_music.components.generic import *
from AstroAPI.ServiceCatalogAPI.media_services.music.youtube_music.components.lookup.artist import lookup_artist
from AstroAPI.InternalComponents.CredentialsManager.media_services.youtube.credentials import youtube_credentials



async def search_music_video(artists: list, title: str, is_explicit: bool = None, country_code: str = 'us') -> object:
	# Prepare the request dictionary with search parameters
	request = {'request': 'search_music_video', 'artists': artists, 'title': title, 'is_explicit': is_explicit, 'country_code': country_code}
	# Lookup JSON variable for later debugging
	lookup_json = None
	# Record the start time for processing time calculation
	start_time = current_unix_time_ms()

	try:
		# Optimize strings for query search
		artists = [optimize_for_search(artist) for artist in artists]
		title = optimize_for_search(transliterate_to_ascii(title).lower())
		
		videos = []
		# Perform a search on YouTube Music for videos matching the first artist and the title
		results = youtube_credentials.ytmusicapi.search(
			query = f'{artists[0]} {title}',
			filter = 'videos'
		)
		# Save the JSON for future debugging if necessary
		lookup_json = results

		# Iterate over each video result
		
		videos = await create_music_video_objects(
			results = lookup_json,
			request = request,
			start_time = start_time,
			http_code = 200
		)

		# Filter and return the music video based on the query parameters
		return await filter_mv(service = service, query_request = request, videos = videos, query_artists = artists, query_title = title, query_is_explicit = is_explicit, query_country_code = country_code)

	# If sinister things happen
	except Exception as msg:
		error = Error(
			service = service,
			component = component,
			error_msg = f'Error when searching for music video: "{msg}"',
			meta = Meta(
				service = service,
				request = request,
				processing_time = current_unix_time_ms() - start_time,
			)
		)
		await log(error, [discord.File(fp = StringIO(json.dumps(lookup_json, indent = 4)), filename = f'{title}.json')])
		return error