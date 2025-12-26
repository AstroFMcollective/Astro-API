from AstroAPI.ServiceCatalogAPI.components import *
from AstroAPI.InternalComponents.SystemMediaObjects import *
from AstroAPI.InternalComponents.Legacy import *
from .components.generic import *

from .components.get.song_preview import get_song_preview

class AppleMusic:
	def __init__(self):
		self.service = service
		self.component = component

	async def get_song_preview(self, id: str, country_code: str = 'us') -> str | Empty | Error:
		"""
            # Apple Music Snitch Song Preview

            Get the song preview URL from Apple Music (via the iTunes API).

            :param id: Song ID.
            :param country_code: The country code of the country in which you want to conduct the lookup.
        """
		return await get_song_preview(id = id, country_code = country_code)



apple_music = AppleMusic()

print(f'[SnitchAPI] {component} initialized')
