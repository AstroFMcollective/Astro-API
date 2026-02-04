from AstroAPI.InternalComponents.Legacy import *
from AstroAPI.ServiceCatalogAPI.components import *
from AstroAPI.ServiceCatalogAPI.media_services.music.apple_music.components.generic import *



async def create_song_objects(json_response: dict, request: dict, start_time: int, http_code: int):
	songs = []

	# Iterate through each song in the results
	for song in json_response['results']:
		if song['kind'] == 'song':
			# Determine the song type based on collection name
			song_type = 'track' if ' - Single' not in song['collectionName'] else 'single'
			song_url = song['trackViewUrl']
			song_id = song['trackId']
			song_preview = song['previewUrl']
			song_title = song['trackName']
			# Determine if the song is explicit
			song_is_explicit = not 'not' in song['trackExplicitness']
			song_genre = song['primaryGenreName'] if 'primaryGenreName' in song else None

			# Build a list of Artist objects for the song
			song_artists = [
				Artist(
					service = service,
					urls = song['artistViewUrl'] if 'artistViewUrl' in song else f'https://music.apple.com/{request['country_code']}/artist/{song['artistId']}', # Additional edge case if artistViewUrl is missing... this API is so weird
					ids = song['artistId'],
					name = artist,
					meta = Meta(
						service = service,
						request = request,
						processing_time = current_unix_time_ms() - start_time,
						filter_confidence_percentage = 100.0,
						http_code = http_code
					)
				) for artist in split_artists(song['artistName'])
			]

			# Create a Cover object for the song
			song_cover = Cover(
				service = service,
				media_type = song_type,
				title = song_title,
				artists = song_artists,
				hq_urls = song['artworkUrl100'],
				lq_urls = song['artworkUrl60'],
				meta = Meta(
					service = service,
					request = request,
					processing_time = current_unix_time_ms() - start_time,
					filter_confidence_percentage = 100.0,
					http_code = http_code
				)
			)

			# Create a Collection object for the song's collection
			song_collection = Collection(
				service = service,
				type = 'album' if ' - EP' not in song['collectionName'] else 'ep' if song_type != 'single' else song_type,
				urls = song['collectionViewUrl'],
				ids = song['collectionId'],
				title = clean_up_collection_title(song['collectionName']),
				artists = song_artists,
				cover = song_cover,
				meta = Meta(
					service = service,
					request = request,
					processing_time = current_unix_time_ms() - start_time,
					filter_confidence_percentage = 100.0,
					http_code = http_code
				)
			)

			# Append the constructed Song object to the songs list
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
				genre = song_genre,
				meta = Meta(
					service = service,
					request = request,
					processing_time = current_unix_time_ms() - start_time,
					http_code = http_code
				)
			))

	return songs