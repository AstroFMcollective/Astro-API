"""
	# Detection Services

	Summons and initializes the SightEngine, SubmitHub and Apple Music API-s, alongside the Global API Interface.
"""


from AstroAPI.SnitchAPI.detection_services.image import sightengine
from AstroAPI.SnitchAPI.detection_services.audio import submithub, apple_music
from AstroAPI.SnitchAPI.detection_services.global_io import global_io


print('[SnitchAPI] Generative AI detection services summoned')