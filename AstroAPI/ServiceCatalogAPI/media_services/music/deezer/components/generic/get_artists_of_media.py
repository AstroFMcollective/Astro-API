from .about import service
from AstroAPI.ServiceCatalogAPI.components import *

def get_artists_of_media(request: dict, artists_json: dict):
	"""
		If you need to compile a list of artists, use this
	"""
	# Initialize an empty list to store Artist objects
	song_artists = []
	# Iterate over each artist in the provided artists JSON
	for artist in artists_json:
		song_artists.append(
			Artist(
				service = service,
				urls = artist['link'],
				ids = artist['id'],
				name = artist['name'],
				profile_picture = ProfilePicture(
					service = service,
					user_type = 'artist',
					hq_urls = artist['picture_xl'],
					lq_urls = artist['picture_medium'],
					meta = Meta(
						service = service,
						request = request,
						processing_time = 0,
						filter_confidence_percentage = 100.0,
						http_code = 200 
					)
				),
				meta = Meta(
					service = service,
					request = request,
					processing_time = 0,
					filter_confidence_percentage = 100.0,
					http_code = 200 
				)
			)
		)

	return song_artists