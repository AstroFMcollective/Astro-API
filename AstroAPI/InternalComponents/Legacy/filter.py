from AstroAPI.InternalComponents.Legacy.media import *
from AstroAPI.InternalComponents.Legacy.log import *
from AstroAPI.InternalComponents.Legacy.text_manipulation import *
from AstroAPI.InternalComponents.Legacy.time import current_unix_time_ms



"""
	--- THE FILTERING MODULE ---

	Not all services output media the same way. Some might have mismatched caps, some might have special
	suffixes at the end of them (or their collection names), some songs have explicit and PG versions uploaded
	under the same name, some artists have albums that are titled the exact same (ex. Weezer (Blue Album) and
	Weezer (Green Album)), etc.

	The filtering module's job is to account for as many of these edge cases and get the most accurate result
	out of a list of media, given a set of parameters.

	Each function below takes two kinds of parameters:
	- API output data (service and media)
	- Search query data

	Both of these are equally important, because API output data provides the necessary media to sort and filter through,
	and search query data provides the guidelines from which the filtering algorithms know what media object is the most
	accurate out of the ones listed. Don't skimp out on supplying search query data!
"""



async def filter_song(service: str, query_request: dict, songs: list, query_artists: list, query_title: str, query_song_type: str = None, query_collection: str = None, query_is_explicit: bool = None, query_country_code: str = None) -> Song:
	"""
		# Song filtering function

		This is a built-in internal Service Catalog API function which iterates through a list of song media objects and
		determines the single most accurate song with the most overlapping data out of the ones listed.

		It can return two object types: `Song` (filtered song) and `Empty` (empty response).

		 :param service: The string representation of the service whose songs you're filtering.
		 :param query_request: The request data of an API function that called the filtering function.
		 :param songs: A list of song objects.
		 :param query_artists: The artists provided in the API search function query.
		 :param query_title: The artists provided in the API search function query.
		 :param query_song_type: The song type provided in the API search function query.
		 :param query_collection: The artists provided in the API search function query.
		 :param query_is_explicit: The song explicitness provided in the API search function query.
		 :param query_country_code: The country code provided in the API search function query. This parameter is unused right now.
	"""


	start_time = current_unix_time_ms()

	# This function relies on a "scoring" system out of which is then calculated the final percentage (for readability)
	# The more crucial parameters are provided, the higher the score ceiling is (the more precise the filtering algorithm is)
	max_score = 2000
	if query_collection != None:
		max_score += 1000
	if query_is_explicit != None:
		max_score += 500
	if query_song_type != None:
		max_score += 500

	data_with_similarity = [] # Empty list for songs with their similiarity score
	for song in songs:
		song_similarity = 0 # Song similarity overall score, the beginning score is always zero

		artist_input = bare_bones(query_artists[0]) # Strip down the artist name of any stylization and convert all characters into their latin counterparts
		artists_reference = [artist.name for artist in song.artists]
		artists_with_similarity = []

		# This accounts all the artists in a song: checks their similarity with the query data, sorts that data from the highest to lowest, and then applies the highest score to the song similarity overall score
		# In the distant future this will be able to use Artist objects but we're not there yet
		for artist_name in artists_reference:
			artists_with_similarity.append([calculate_similarity(bare_bones(artist_name), artist_input), artist_name]) 
		artists_with_similarity = sort_similarity_lists(artists_with_similarity)
		# If the most accurate artist doesn't have at least 500 points, discard the loop cycle and iterate the next song in the list
		# This is done to immediately eliminate covers of songs
		if artists_with_similarity != [] and artists_with_similarity[0][0] > 500:
			song_similarity += artists_with_similarity[0][0]
		else:
			continue
		
		title_input = bare_bones(query_title) # Strips down the title
		title_reference = remove_feat(song.title) # Removes all features included in the title
		song_similarity += calculate_similarity(bare_bones(title_reference), title_input) # Calculates their similarity and adds it to the overall score

		if query_collection != None and song.collection != None: 
			collection_input = bare_bones(query_collection)
			collection_reference = song.collection.title
			song_similarity += calculate_similarity(bare_bones(collection_reference), collection_input)

		if query_is_explicit != None and song.is_explicit != None: # Since these are boolean values, you can just check them and then add the points or not
			if query_is_explicit == song.is_explicit:
				song_similarity += 500

		if query_song_type != None and song.type != None: # Since these are boolean values, you can just check them and then add the points or not
			if query_song_type == song.type:
				song_similarity += 500

		data_with_similarity.append([song_similarity, song])
	
	data_with_similarity = sort_similarity_lists(data_with_similarity) # Sort the list from the biggest to smallest score
	if data_with_similarity != []: # Check if the list is empty
		top_result = data_with_similarity[0]
		top_data = top_result[1]
		filtering_time = current_unix_time_ms() - start_time
		if percentage(max_score, top_result[0]) > 30: # Check if the similarity percentage is above 30%, if it's not discard the song and return an empty object			
			top_song = Song(
				service = top_data.service,
				type = top_data.type,
				urls = top_data.urls,
				ids =  top_data.ids,
				title = top_data.title,
				artists = top_data.artists,
				collection = top_data.collection,
				cover = top_data.cover,
				genre = top_data.genre,
				is_explicit = top_data.is_explicit,
				meta = Meta(
					service = top_data.service,
					request = top_data.meta.request,
					http_code = top_data.meta.http_code,
					processing_time = top_data.meta.processing_time[top_data.service] + filtering_time,
					filter_confidence_percentage = {top_data.service: percentage(max_score, top_result[0])}
				)
			)
			
			return top_song
		else:
			response = Empty(
				service = service,
				meta = Meta(
					service = top_data.service,
					request = top_data.meta.request,
					http_code = 204,
					processing_time = top_data.meta.processing_time,
					filter_confidence_percentage = {service: percentage(max_score, top_result[0])}
				)
			)
			await log(response)
			return response

	else: # Return empty if there is no song that has passed filtering
		response = Empty(
			service = service,
			meta = Meta(
				service = service,
				request = query_request,
				http_code = 204,
				processing_time = 0,
				filter_confidence_percentage = {service: 0.0}
			)
		)
		await log(response)
		return response



