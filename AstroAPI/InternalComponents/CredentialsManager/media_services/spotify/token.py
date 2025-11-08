from AstroAPI.InternalComponents.Legacy import *
from AstroAPI.InternalComponents.Legacy.ini import keys
from .components.about import *
import aiohttp



class Token:
	def __init__(self):
		self.service = service
		self.component = component
		self.client_id = None
		self.client_secret = None
		self.token = None
		self.token_expiration_date = None

	async def get_token(self) -> str:
		if self.token == None or (self.token_expiration_date == None or current_unix_time() > self.token_expiration_date):
			await self.get_credentials()
			async with aiohttp.ClientSession() as session:
				request = {'request': 'get_token'}
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
	
	async def get_credentials(self) -> None:
		async with aiohttp.ClientSession() as session:
			request = {'request': 'get_credentials'}
			creds_url = keys['cred_endpoints'][self.service]
			start_time = current_unix_time_ms()
			async with session.get(url = creds_url) as response:
				if response.status == 200:
					json_response = await response.json()
					self.client_id = json_response['id']
					self.client_secret = json_response['secret']
					
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



spotify_token = Token()