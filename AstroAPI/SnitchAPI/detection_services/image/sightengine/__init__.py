from AstroAPI.SnitchAPI.components import *
from AstroAPI.InternalComponents.SystemMediaObjects import *
from AstroAPI.InternalComponents.Legacy import *
from .components.generic import *

from .components.check.image import check_image

class SightEngine:
	def __init__(self):
		self.service = service
		self.component = component

	async def check_image(self, image_url: str) -> Analysis | Empty | Error:
		"""
            # SightEngine Snitch Image Checker

            Check whether an image file is AI-generated via SightEngine.

            :param image_url: URL of the image file you want to check.
        """
		return await check_image(image_url = image_url)



sightengine = SightEngine()

print(f'[SnitchAPI] {component} initialized')
