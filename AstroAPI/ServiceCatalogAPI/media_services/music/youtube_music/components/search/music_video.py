from AstroAPI.ServiceCatalogAPI.components import *
from AstroAPI.ServiceCatalogAPI.media_services.music.youtube_music.components.generic import *
from AstroAPI.ServiceCatalogAPI.media_services.music.youtube_music.components.lookup.artist import lookup_artist
from AstroAPI.ServiceCatalogAPI.media_services.music.youtube_music.components.generic import ytm



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
		title = optimize_for_search(replace_with_ascii(title).lower())
		
		videos = []
		# Perform a search on YouTube Music for videos matching the first artist and the title
		results = ytm.search(
			query = f'{artists[0]} {title}',
			filter = 'videos'
		)
		# Save the JSON for future debugging if necessary
		lookup_json = results

		# Iterate over each video result
		for video in results:
			mv_url = f'https://music.youtube.com/watch?v={video["videoId"]}'
			mv_id = video['videoId']
			mv_title = video['title']
			
			# If artist information is available in the result
			if video['artists'] != []:
				# Build a list of Artist objects from the result's artists
				mv_artists = [
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
					) for artist in video['artists']]
			else:
				# If no artist info, look up the artist using the video ID
				# Because apparently that's a thing that can happen????????
				# I should probably make an issue on the API's repo
				mv_artists = [await lookup_artist(video_id = video['videoId'], country_code = country_code)]

			# Create a Cover object for the music video
			mv_cover = Cover(
				service = service,
				media_type = 'song',
				title = mv_title,
				artists = mv_artists,
				hq_urls = video['thumbnails'][0]['url'],
				lq_urls = video['thumbnails'][len(video['thumbnails'])-1]['url'],
				meta = Meta(
					service = service,
					request = request,
					processing_time = current_unix_time_ms() - start_time,
					http_code = 200
				)
			)

			# Append a MusicVideo object to the videos list
			videos.append(MusicVideo(
				service = service,
				urls = mv_url,
				ids = mv_id,
				title = mv_title,
				artists = mv_artists,
				is_explicit = None,
				cover = mv_cover,
				meta = Meta(
					service = service,
					request = request,
					processing_time = current_unix_time_ms() - start_time,
					http_code = 200
				)
			))
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
		await log(error, [discord.File(fp = StringIO(json.dumps(lookup_json, indent = 4)), filename = f'{id}.json')])
		return error