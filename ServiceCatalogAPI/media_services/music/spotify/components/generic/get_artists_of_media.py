from .about import service
from ServiceCatalogAPI.components import *

def get_artists_of_media(request: dict, artists_json: dict):
	"""
		If you need to compile a list of artists, use this
	"""
	# Initialize an empty list to store Artist objects
	song_artists = []
	# Iterate over each artist in the provided artists_json dictionary
	for artist in artists_json:
		# Create an Artist object with relevant information and metadata
		song_artists.append(
			Artist(
				service = service,
				urls = artist['external_urls']['spotify'],
				ids = artist['id'],
				name = artist['name'],
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