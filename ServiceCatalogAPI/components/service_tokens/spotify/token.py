from ServiceCatalogAPI.components import *
from ServiceCatalogAPI.components.ini import keys
from .components.about import *
from asyncio import run
import aiohttp



class Token:
	def __init__(self, client_id: str, client_secret: str):
		self.service = service
		self.component = component
		self.client_id = client_id
		self.client_secret = client_secret
		self.token = None
		self.token_expiration_date = None
		run(self.get_token())

	async def get_token(self) -> str:
		if self.token == None or (self.token_expiration_date == None or current_unix_time() > self.token_expiration_date):
			async with aiohttp.ClientSession() as session:
				request = 'get_token'
				api_url = api
				api_data = f'grant_type=client_credentials&client_id={self.client_id}&client_secret={self.client_secret}'
				api_headers = {'Content-Type': 'application/x-www-form-urlencoded'}
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



spotify_token = Token(
	client_id = keys['spotify']['id'],
	client_secret = keys['spotify']['secret']
)