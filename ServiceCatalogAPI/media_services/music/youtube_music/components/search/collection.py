from ServiceCatalogAPI.components import *
from ServiceCatalogAPI.media_services.music.youtube_music.components.generic import *
from ServiceCatalogAPI.media_services.music.youtube_music.components.lookup.artist import lookup_artist
from ServiceCatalogAPI.media_services.music.youtube_music.components.generic import ytm



async def search_collection(artists: list, title: str, year: int = None, country_code: str = 'us') -> object:
	request = {'request': 'search_collection', 'artists': artists, 'title': title, 'year': year, 'country_code': country_code}
	start_time = current_unix_time_ms()
	
	try:
		artists = [optimize_for_search(artist) for artist in artists]
		title = optimize_for_search(title)

		collections = []
		results = ytm.search(
			query = f'{artists[0]} {title}',
			filter = 'albums'
		)

		for collection in results:
			collection_type = ('album' if collection['type'] == 'Album' else 'ep')
			collection_url = f'https://music.youtube.com/playlist?list={collection['playlistId']}'
			collection_id = collection['playlistId']
			collection_title = collection['title']
			collection_year = collection['year']

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
		return await filter_collection(service = service, query_request = request, collections = collections, query_artists = artists, query_title = title, query_year = year, query_country_code = country_code)

	except Exception as msg:
		error = Error(
			service = service,
			component = component,
			error_msg = f'Error when searching for collection: "{msg}"',
			meta = Meta(
				service = service,
				request = request,
				processing_time = current_unix_time_ms() - start_time,
			)
		)
		await log(error)
		return error