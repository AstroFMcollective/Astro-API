from AstroAPI.components import *
from AstroAPI.media_services.music.youtube_music.components.generic import *
from AstroAPI.media_services.music.youtube_music.components.lookup.artist import lookup_artist
from AstroAPI.media_services.music.youtube_music.components.generic import ytm



async def lookup_collection(id: str, country_code: str = 'us') -> object:
	request = {'request': 'lookup_collection', 'id': id, 'country_code': country_code, 'url': f'https://music.youtube.com/playlist?list={id}'}
	start_time = current_unix_time_ms()
	
	try:
		browse_id = ytm.get_album_browse_id(id)
		collection = ytm.get_album(browse_id)
			
		collection_type = ('album' if collection['type'] == 'Album' else 'ep')
		collection_url = f'https://music.youtube.com/playlist?list={collection['audioPlaylistId']}'
		collection_id = collection['audioPlaylistId']
		collection_title = collection['title']
		collection_year = collection['year']

		collection_artists = [
			Artist(
				service = service,
				ids = artist['id'],
				name = artist['name'],
				urls = f'https://music.youtube.com/channel/{artist["id"]}',
				meta = Meta(
					service = service,
					request = request,
					processing_time = current_unix_time_ms() - start_time,
					http_code = 200,
					filter_confidence_percentage = {service: 100.0}
				)
			) for artist in collection['artists']
		]

		collection_cover = Cover(
			service = service,
			media_type = 'collection',
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

		return Collection(
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
				filter_confidence_percentage = {service: 100.0},
				http_code = 200
			)
		)
			
	except Exception as msg:
		error = Error(
			service = service,
			component = component,
			error_msg = f'Error while looking up collection {id} on {component}: "{msg}"',
			meta = Meta(
				service = service,
				request = request,
				processing_time = current_unix_time_ms() - start_time,
				http_code = 500
			)
		)
		await log(error)
		return error