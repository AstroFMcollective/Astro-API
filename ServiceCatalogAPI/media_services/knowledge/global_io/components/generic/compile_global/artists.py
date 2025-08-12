from ServiceCatalogAPI.components import *
from ServiceCatalogAPI.media_services.knowledge.global_io.components.generic.about import service as gservice, component as gcomponent
from ServiceCatalogAPI.media_services.knowledge.global_io.components.generic import *



def compiled_artists(request: dict, unlabeled_artists: dict) -> list[Artist]:	
	# Results order based on service priority
	# Some services have lesser quality or straight-up do not carry certain information, so we prioritize the ones who do
	all_services = [spotify.service, genius.service]
	artist_lift_from_template = [spotify.service, genius.service]
	profile_picture_lift_from_template = [genius.service, spotify.service]
	general_order = [spotify.service, genius.service]
	name_order = [spotify.service, genius.service]
	genre_order = [spotify.service, genius.service]

	labeled_artists = {artists[0].service: artists for artists in unlabeled_artists}


	# Removing services from order if there were no results from those services
	for service in all_services:
		if service not in labeled_artists:
			artist_lift_from_template.remove(service)
			profile_picture_lift_from_template.remove(service)
			general_order.remove(service)
			name_order.remove(service)
			genre_order.remove(service)
	
	artists = []
	new_artists = []

	# Preload an existing artist list
	for service in artist_lift_from_template:
		if artists == []:
			artists = labeled_artists[service]

	# Processing each artist object
	for artist in artists:
		artist_index = artists.index(artist)

		# Declaring variables to hold the results
		profile_picture = None
		result_name = None
		result_urls = {}
		result_ids = {}
		result_profile_picture_hq_urls = {}
		result_profile_picture_lq_urls = {}
		result_genre = None
		result_processing_time = {}
		result_confidence = {}

		# Iterating through the ordered list to find the first non-None result for each field
		for service_index in range(len(general_order)):
			if result_name is None:
				if artist_index < len(labeled_artists[name_order[service_index]]):
					result_name = labeled_artists[name_order[service_index]][artist_index].name
			if result_genre is None:
				if artist_index < len(labeled_artists[genre_order[service_index]]):
					result_genre = labeled_artists[genre_order[service_index]][artist_index].genre
			if result_urls == {}:
				for result in unlabeled_artists:
					for obj in result:
						result_urls[obj.service] = obj.urls[obj.service]
				result_urls = sort_dicts(result_urls, general_order)
			if result_ids == {}:
				for result in unlabeled_artists:
					for obj in result:
						result_ids[obj.service] = obj.ids[obj.service]
				result_ids = sort_dicts(result_ids, general_order)
			if result_processing_time == {}:
				for result in unlabeled_artists:
					for obj in result:
						result_processing_time[obj.service] = obj.meta.processing_time[obj.service]
				result_processing_time = sort_dicts(result_processing_time, general_order)
			if result_confidence == {}:
				for result in unlabeled_artists:
					for obj in result:
						result_confidence[obj.service] = obj.meta.filter_confidence_percentage[obj.service]
				result_confidence = sort_dicts(result_confidence, general_order)
			if profile_picture is None:
				if artist_index < len(labeled_artists[profile_picture_lift_from_template[service_index]]):
					# This catastrophe attempts to fill in HQ and LQ URLs from all prioritized services if a profile picture was found
					# ts pmo 🥀
					profile_picture = labeled_artists[profile_picture_lift_from_template[service_index]][artist_index].profile_picture
					if profile_picture is not None:
						# Populate HQ URLs if not already set
						if not result_profile_picture_hq_urls:
							for service in profile_picture_lift_from_template:
								artist_list = labeled_artists.get(service)
								if artist_list and artist_index < len(artist_list):
									obj = artist_list[artist_index]
									# Add HQ URL for this service if available
									if obj.profile_picture and obj.profile_picture.hq_urls.get(service):
										result_profile_picture_hq_urls[service] = obj.profile_picture.hq_urls[service]
							result_profile_picture_hq_urls = sort_dicts(result_profile_picture_hq_urls, general_order)
						# Populate LQ URLs if not already set
						if not result_profile_picture_lq_urls:
							for service in profile_picture_lift_from_template:
								artist_list = labeled_artists.get(service)
								if artist_list and artist_index < len(artist_list):
									obj = artist_list[artist_index]
									# Add LQ URL for this service if available
									if obj.profile_picture and obj.profile_picture.lq_urls.get(service):
										result_profile_picture_lq_urls[service] = obj.profile_picture.lq_urls[service]
							result_profile_picture_lq_urls = sort_dicts(result_profile_picture_lq_urls, general_order)
		
		# Building the new Artist object with the results
		artist = Artist(
			service = gservice,
			name = result_name,
			urls = result_urls,
			ids = result_ids,
			profile_picture = ProfilePicture(
				service = gservice,
				user_type = 'artist',
				hq_urls = result_profile_picture_hq_urls,
				lq_urls = result_profile_picture_lq_urls,
				meta = Meta(
					service = gservice,
					request = request,
					processing_time = result_processing_time,
					filter_confidence_percentage = {gservice: 100.0},
					http_code = 200
				)
			) if profile_picture is not None else None,
			genre = result_genre,
			meta = Meta(
				service = gservice,
				request = request,
				processing_time = result_processing_time,
				filter_confidence_percentage = {gservice: 100.0},
				http_code = 200
			)
		)

		new_artists.append(artist)



	return new_artists