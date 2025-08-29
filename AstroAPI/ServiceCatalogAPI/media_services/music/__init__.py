"""
	# Music Services

	Summons and initializes the Spotify, Apple Music, Deezer and YouTube Music music API-s, alongside the Global Music API Interface.
"""


from AstroAPI.ServiceCatalogAPI.media_services.music.global_io import global_io
from AstroAPI.ServiceCatalogAPI.media_services.music.spotify import spotify
from AstroAPI.ServiceCatalogAPI.media_services.music.apple_music import apple_music
from AstroAPI.ServiceCatalogAPI.media_services.music.deezer import deezer
from AstroAPI.ServiceCatalogAPI.media_services.music.youtube_music import youtube_music

print('[ServiceCatalogAPI] Music services summoned')