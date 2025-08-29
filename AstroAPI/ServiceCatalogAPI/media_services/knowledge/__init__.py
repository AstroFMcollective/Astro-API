"""
	# Knowledge Services

	Summons and initializes the Spotify and Genius knowledge API-s, alongside the Global Knowledge API Interface.
"""


from AstroAPI.ServiceCatalogAPI.media_services.knowledge.global_io import global_io
from AstroAPI.ServiceCatalogAPI.media_services.knowledge.spotify import spotify
from AstroAPI.ServiceCatalogAPI.media_services.knowledge.genius import genius

print('[ServiceCatalogAPI] Knowledge services summoned')