async def filter_mv(service: str, query_request: dict, videos: list, query_artists: list, query_title: str, query_is_explicit: bool = None, query_country_code: str = None) -> Song:
	"""
		# Music video filtering function

		This is a built-in internal Service Catalog API function which iterates through a list of music video media objects and
		determines the single most accurate music video with the most overlapping data out of the ones listed.

		It can return two object types: `MusicVideo` (filtered music video) and `Empty` (empty response).

		 :param service: The string representation of the service whose songs you're filtering.
		 :param query_request: The request data of an API function that called the filtering function.
		 :param videos: A list of music video objects.
		 :param query_artists: The artists provided in the API search function query.
		 :param query_title: The artists provided in the API search function query.
		 :param query_is_explicit: The song explicitness provided in the API search function query.
		 :param query_country_code: The country code provided in the API search function query. This parameter is unused right now.
	"""
	
	
	start_time = current_unix_time_ms()

	# This function relies on a "scoring" system out of which is then calculated the final percentage (for readability)
	# The more crucial parameters are provided, the higher the score ceiling is (the more precise the filtering algorithm is)
	max_score = 2000
	if query_is_explicit != None:
		max_score += 500

	data_with_similarity = [] # Empty list for music videos with their similiarity score
	for video in videos:
		song_similarity = 0 # Music video similarity overall score, the beginning score is always zero
		
		artist_input = bare_bones(query_artists[0]) # Strip down the artist name of any stylization and convert all characters into their latin counterparts
		artists_reference = [artist.name for artist in video.artists]
		artists_with_similarity = []

		# This accounts all the artists in a music video: checks their similarity with the query data, sorts that data from the highest to lowest, and then applies the highest score to the music video similarity overall score
		# In the distant future this will be able to use Artist objects but we're not there yet
		for artist_name in artists_reference:
			artists_with_similarity.append([calculate_similarity(bare_bones(artist_name), artist_input), artist_name])
		artists_with_similarity = sort_similarity_lists(artists_with_similarity)
		# If the most accurate artist doesn't have at least 500 points, discard the loop cycle and iterate the next music video in the list
		# This is done to immediately eliminate covers or fan-made unofficial music videos
		if artists_with_similarity != [] and artists_with_similarity[0][0] > 500:
			song_similarity += artists_with_similarity[0][0]
		else:
			continue

		title_input = bare_bones(query_title) # Strips down the title
		title_reference = remove_feat(video.title) # Removes all features included in the title
		song_similarity += calculate_similarity(bare_bones(title_reference), title_input) # Calculates their similarity and adds it to the overall score

		if query_is_explicit != None and video.is_explicit != None: # Since these are boolean values, you can just check them and then add the points or not
			if query_is_explicit == video.is_explicit:
				song_similarity += 500

		data_with_similarity.append([song_similarity, video])
	
	data_with_similarity = sort_similarity_lists(data_with_similarity) # Sort the list from the biggest to smallest score
	if data_with_similarity != []: # Check if the list is empty
		top_result = data_with_similarity[0]
		top_data = top_result[1]
		filtering_time = current_unix_time_ms() - start_time
		if percentage(max_score, top_result[0]) > 30: # Check if the similarity percentage is above 30%, if it's not discard the music video and return an empty object
			top_video = MusicVideo(
				service = top_data.service,
				urls = top_data.urls,
				ids =  top_data.ids,
				title = top_data.title,
				artists = top_data.artists,
				cover = top_data.cover,
				genre = top_data.genre,
				is_explicit = top_data.is_explicit,
				meta = Meta(
					service = top_data.service,
					request = top_data.meta.request,
					http_code = top_data.meta.http_code,
					processing_time = top_data.meta.processing_time[top_data.service] + filtering_time,
					filter_confidence_percentage = {top_data.service: percentage(max_score, top_result[0])}
				)
			)

			return top_video
		else:
			response = Empty(
				service = service,
				meta = Meta(
					service = top_data.service,
					request = top_data.meta.request,
					http_code = 204,
					processing_time = top_data.meta.processing_time,
					filter_confidence_percentage = {service: percentage(max_score, top_result[0])}
				)
			)
			await log(response)
			return response

	else: # Return empty if there is no video that has passed filtering
		response = Empty(
			service = service,
			meta = Meta(
				service = service,
				request = query_request,
				http_code = 204,
				processing_time = 0,
				filter_confidence_percentage = {service: 0.0}
			)
		)
		await log(response)
		return response



