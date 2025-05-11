import discord as discord
from discord import Webhook
from AstroAPI.components.ini import config, keys, text
import aiohttp



"""
	--- THE API LOGGING FUNCTION ---

	A simple command that makes logs regarding API activity.

	It leverages Discord's webhook system to send them into a logging channel.

	This function is right now pretty crude and it could be better, but it works well.
"""



async def log(media: object):
	async with aiohttp.ClientSession() as session:
		deployment_channel = config['system']['deployment_channel']
		embed = discord.Embed(
			title = f'Astro API - `{media.type}`',
			colour = 0x0097f5,
		)
		embed.add_field(
			name = 'Service',
			value = f'{text['api_tag'][media.service]}',
			inline = False
		)
		if media.type == 'error':
			report = [
				f'HTTP code: `{media.meta.http_code}`',
				f'Error message: `{media.error_msg}`'
			]
			embed.add_field(
				name = 'Report',
				value = f'{'\n'.join(report)}',
				inline = False
			)

			request = '\n'.join([f'{parameter}: `{media.meta.request[parameter]}`' for parameter in list(media.meta.request.keys())])

			embed.add_field(
				name = 'Request (parameters)',
				value = f'{request}',
				inline = False
			)
			
			webhook = Webhook.from_url(url = keys['webhooks'][f'{deployment_channel}'], session = session)
			await webhook.send('<@&1330182314831122492>', embed = embed, username = 'Astro API', avatar_url = text['images']['astro_trans'])
			return

		elif media.type == 'empty_response':
			request = '\n'.join([f'{parameter}: `{media.meta.request[parameter]}`' for parameter in list(media.meta.request.keys())])
			embed.add_field(
				name = 'Request (parameters)',
				value = f'{request}',
				inline = False
			)

			webhook = Webhook.from_url(url = keys['webhooks'][f'{deployment_channel}'], session = session)
			await webhook.send(embed = embed, username = 'Astro API', avatar_url = text['images']['astro_trans'])
			return