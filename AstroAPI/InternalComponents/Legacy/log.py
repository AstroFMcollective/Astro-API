import discord as discord
from discord import Webhook
from AstroAPI.InternalComponents.Legacy.ini import config, keys, text
import aiohttp



"""
	--- THE API LOGGING FUNCTION ---

	Like all software, Astro is not perfect, despite our best efforts.
	But when something goes wrong, two things can happen:

	  1. Astro will make a log using the log command down below in the #api-logs channel
	  2. A catastrophic error that takes the entire API down (hopefully never happens 🤞)

	log() is a simple command that makes logs regarding API activity.

	It leverages Discord's webhook system to send them [logs] into a predefined logging channel.

	This function is right now pretty crude and it could be better, but it works well.
"""



async def log(media: object, files: list = None):
	async with aiohttp.ClientSession() as session:
		deployment_channel = config['system']['deployment_channel']
		api_dev_ping = '<@&1330182314831122492>'
		try:
			embed = discord.Embed(
				title = f'Astro Service Catalog API - `{media.type}`', # TODO: rn this is hard coded to only work with the service catalog api
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
				if files is not None:
					await webhook.send(api_dev_ping, embed = embed, username = 'Astro API', avatar_url = text['images']['astro_trans'], files = files)
				else:
					await webhook.send(api_dev_ping, embed = embed, username = 'Astro API', avatar_url = text['images']['astro_trans'])
				return

			elif media.type == 'empty_response':
				request = '\n'.join([f'{parameter}: `{media.meta.request[parameter]}`' for parameter in list(media.meta.request.keys())])
				embed.add_field(
					name = 'Request (parameters)',
					value = f'{request}',
					inline = False
				)
				api_dev_ping = ''

				webhook = Webhook.from_url(url = keys['webhooks'][f'{deployment_channel}'], session = session)
				if files is not None:
					await webhook.send(api_dev_ping, embed = embed, username = 'Astro API', avatar_url = text['images']['astro_trans'], files = files)
				else:
					await webhook.send(api_dev_ping, embed = embed, username = 'Astro API', avatar_url = text['images']['astro_trans'])
				return
		except:
			try:
				# For some reason this function can fail in prod
				# Something something 1024 character limit being tripped
				# I cannot recreate it locally, so this is my solution
				embed_text = f'# Astro Service Catalog API - {media.type}'
				embed_text += f'\n**Service**: {text['api_tag'][media.service]}'
				embed_text += f'\n**Service**'
				if media.type == 'error':
					embed_text += f'\n**HTTP code**: `{media.meta.http_code}`'
					embed_text += f'\n**Error message**: `{media.error_msg}`'
					
					request = '\n'.join([f'{parameter}: `{media.meta.request[parameter]}`' for parameter in list(media.meta.request.keys())])

					embed_text += f'\n\nRequest (parameters):\n'
					embed_text += request


					
					webhook = Webhook.from_url(url = keys['webhooks'][f'{deployment_channel}'], session = session)
					if files is not None:
						await webhook.send(f'{api_dev_ping}\n{embed_text}', username = 'Astro API', avatar_url = text['images']['astro_trans'], files = files)
					else:
						await webhook.send(f'{api_dev_ping}\n{embed_text}', username = 'Astro API', avatar_url = text['images']['astro_trans'])
					return

				elif media.type == 'empty_response':
					request = '\n'.join([f'{parameter}: `{media.meta.request[parameter]}`' for parameter in list(media.meta.request.keys())])

					embed_text += f'\n\nRequest (parameters):\n'
					embed_text += request

					api_dev_ping = ''

					webhook = Webhook.from_url(url = keys['webhooks'][f'{deployment_channel}'], session = session)
					if files is not None:
						await webhook.send(api_dev_ping, username = 'Astro API', avatar_url = text['images']['astro_trans'], files = files)
					else:
						await webhook.send(api_dev_ping, username = 'Astro API', avatar_url = text['images']['astro_trans'])
					return
			except:
				# Okay if this really REALLY doesn't work just give up
				webhook = Webhook.from_url(url = keys['webhooks'][f'{deployment_channel}'], session = session)
				await webhook.send(f"{api_dev_ping} Logging keeps failing for some reason, here's the json of the response", username = 'Astro API', avatar_url = text['images']['astro_trans'], files = media.json)
				return
		
print('[ServiceCatalogAPI] Logging to Discord initialized')
