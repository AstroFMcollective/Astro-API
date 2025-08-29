import AstroAPI.ServiceCatalogAPI as ServiceCatalog
from fastapi import FastAPI, HTTPException



music_media_services = ['spotify', 'apple_music', 'youtube_music', 'deezer']
knowledge_media_services = ['spotify', 'genius']
illegal_results = ['error', 'empty_response']



def get_service_catalog_api(media_type: str, service: str):
	if media_type == 'music':
		service_api = getattr(ServiceCatalog.music, service)
	elif media_type == 'knowledge':
		service_api = getattr(ServiceCatalog.knowledge, service)
	return service_api



api = FastAPI()
print("[AstroAPI] Ready!")
print(f"[AstroAPI] Version: {ServiceCatalog.version}")
print(f"[AstroAPI] Deployment channel: {ServiceCatalog.deployment_channel}")



# ------------------------------------
# --- Service Search API Endpoints ---
# ------------------------------------

# Song Search for media services
@api.get("/{media}/{service}/search_song")
async def search_song(media: str, service: str, artist: str, title: str, song_type: str = None, collection_title: str = None, is_explicit: str = None, country_code: str = 'us', exclude_services: str = None):
	# Prepare everything for the API request
	is_explicit = False if is_explicit is None else is_explicit.lower() == 'true' # Convert the is_explicit string to a boolean
	country_code = country_code.lower()
	exclude_services = exclude_services.lower().split(',') if exclude_services is not None else [] # Split the exclude_services string into a list (ex. 'spotify,deezer' -> ['spotify', 'deezer'])
	service_api = get_service_catalog_api(media, service)

	# Check if the queried service is the Global Interface, so we know whether we need to plug in the exclude_services parameter into it or not
	if service == 'global_io': 
		song_object = await service_api.search_song(
			artists = [artist],
			title = title,
			song_type = song_type,
			collection = collection_title,
			is_explicit = is_explicit,
			country_code = country_code,
			exclude_services = exclude_services
		)
	else:
		song_object = await service_api.search_song(
			artists = [artist],
			title = title,
			song_type = song_type,
			collection = collection_title,
			is_explicit = is_explicit,
			country_code = country_code
		)
	if song_object.type not in illegal_results:
		return song_object.json
	else:
		raise HTTPException(status_code = song_object.meta.http_code, detail = song_object.error_msg if song_object.type == 'error' else None)



# Music Video Search for media services
@api.get("/{media}/{service}/search_music_video")
async def search_music_video(media: str, service: str, artist: str, title: str, is_explicit: str = None, country_code: str = 'us', exclude_services: str = None):
	# Prepare everything for the API request
	is_explicit = False if is_explicit is None else is_explicit.lower() == 'true' # Convert the is_explicit string to a boolean
	country_code = country_code.lower()
	exclude_services = exclude_services.lower().split(',') if exclude_services is not None else [] # Split the exclude_services string into a list (ex. 'spotify,deezer' -> ['spotify', 'deezer'])
	service_api = get_service_catalog_api(media, service)

	# Check if the queried service is the Global Interface, so we know whether we need to plug in the exclude_services parameter into it or not
	if service == 'global_io': 
		music_video_object = await service_api.search_music_video(
			artists = [artist],
			title = title,
			is_explicit = is_explicit,
			country_code = country_code,
			exclude_services = exclude_services
		)
	else:
		music_video_object = await service_api.search_music_video(
			artists = [artist],
			title = title,
			is_explicit = is_explicit,
			country_code = country_code
		)
	if music_video_object.type not in illegal_results:
		return music_video_object.json
	else:
		raise HTTPException(status_code = music_video_object.meta.http_code, detail = music_video_object.error_msg if music_video_object.type == 'error' else None)



