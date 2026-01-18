from AstroAPI.InternalComponents.Legacy import *
from AstroAPI.ServiceCatalogAPI.components import *
from AstroAPI.ServiceCatalogAPI.media_services.music.deezer.components.generic import *



async def create_song_objects(json_response: dict, request: dict, start_time: int, http_code: int, incomplete_artist_info: bool):

	"""
		Iterate through Deezer's tracks list in their JSON response and convert all of it into Song objects.
		
		:param json_response: Deezer's JSON response.
		:param request: Request dict.
	"""

	songs = []

	for data in json_response['data']:
		if incomplete_artist_info:
			async with aiohttp.ClientSession() as session:
				api_headers = {
					'Content-Type': 'application/json'
				}

				# Fetch detailed information for each track by ID because the base results don't have much artist info needed for accurate filtering
				async with session.get(url = f'{api}/track/{data['id']}', headers = api_headers) as result:
					# Parse the detailed track info
					song_json = await result.json()
					song = song_json

					song_type = 'track'
					song_url = song['link']
					song_id = song['id']
					song_title = song['title']
					song_is_explicit = song['explicit_lyrics']
					song_artists = get_artists_of_media(request, song['contributors'])

					# Create a Cover object for the song
					song_cover = Cover(
						service = service,
						media_type = song_type,
						title = song_title,
						artists = song_artists,
						hq_urls = song['album']['cover_xl'],
						lq_urls = song['album']['cover_medium'],
						meta = Meta(
							service = service,
							request = request,
							processing_time = current_unix_time_ms() - start_time,
							filter_confidence_percentage = {service: 100.0},
							http_code = http_code
						)
					)

					# Create a Collection object for the song's album/EP
					song_collection = Collection(
						service = service,
						type = 'album' if song['album']['type'] != 'ep' else 'ep',
						urls = song['album']['link'],
						ids = song['album']['id'],
						title = remove_feat(song['album']['title']),
						artists = [song_artists[0]],
						release_year = song['album']['release_date'][:4],
						cover = song_cover,
						meta = Meta(
							service = service,
							request = request,
							processing_time = current_unix_time_ms() - start_time,
							filter_confidence_percentage = {service: 100.0},
							http_code = http_code
						)
					)

					# Append the Song object to the songs list
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
							http_code = http_code
						)
					))
		
		else:
			# Iterate through each song in the response
			for song in json_response['data']:
				# Extract song details
				song_type = 'track'
				song_url = song['link']
				song_id = song['id']
				song_preview = song['preview']
				song_title = song['title']
				song_artists = get_artists_of_media(request, [song['artist']])
				song_is_explicit = song['explicit_lyrics']
				
				# Extract collection details
				collection_type = 'album' if song['album']['type'] != 'ep' else 'ep'
				collection_url = f'https://deezer.com/album/{song['album']['id']}'
				collection_id = {song['album']['id']}
				collection_title = remove_feat(song['album']['title'])
				collection_artists = song_artists

				# Create Cover object for the collection
				song_cover = Cover(
					service = service,
					media_type = song_type,
					title = song_title,
					artists = song_artists,
					hq_urls = song['album']['cover_xl'],
					lq_urls = song['album']['cover_medium'],
					meta = Meta(
						service = service,
						request = request,
						processing_time = current_unix_time_ms() - start_time,
						filter_confidence_percentage = {service: 100.0},
						http_code = http_code
					)
				)

				# Create Collection object for the song's album/EP
				song_collection = Collection(
					service = service,
					type = collection_type,
					urls = collection_url,
					ids = collection_id,
					title = collection_title,
					artists = collection_artists,
					cover = song_cover,
					meta = Meta(
						service = service,
						request = request,
						processing_time = 0,
						filter_confidence_percentage = 100.0,
						http_code = 200
					)
				)

				# Append the Song object to the songs list
				songs.append(Song(
					service = service,
					type = song_type,
					urls = song_url,
					ids = song_id,
					previews = song_preview,
					title = song_title,
					artists = song_artists,
					collection = song_collection,
					is_explicit = song_is_explicit,
					cover = song_cover,
					meta = Meta(
						service = service,
						request = request,
						processing_time = current_unix_time_ms() - start_time,
						http_code = http_code
					)
				))

	return songs