async def filter_collection(service: str, query_request: dict, collections: list, query_artists: list, query_title: str, query_year: str = None, query_country_code: str = None) -> Collection:
	"""
		# Collection filtering function

		This is a built-in internal Service Catalog API function which iterates through a list of collection media objects and
		determines the single most accurate collection with the most overlapping data out of the ones listed.

		It can return two object types: `Collection` (filtered collection) and `Empty` (empty response).

		 :param service: The string representation of the service whose songs you're filtering.
		 :param query_request: The request data of an API function that called the filtering function.
		 :param collections: A list of music video objects.
		 :param query_artists: The artists provided in the API search function query.
		 :param query_title: The artists provided in the API search function query.
		 :param query_is_explicit: The song explicitness provided in the API search function query.
		 :param query_year: The collection year provided in the API search function query.
		 :param query_country_code: The country code provided in the API search function query. This parameter is unused right now.
	"""
	
	
	start_time = current_unix_time_ms()

	# This function relies on a "scoring" system out of which is then calculated the final percentage (for readability)
	# The more crucial parameters are provided, the higher the score ceiling is (the more precise the filtering algorithm is)
	max_score = 2000
	if query_year != None:
		max_score += 1000

	data_with_similarity = [] # Empty list for collections with their similiarity score
	for collection in collections:
		collection_similarity = 0 # Collection similarity overall score, the beginning score is always zero

		artist_input = bare_bones(query_artists[0]) # Strip down the artist name of any stylization and convert all characters into their latin counterparts
		artists_reference = [artist.name for artist in collection.artists]
		artists_with_similarity = []

		# This accounts all the artists in a collection: checks their similarity with the query data, sorts that data from the highest to lowest, and then applies the highest score to the music video similarity overall score
		# In the distant future this will be able to use Artist objects but we're not there yet
		for artist_name in artists_reference:
			artists_with_similarity.append([calculate_similarity(bare_bones(artist_name), artist_input), artist_name])
		artists_with_similarity = sort_similarity_lists(artists_with_similarity)
		# If the most accurate artist doesn't have at least 500 points, discard the loop cycle and iterate the next collection in the list
		# This is done to immediately eliminate covers or bootlegs of collections
		if artists_with_similarity != [] and artists_with_similarity[0][0] > 500:
			collection_similarity += artists_with_similarity[0][0]
		else:
			continue

		title_input = bare_bones(query_title) # Strips down the title
		title_reference = remove_feat(collection.title) # Removes all features included in the title
		collection_similarity += calculate_similarity(bare_bones(title_reference), title_input) # Calculates their similarity and adds it to the overall score

		if query_year != None and collection.release_year != None: # Since these are boolean values, you can just check them and then add the points or not
			if query_year == collection.release_year:
				collection_similarity += 1000

		data_with_similarity.append([collection_similarity, collection])

	data_with_similarity = sort_similarity_lists(data_with_similarity) # Sort the list from the biggest to smallest score
	if data_with_similarity != []: # Check if the list is empty
		top_result = data_with_similarity[0]
		top_data = top_result[1]
		filtering_time = current_unix_time_ms() - start_time
		if percentage(max_score, top_result[0]) > 30: # Check if the similarity percentage is above 30%, if it's not discard the collection and return an empty object
			top_collection = Collection(
				service = top_data.service,
				type = top_data.type,
				urls = top_data.urls,
				ids = top_data.ids,
				title = top_data.title,
				artists = top_data.artists,
				release_year = top_data.release_year,
				cover = top_data.cover,
				genre = top_data.genre,
				meta = Meta(
					service = top_data.service,
					request = top_data.meta.request,
					http_code = top_data.meta.http_code,
					processing_time = top_data.meta.processing_time[top_data.service] + filtering_time,
					filter_confidence_percentage = {service: percentage(max_score, top_result[0])}
				)
			)
			
			return top_collection
		else: 
			empty_response = Empty(
				service = service,
				meta = Meta(
					service = top_data[1].service,
					request = top_data[1].meta.request,
					processing_time = top_data[1].meta.processing_time,
					filter_confidence_percentage = {service: percentage(max_score, top_result[0])},
					http_code = 204
				)
			)
			await log(empty_response)
			return empty_response
		
	else: # Return empty if there is no collection that has passed filtering
		empty_response = Empty(
			service = service,
			meta = Meta(
				service = service,
				request = query_request,
				processing_time = 0,
				filter_confidence_percentage = {service: 0.0},
				http_code = 204
			)
		)
		await log(empty_response)
		return empty_response

print('[ServiceCatalogAPI] Filtering module initialized')