# Collection Search for media services
@api.get("/{media}/{service}/search_collection")
async def search_collection(media: str, service: str, artist: str, title: str, year: str = None, country_code: str = 'us', exclude_services: str = None):
	# Prepare everything for the API request
	year = int(year) if year is not None else None
	country_code = country_code.lower()
	exclude_services = exclude_services.lower().split(',') if exclude_services is not None else [] # Split the exclude_services string into a list (ex. 'spotify,deezer' -> ['spotify', 'deezer'])
	service_api = get_service_catalog_api(media, service)

	# Check if the queried service is the Global Interface, so we know whether we need to plug in the exclude_services parameter into it or not
	if service == 'global_io': 
		collection_object = await service_api.search_collection(
			artists = [artist],
			title = title,
			year = year,
			country_code = country_code,
			exclude_services = exclude_services
		)
	else:
		collection_object = await service_api.search_collection(
			artists = [artist],
			title = title,
			year = year,
			country_code = country_code
		)
	if collection_object.type not in illegal_results:
		return collection_object.json
	else:
		raise HTTPException(status_code = collection_object.meta.http_code, detail = collection_object.error_msg if collection_object.type == 'error' else None)



# Query Search for media services
@api.get("/{media}/{service}/search_query")
async def search_music_video(media: str, service: str, query: str, country_code: str = 'us', exclude_services: str = None):
	# Prepare everything for the API request
	country_code = country_code.lower()
	exclude_services = exclude_services.lower().split(',') if exclude_services is not None else [] # Split the exclude_services string into a list (ex. 'spotify,deezer' -> ['spotify', 'deezer'])
	service_api = get_service_catalog_api(media, service)

	# Check if the queried service is the Global Interface, so we know whether we need to plug in the exclude_services parameter into it or not
	if service == 'global_io': 
		query_object = await service_api.search_query(
			query = query,
			country_code = country_code,
			exclude_services = exclude_services
		)
	else:
		query_object = await service_api.search_query(
			query = query,
			country_code = country_code
		)
	if query_object.type not in illegal_results:
		return query_object.json
	else:
		raise HTTPException(status_code = query_object.meta.http_code, detail = query_object.error_msg if query_object.type == 'error' else None)







# ------------------------------------
# --- Service Lookup API Endpoints ---
# ------------------------------------

# Song Lookup for media services
@api.get("/{media}/{service}/lookup_song")
async def lookup_song(media: str, service: str, id: str, id_service: str = None, country_code: str = 'us'):
	# Prepare everything for the API request
	media = media.lower()
	service = service.lower()
	id_service = id_service.lower() if id_service is not None else None
	country_code = country_code.lower()
	# Request from the correct API endpoint
	if id_service == service or id_service is None: # Check if the supplied ID service is empty or the same as the service in the path
		# Get the service's correct object variable
		service_api = get_service_catalog_api(media, service)
		song_object = await service_api.lookup_song(id, country_code) # If so, assume the user wants to query the path service with the ID
	else: # If they are different, the user wants to do a Global Interface request or wants to request from a different service
		# Get the ID service's correct object variable
		if id_service in music_media_services:
			id_service_api = get_service_catalog_api('music', id_service)
		elif id_service in knowledge_media_services:
			id_service_api = get_service_catalog_api('knowledge', id_service)
		# Request from the Global Interface if that's what the user wants
		if service == 'global_io':
			# Get the service's correct object variable
			service_api = get_service_catalog_api(media, service)
			song_object = await service_api.lookup_song(id_service_api, id, country_code, country_code)
		else:
			# Request for the song from the ID service
			# We'll use its data to construct a query request for a path service song search 
			id_service_song_object = await id_service_api.lookup_song(id = id, country_code = country_code)
			# Get the service's correct object variable
			service_api = get_service_catalog_api(media, service)
			# Query the service for the song
			song_object = await service_api.search_song(
				artists = [artist.name for artist in id_service_song_object.artists],
				title = id_service_song_object.title,
				song_type = id_service_song_object.type,
				collection = id_service_song_object.collection.title if 'collection' in id_service_song_object.json else None,
				is_explicit = id_service_song_object.is_explicit,
				country_code = country_code,
			)
	if song_object.type not in illegal_results:
		return song_object.json
	else:
		raise HTTPException(status_code = song_object.meta.http_code, detail = song_object.error_msg if song_object.type == 'error' else None)



