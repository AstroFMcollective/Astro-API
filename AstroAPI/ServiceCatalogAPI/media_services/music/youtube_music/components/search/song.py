from AstroAPI.ServiceCatalogAPI.components import *
from AstroAPI.InternalComponents.SystemMediaObjects import *
from AstroAPI.InternalComponents.Legacy import *
from AstroAPI.ServiceCatalogAPI.media_services.music.youtube_music.components.generic import *
from AstroAPI.ServiceCatalogAPI.media_services.music.youtube_music.components.lookup.artist import lookup_artist
from AstroAPI.ServiceCatalogAPI.media_services.music.youtube_music.components.lookup.collection import lookup_collection
from AstroAPI.InternalComponents.CredentialsManager.media_services.youtube.credentials import youtube_credentials



async def search_song(artists: list, title: str, song_type: str = None, collection: str = None, is_explicit: bool = None, country_code: str = 'us') -> object:
	# Build the request dictionary with all input parameters
	request = {'request': 'search_song', 'artists': artists, 'title': title, 'song_type': song_type, 'collection': collection, 'is_explicit': is_explicit, 'country_code': country_code}
	# Lookup JSON variable for later debugging
	lookup_json = None
	# Record the start time for processing time calculation
	start_time = current_unix_time_ms()
	
	try:
		# Optimize strings for query search
		artists = [optimize_for_search(artist) for artist in artists]
		title = optimize_for_search(replace_with_ascii(title).lower())
		collection = clean_up_collection_title(optimize_for_search(collection)) if collection != None else None
			
		songs = []
		# Search for songs using the first artist and the title
		results = youtube_credentials.ytmusicapi.search(
			query = f'{artists[0]} {title}',
			filter = 'songs'
		)
		# Save the JSON for future debugging if necessary
		lookup_json = results

		# Iterate through each song result
		for song in results:
			song_type = 'track' # Set song type to 'track' because AFAIK there is nothing differentiating singles from tracks inside the metadata
			song_url = f'https://music.youtube.com/watch?v={song['videoId']}'
			song_id = song['videoId']
			song_title = song['title']
			song_is_explicit = song['isExplicit']
			
			# If artist info is available in the song result
			if 'artists' in song and song['artists'] != []:
				# Build Artist objects for each artist in the result
				song_artists = [
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
					) for artist in song['artists']]
			else:
				# If no artist info, look up the artist using the video ID
				# Because apparently that's a thing that can happen????????
				# I should probably make an issue on the API's repo
				song_artists = [await lookup_artist(video_id = song['videoId'], country_code = country_code)]

			# Build Cover object for the song
			song_cover = Cover(
				service = service,
				media_type = 'song',
				title = song_title,
				artists = song_artists,
				hq_urls = song['thumbnails'][len(song['thumbnails'])-1]['url'],
				lq_urls = song['thumbnails'][0]['url'],
				meta = Meta(
					service = service,
					request = request,
					processing_time = current_unix_time_ms() - start_time,
					http_code = 200
				)
			)

			# Build Collection object for the song's album
			if song['album'] != None:
				song_collection = Collection(
					service = service,
					type = 'album',
					urls = f'https://music.youtube.com/playlist?list={song['album']['id']}',
					ids = song['album']['id'],
					title = song['album']['name'],
					artists = [song_artists[0]],
					release_year = song['album']['year'] if 'year' in song['album'] else None,
					cover = song_cover,
					meta = Meta(
						service = service,
						request = request,
						processing_time = current_unix_time_ms() - start_time,
						http_code = 200,
						filter_confidence_percentage = 100.0
					)
				)
			else:
				song_collection = None

			# Append the constructed Song object to the songs list
			songs.append(Song(
				service = service,
				type = song_type,
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
					processing_time = current_unix_time_ms() - start_time,
					http_code = 200
				)
			))

		# Rip the filtered song, replace the collection with the lookup_collection collection
		filtered_song = await filter_song(service = service, query_request = request, songs = songs, query_artists = artists, query_title = title, query_song_type = song_type, query_collection = collection, query_is_explicit = is_explicit, query_country_code = country_code)
		if filtered_song.type == 'track':
			filtered_song.collection = await lookup_collection(browse_id = filtered_song.collection.ids[service], country_code = country_code)
			# Regenerate the song's JSON representation
		return filtered_song

	# If sinister things happen
	except Exception as msg:
		error = Error(
			service = service,
			component = component,
			error_msg = f'Error while searching song: {msg}',
			meta = Meta(
				service = service,
				request = request,
				http_code = 500,
				processing_time = current_unix_time_ms() - start_time,
			)
		)
		await log(error, [discord.File(fp = StringIO(json.dumps(lookup_json, indent = 4)), filename = f'{title}.json')])
		return error