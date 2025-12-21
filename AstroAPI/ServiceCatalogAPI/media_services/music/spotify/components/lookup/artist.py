from AstroAPI.InternalComponents.Legacy import *
from AstroAPI.ServiceCatalogAPI.components.generic import *
from AstroAPI.ServiceCatalogAPI.components.spotify import *
from AstroAPI.InternalComponents.CredentialsManager.media_services.spotify.token import spotify_token
from AstroAPI.ServiceCatalogAPI.media_services.music.spotify.components.generic import *
import aiohttp



async def lookup_artist(id: str, country_code: str = 'us') -> object:
	# Prepare the request metadata
	request = {'request': 'lookup_artist', 'id': id, 'country_code': country_code}
	# Lookup JSON variable for later debugging
	lookup_json = None
	# Record the start time for processing time calculation
	start_time = current_unix_time_ms()
	
	try:
		async with aiohttp.ClientSession() as session:
			# Prepare request data and Spotify API endpoint
			api_url = f'{api}/artists/{id}'
			api_headers = {'Authorization': f'Bearer {await spotify_token.get_token()}'}
			timeout = aiohttp.ClientTimeout(total = 30)

			# Make the GET request to the Spotify API
			async with session.get(url = api_url, headers = api_headers, timeout = timeout) as response:
				lookup_json = await response.json()
				if response.status == 200:
					# Parse the JSON response if the request was successful
					artist = lookup_json
					if 'error' not in artist: # Check if there was any song data returned
						# Extract artist details from the response
						artist_url = artist['external_urls']['spotify']
						artist_id = artist['id']
						artist_name = artist['name']
						artist_genre = artist['genre'][0] if artist['genre'] != [] else None

						if len(artist['images']) > 0:
							artist_pfp = ProfilePicture(
								service = service,
								user_type = 'artist',
								hq_urls = artist['images'][0]['url'],
								lq_urls = artist['images'][len(artist['images'])-1]['url'],
								meta = Meta(
									service = service,
									request = request,
									processing_time = 0,
									filter_confidence_percentage = 100.0,
									http_code = 200 
								)
							)
						else:
							artist_pfp = None

						# Return an Artist object with the extracted data and metadata
						return Artist(
							service = service,
							urls = artist_url,
							ids = artist_id,
							name = artist_name,
							genre = artist_genre,
							profile_picture = artist_pfp,
							meta = Meta(
								service = service,
								request = request,
								processing_time = current_unix_time_ms() - start_time,
								filter_confidence_percentage = {service: 100.0},
								http_code = response.status
							)
						)

					else: # If not, return an empty object and log it
						empty = Empty(
							service = service,
							meta = Meta(
								service = service,
								request = request,
								processing_time = current_unix_time_ms() - start_time,
								http_code = 204
							)
						)
						await log(empty)
						return empty
				
				else:
					# Handle non-200 HTTP responses by returning an Error object
					error = Error(
						service = service,
						component = component,
						error_msg = "HTTP error when looking up artist ID",
						meta = Meta(
							service = service,
							request = request,
							processing_time = current_unix_time_ms() - start_time,
							http_code = response.status
						)
					)
					await log(error, [discord.File(fp = StringIO(json.dumps(lookup_json, indent = 4)), filename = f'{id}.json')])
					return error


	# Handle any exceptions that occur during the lookup process
	except Exception as error:
		error = Error(
			service = service,
			component = component,
			error_msg = f'Error when looking up artist: "{error}"',
			meta = Meta(
				service = service,
				request = request,
				http_code = 500,
				processing_time = {service: current_unix_time_ms() - start_time}
			)
		)
		await log(error, [discord.File(fp = StringIO(json.dumps(lookup_json, indent = 4)), filename = f'{id}.json')])
		return error