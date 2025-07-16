from ServiceCatalogAPI.components import *
from ServiceCatalogAPI.components.ini import keys
from ServiceCatalogAPI.media_services.knowledge.genius.components.generic import *
import requests



async def lookup_song(id: str, country_code: str = 'us') -> object:
	request = {'request': 'lookup_song', 'id': id, 'country_code': country_code}
	start_time = current_unix_time_ms()

	try:
		api_url = f'{api}/songs/{id}'
		api_headers = {'Authorization': f'Bearer {keys['genius']['token']}'}
		result = requests.get(api_url, headers = api_headers)
			
		if result.status_code == 200:
			song = result.json()['response']['song']
			song_type = 'track'
			song_url = song['url']
			song_id = song['id']
			song_title = song['title']
			song_description = convert_genius_desc_into_discord_str(song['description'])
			song_release_date = song['release_date_for_display']
			song_is_explicit = None

			artists_data = song['primary_artists'] + song['featured_artists']

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

			collection_data = song['album']
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
				release_year = collection_data['release_date_for_display'][-4:],
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