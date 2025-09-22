from AstroAPI.InternalComponents.Legacy import *
from AstroAPI.InternalComponents.Legacy.ini import keys
from .components.about import *
import aiohttp
import base64



class Token:
	def __init__(self, client_id: str, client_secret: str):
		self.service = service
		self.component = component
		self.client_id = client_id
		self.client_secret = client_secret
		self.token = None
		self.token_expiration_date = None

	async def get_token(self) -> str:
		if self.token == None or (self.token_expiration_date == None or current_unix_time() > self.token_expiration_date):
			creds = f'{self.client_id}:{self.client_secret}='
			b64_creds = base64.b64encode(creds.encode()).decode()
			async with aiohttp.ClientSession() as session:
				request = {'request': 'get_token'}
				api_url = api
				api_data = {'grant_type': 'client_credentials'}
				api_headers = {'Authorization': f'Basic {b64_creds}'}
				start_time = current_unix_time_ms()

				async with session.post(url = api_url, data = api_data, headers = api_headers) as response:
					if response.status == 200:
						json_response = await response.json()
						self.token = json_response['access_token']
						self.token_expiration_date = current_unix_time() + int(json_response['expires_in'])
					
					else:
						error = Error(
							service = self.service,
							component = self.component,
							error_msg = "HTTP error when getting token",
							meta = Meta(
								service = self.service,
								request = request,
								processing_time = current_unix_time_ms() - start_time,
								http_code = response.status
							)
						)
						await log(error)
						return error

		return self.token



tidal_token = Token(
	client_id = keys['tidal']['id'],
	client_secret = keys['tidal']['secret']
)