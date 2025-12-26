from AstroAPI.SnitchAPI.components import *
from AstroAPI.InternalComponents.SystemMediaObjects import *
from AstroAPI.InternalComponents.Legacy import *
from .components.generic import *

from .components.check.audio import check_audio

class SubmitHub:
	def __init__(self):
		self.service = service
		self.component = component

	async def check_audio(self, audio_url: str) -> Analysis | Empty | Error:
		"""
            # SubmitHub Snitch Song Checker

            Check whether an audio file is AI-generated via SubmitHub.

            :param audio_url: URL of the audio file you want to check.
        """
		return await check_audio(audio_url = audio_url)



submithub = SubmitHub()

print(f'[SnitchAPI] {component} initialized')
