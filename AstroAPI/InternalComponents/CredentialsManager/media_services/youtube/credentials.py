from AstroAPI.InternalComponents.Legacy import *
from AstroAPI.InternalComponents.Legacy.ini import keys
from AstroAPI.InternalComponents.Legacy.time import current_unix_time
from .components.about import *
from ytmusicapi import YTMusic, OAuthCredentials
from googleapiclient import *
import aiohttp
import json



class Credentials:
	def __init__(self, client_id: str, client_secret: str, api_key: str, oauth_path: str):
		self.service = service
		self.component = component
		self.client_id = client_id
		self.client_secret = client_secret
		self.api_key = api_key
		self.oauth_path = oauth_path
		self.access_token = None
		self.refresh_token = None
		with open(oauth_path, 'r') as file:
			self.oauth = json.load(file)

	async def initialize_ytmusicapi(self):
		# await self.refresh_access_token()
		return YTMusic(
			auth = self.oauth,
			oauth_credentials = 
				OAuthCredentials(
					client_id = self.client_id,
					client_secret = self.client_secret
				)
			)
	
	async def refresh_access_token(self):
		async with aiohttp.ClientSession() as session:
			request = {'request': 'refresh_access_token'}
			api_url = api
			api_data = {
				'client_id': self.client_id,
				'client_secret': self.client_secret,
				'refresh_token': self.refresh_token,
				'grant_type': 'refresh_token'
			}
			api_headers = {
				'Content-Type': 'application/x-www-form-urlencoded'
			}
			start_time = current_unix_time_ms()
			async with session.post(url = api_url, data = api_data, headers = api_headers) as response:
				if response.status == 200:
					json_response = await response.json()
					with open(f'{path}/components/oauth.json', 'r+') as oauth_file:
						oauth_data = json.load(oauth_file)
						oauth_data['access_token'] = json_response.get('access_token')
						oauth_data['expires_in'] = json_response.get('expires_in')
						oauth_data['token_type'] = json_response.get('token_type')
						oauth_file.seek(0)
						json.dump(oauth_data, oauth_file, indent = 4)
						oauth_file.truncate()
				
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



with open(f'{path}/components/credentials.json', 'r') as file:
	creds = json.load(file)
youtube_credentials = Credentials(creds['id'], creds['secret'], creds['api_key'], f'{path}/components/oauth.json')