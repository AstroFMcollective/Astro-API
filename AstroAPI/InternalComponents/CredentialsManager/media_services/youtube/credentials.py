from AstroAPI.ServiceCatalogAPI.components import *
from AstroAPI.InternalComponents.SystemMediaObjects import *
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
		self.PREFER_LOCAL_CREDS = True
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
	
	def get_browser(self) -> None:
		if self.PREFER_LOCAL_CREDS:
			path = credentials['servicecatalogapi'][service]
			self.browser = path['browser']
		else:
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
		if self.PREFER_LOCAL_CREDS:
			path = credentials['servicecatalogapi'][service]
			self.oauth = path['oauth']
		else:
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
		if self.PREFER_LOCAL_CREDS:
			path = credentials['servicecatalogapi'][service]
			self.client_id = path['credentials']['id']
			self.client_secret = path['credentials']['secret']
			self.api_key = path['credentials']['api_key']
		else:
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