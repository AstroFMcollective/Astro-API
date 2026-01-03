from AstroAPI.InternalComponents.SystemMediaObjects import *
from AstroAPI.InternalComponents.Legacy import *
from AstroAPI.ServiceCatalogAPI.media_services.music.apple_music.components.generic import *
from AstroAPI.ServiceCatalogAPI.components import *

import aiohttp



async def get_search_wrapper(term: str, country: str, media: str = 'all', entity: str = 'all', limit: int = 50, lang: str = 'en_us', version: int = 2, explicit: bool = True):

	"""
		Wrapper for iTunes API search endpoint https://developer.apple.com/library/archive/documentation/AudioVideo/Conceptual/iTuneSearchAPI/Searching.html#//apple_ref/doc/uid/TP40017632-CH5-SW1
		
		:param term: The URL-encoded text string you want to search for. For example: jack+johnson.
		:param country: The two-letter country code for the store you want to search. The search uses the default store front for the specified country. For example: US. The default is US.
		:param media: The media type you want to search for. For example: movie. The default is all.
		:param entity: The type of results you want returned, relative to the specified media type. For example: movieArtist for a movie media type search. The default is the track entity associated with the specified media type.
		:param limit: The number of search results you want the iTunes Store to return. For example: 25. The default is 50.
		:param lang: The language, English or Japanese, you want to use when returning search results. Specify the language using the five-letter codename. For example: en_us. The default is en_us (English).
		:param version: The search result key version you want to receive back from your search. The default is 2.
		:param explicit: A flag indicating whether or not you want to include explicit content in your search results. The default is Yes (True).
	"""

	request = {
		'term': term,
		'country': country,
		'media': media,
		'entity': entity,
		'limit': limit,
		'lang': lang,
		'version': version,
		'explicit': 'Yes' if explicit else 'No'
	}
	start_time = current_unix_time_ms()
	
	try:
		async with aiohttp.ClientSession() as session:
			api_url = f'{api}/search'
			api_params = request
			timeout = aiohttp.ClientTimeout(total = 30) # Set a timeout for the HTTP request
			async with session.get(url = api_url, timeout = timeout, params = api_params) as response:
				lookup_json = await response.json(content_type = 'text/javascript')
				return lookup_json

	# Handle any exceptions that occur during the process
	except Exception as error:
		error = Error(
			service = service,
			component = component,
			error_msg = f'Error when doing generic GET request: "{error}"',
			meta = Meta(
				service = service,
				request = request,
				http_code = 500,
				processing_time = {service: current_unix_time_ms() - start_time}
			)
		)
		await log(error, [discord.File(fp = StringIO(json.dumps(lookup_json, indent = 4)), filename = f'{term}.json')])
		return error
