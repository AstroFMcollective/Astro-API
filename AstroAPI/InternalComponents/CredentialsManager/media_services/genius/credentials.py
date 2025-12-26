from AstroAPI.ServiceCatalogAPI.components import *
from AstroAPI.InternalComponents.SystemMediaObjects import *
from AstroAPI.InternalComponents.Legacy import *
from AstroAPI.InternalComponents.Legacy.ini import keys
from .components.about import *
import aiohttp



class Credentials:
	def __init__(self):
		self.service = service
		self.component = component
		self.client_token = None
	
	async def get_credentials(self) -> None:
		if self.client_token == None:
			async with aiohttp.ClientSession() as session:
				request = {'request': 'get_credentials'}
				creds_url = keys['cred_endpoints'][self.service]
				start_time = current_unix_time_ms()
				async with session.get(url = creds_url) as response:
					if response.status == 200:
						json_response = await response.json()
						self.client_token = json_response['token']
						
					else:
						error = Error(
							service = self.service,
							component = self.component,
							error_msg = "HTTP error when getting credentials",
							meta = Meta(
								service = self.service,
								request = request,
								processing_time = current_unix_time_ms() - start_time,
								http_code = response.status
							)
						)
						await log(error)



genius_credentials = Credentials()