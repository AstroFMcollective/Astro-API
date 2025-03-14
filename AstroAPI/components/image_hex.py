import aiohttp
from PIL import Image
import numpy as np
from io import BytesIO



"""
	--- THE IMAGE HEX COLOR CALCULATOR ---

	A simple async script to get the hex color code of
	the average color of an image. Useful for embedding
	Astro API output data on something like a website.

	This used to be a Discord client thing, but it was
	built into the API in the a2.2 update because
	technical limitations disallowed the client's function
	to be asynchronous. It never caused any obnoxious
	blocking, but this is a nicer approach in general.
"""



async def image_hex(image_url: str, quality: int = 5):
	"""
	# Song filtering function

		This is a built-in internal Astro API function which generates a hex code of the average color
		of a cover.

		 :param image_url: The URL string of the cover.
		 :param quality: Optional. The factor at which the function reduces the cover's resolution. Bigger the number, smaller the resolution.
	"""
	async with aiohttp.ClientSession() as session:
		async with session.get(url = image_url) as response:
			if response.status == 200:
				image_bytes = await response.read()
				image = Image.open(BytesIO(image_bytes))

				width, height = image.size
				new_width = width // quality
				new_height = height // quality
				image = image.resize((new_width, new_height))

				pixels = image.convert('RGB').getdata()
				average_color = np.mean(pixels, axis = 0).astype(int)

				hex_color = "{:02x}{:02x}{:02x}".format(*average_color)
				return int(hex_color, base = 16)
			else:
				return 0xf5c000 # The iconic Astro Yellow - #F5C000