from AstroAPI.InternalComponents.Legacy import *
from AstroAPI.InternalComponents.Legacy.ini import keys
from AstroAPI.InternalComponents.Legacy.time import current_unix_time
from .components.about import *
from ytmusicapi import YTMusic, OAuthCredentials
import aiohttp
import json
import requests, asyncio




class Credentials:
	def __init__(self):
		self.service = service
		self.component = component
		self.client_id = None
		self.client_secret = None
		self.api_key = None
		self.oauth = None
		self.browser = None
		self.ytmusicapi = self.initialize_ytmusicapi()

	def initialize_ytmusicapi(self):
		self.get_browser()
		self.get_oauth()
		self.get_credentials()
		# A YouTube API update broke the way ytmusicapi does authentication, so for the time being we're
		# emulating a browser session by reusing sushi's Firefox request headers. If these break, check
		# if the OAuth issues have been solved. If not, make some new headers.
		# return YTMusic(
		# 	auth = self.oauth,
		# 	oauth_credentials = 
		# 		OAuthCredentials(
		# 			client_id = self.client_id,
		# 			client_secret = self.client_secret
		# 		)
		# 	)
		return YTMusic(auth = self.browser)
	
	async def refresh_access_token(self): # Unused and doesn't work right now
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
	
	def get_browser(self) -> None:
		if self.browser is None:
			request = {'request': 'get_credentials'}
			creds_url = keys['cred_endpoints'][f'{self.service}_browser']
			start_time = current_unix_time_ms()
			try:
				response = requests.get(creds_url, timeout=10)
				if response.status_code == 200:
					json_response = response.json()
					self.browser = json_response
				else:
					error = Error(
						service = self.service,
						component = self.component,
						error_msg = "HTTP error when getting browser credentials",
						meta = Meta(
							service = self.service,
							request = request,
							processing_time = current_unix_time_ms() - start_time,
							http_code = response.status_code
						)
					)
					# schedule or run logging depending on loop state
					try:
						loop = asyncio.get_running_loop()
					except RuntimeError:
						asyncio.run(log(error))
					else:
						loop.create_task(log(error))
			except requests.RequestException as e:
				error = Error(
					service = self.service,
					component = self.component,
					error_msg = f"Request error when getting browser credentials: {e}",
					meta = Meta(
						service = self.service,
						request = request,
						processing_time = current_unix_time_ms() - start_time,
						http_code = None
					)
				)
				try:
					loop = asyncio.get_running_loop()
				except RuntimeError:
					asyncio.run(log(error))
				else:
					loop.create_task(log(error))

	def get_oauth(self) -> None:
		if self.oauth is None:
			request = {'request': 'get_credentials'}
			creds_url = keys['cred_endpoints'][f'{self.service}_oauth']
			start_time = current_unix_time_ms()
			try:
				response = requests.get(creds_url, timeout=10)
				if response.status_code == 200:
					json_response = response.json()
					self.oauth = json_response
				else:
					error = Error(
						service = self.service,
						component = self.component,
						error_msg = "HTTP error when getting OAuth credentials",
						meta = Meta(
							service = self.service,
							request = request,
							processing_time = current_unix_time_ms() - start_time,
							http_code = response.status_code
						)
					)
					try:
						loop = asyncio.get_running_loop()
					except RuntimeError:
						asyncio.run(log(error))
					else:
						loop.create_task(log(error))
			except requests.RequestException as e:
				error = Error(
					service = self.service,
					component = self.component,
					error_msg = f"Request error when getting OAuth credentials: {e}",
					meta = Meta(
						service = self.service,
						request = request,
						processing_time = current_unix_time_ms() - start_time,
						http_code = None
					)
				)
				try:
					loop = asyncio.get_running_loop()
				except RuntimeError:
					asyncio.run(log(error))
				else:
					loop.create_task(log(error))

	def get_credentials(self) -> None:
		if self.client_id is None:
			request = {'request': 'get_credentials'}
			creds_url = keys['cred_endpoints'][f'{self.service}_credentials']
			start_time = current_unix_time_ms()
			try:
				response = requests.get(creds_url, timeout=10)
				if response.status_code == 200:
					json_response = response.json()
					self.client_id = json_response.get('id')
					self.client_secret = json_response.get('secret')
					self.api_key = json_response.get('api_key')
				else:
					error = Error(
						service = self.service,
						component = self.component,
						error_msg = "HTTP error when getting OAuth credentials",
						meta = Meta(
							service = self.service,
							request = request,
							processing_time = current_unix_time_ms() - start_time,
							http_code = response.status_code
						)
					)
					try:
						loop = asyncio.get_running_loop()
					except RuntimeError:
						asyncio.run(log(error))
					else:
						loop.create_task(log(error))
			except requests.RequestException as e:
				error = Error(
					service = self.service,
					component = self.component,
					error_msg = f"Request error when getting credentials: {e}",
					meta = Meta(
						service = self.service,
						request = request,
						processing_time = current_unix_time_ms() - start_time,
						http_code = None
					)
				)
				try:
					loop = asyncio.get_running_loop()
				except RuntimeError:
					asyncio.run(log(error))
				else:
					loop.create_task(log(error))



youtube_credentials = Credentials()