# Music Video Lookup for media services
@api.get("/{media}/{service}/lookup_music_video")
async def lookup_music_video(media: str, service: str, id: str, id_service: str = None, country_code: str = 'us'):
	# Prepare everything for the API request
	media = media.lower()
	service = service.lower()
	id_service = id_service.lower() if id_service is not None else None
	country_code = country_code.lower()
	# Request from the correct API endpoint
	if id_service == service or id_service is None: # Check if the supplied ID service is empty or the same as the service in the path
		# Get the service's correct object variable
		service_api = get_service_catalog_api(media, service)
		music_video_object = await service_api.lookup_music_video(id, country_code) # If so, assume the user wants to query the path service with the ID
	else: # If they are different, the user wants to do a Global Interface request or wants to request from a different service
		# Get the ID service's correct object variable
		if id_service in music_media_services:
			id_service_api = get_service_catalog_api('music', id_service)
		elif id_service in knowledge_media_services:
			id_service_api = get_service_catalog_api('knowledge', id_service)
		# Request from the Global Interface if that's what the user wants
		if service == 'global_io':
			# Get the service's correct object variable
			service_api = get_service_catalog_api(media, service)
			music_video_object = await service_api.lookup_music_video(id_service_api, id, country_code, country_code)
		else:
			# Request for the music_video from the ID service
			# We'll use its data to construct a query request for a path service music video search 
			id_service_music_video_object = await id_service_api.lookup_music_video(id = id, country_code = country_code)
			# Get the service's correct object variable
			service_api = get_service_catalog_api(media, service)
			# Query the service for the music_video
			music_video_object = await service_api.search_music_video(
				artists = [artist.name for artist in id_service_music_video_object.artists],
				title = id_service_music_video_object.title,
				is_explicit = id_service_music_video_object.is_explicit,
				country_code = country_code,
			)
	if music_video_object.type not in illegal_results:
		return music_video_object.json
	else:
		raise HTTPException(status_code = music_video_object.meta.http_code, detail = music_video_object.error_msg if music_video_object.type == 'error' else None)



# Collection Lookup for media services
@api.get("/{media}/{service}/lookup_collection")
async def lookup_collection(media: str, service: str, id: str, id_service: str = None, country_code: str = 'us'):
	# Prepare everything for the API request
	media = media.lower()
	service = service.lower()
	id_service = id_service.lower() if id_service is not None else None
	country_code = country_code.lower()
	# Request from the correct API endpoint
	if id_service == service or id_service is None: # Check if the supplied ID service is empty or the same as the service in the path
		# Get the service's correct object variable
		service_api = get_service_catalog_api(media, service)
		collection_object = await service_api.lookup_collection(id, country_code) # If so, assume the user wants to query the path service with the ID
	else: # If they are different, the user wants to do a Global Interface request or wants to request from a different service
		# Get the ID service's correct object variable
		if id_service in music_media_services:
			id_service_api = get_service_catalog_api('music', id_service)
		elif id_service in knowledge_media_services:
			id_service_api = get_service_catalog_api('knowledge', id_service)
		# Request from the Global Interface if that's what the user wants
		if service == 'global_io':
			# Get the service's correct object variable
			service_api = get_service_catalog_api(media, service)
			collection_object = await service_api.lookup_collection(id_service_api, id, country_code, country_code)
		else:
			# Request for the collection from the ID service
			# We'll use its data to construct a query request for a path service collection search 
			id_service_collection_object = await id_service_api.lookup_collection(id = id, country_code = country_code)
			# Get the service's correct object variable
			service_api = get_service_catalog_api(media, service)
			# Query the service for the collection
			collection_object = await service_api.search_collection(
				artists = [artist.name for artist in id_service_collection_object.artists],
				title = id_service_collection_object.title,
				year = id_service_collection_object.release_year,
				country_code = country_code
			)
	if collection_object.type not in illegal_results:
		return collection_object.json
	else:
		raise HTTPException(status_code = collection_object.meta.http_code, detail = collection_object.error_msg if collection_object.type == 'error' else None)