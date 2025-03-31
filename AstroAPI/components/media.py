from AstroAPI.components.ini import config

missing_image = config['images']['missing_image']
astro_yellow = int(config['color_hex']['astro_yellow'])



"""
	--- MEDIA OBJECTS ---

	This is the reference sheet of all Astro's supported media types.

	This is a more sophisticated method of forming media objects, so devs have to work less
	to get nice, proper media objects. 

	All objects must contain a service, type and meta (technical metadata) variables.
"""



class Error:
	"""
		# Astro Error Object

		This is a built-in Astro API object which identifies errors.
		Use this to return *a thing* when something internally goes wrong.
		JSON representation available.

		 :param	service: The API service in which the object was formed.
		 :param component: The API service component in which the object was formed.
		 :param error_msg: Optional, but recommended. The error message of the error.
		 :param meta: The technical metadata of this object.
	"""
	def __init__(self, service: str, component: str, meta: object, error_msg: str = None) -> object:
		type = 'error'

		self.service = service
		self.type = type
		self.component = component
		self.error_msg = error_msg
		self.meta = meta
		self.json = {
			'service': service,
			'type': type,
			'component': component,
			'error_msg': error_msg,
			'meta': meta.json
		}

class Empty:
	"""
		# Astro Empty Object

		This is a built-in Astro API object which identifies empty responses.
		Use this to return *a thing* when a service you're using doesn't end up
		returning anything/returns an empty response.
		JSON representation available.

		 :param	service: The API service in which the object was formed.
		 :param meta: The technical metadata of this object.
	"""
	def __init__(self, service: str, meta: object) -> object:
		type = 'empty_response'

		self.service = service
		self.type = type
		self.meta = meta
		self.json = {
			'service': service,
			'type': type,
			'meta': meta.json
		}

class Meta:
	"""
		# Astro (Technical) Metadata Object

		This is a built-in Astro API object which identifies technical metadata.
		In it are shoved in stats and values useful for debugging or general
		handling.
		This is pretty much mandatory for every media object.
		JSON representation available.

		 :param	service: The API service in which the parent object was formed.
		 :param request: The request dictionary (json) of all the data used to make the request.
		 :param http_code: Optional. The HTTP code returned by an Astro component.
		 :param processing_time: The amount of time in milliseconds that an Astro component took to form the orignial media object.
		 :param filter_confidence_percentage: Optional. Astro's confidence it got the correct media object.
	"""
	def __init__(self, service: str, request: dict, processing_time: int | dict, filter_confidence_percentage: int | dict = None, http_code: int = None):
		processing_time = {service: processing_time} if isinstance(processing_time, int) else processing_time
		filter_confidence_percentage = {service: filter_confidence_percentage} if isinstance(filter_confidence_percentage, float) else filter_confidence_percentage
		
		self.request = request
		self.http_code = http_code
		self.processing_time = processing_time
		self.filter_confidence_percentage = filter_confidence_percentage
		self.json = {
			'request': request,
			'http_code': http_code,
			'processing_time': processing_time,
			'filter_confidence_percentage': filter_confidence_percentage
		}

class Song:
	"""
		# Astro Song Object

		This is a built-in Astro API object which identifies songs.
		Astro identifies two types of songs: tracks and singles.
		It's an unwritten rule, but Astro should sort tracks as songs off albums, while
		singles are standalone tracks and tracks from EP-s.
		JSON representation available.

		 :param	service: The API service in which the object was formed.
		 :param type: The song type, can either be `track` or `single`.
		 :param urls: The song's URL(s).
		 :param ids: The song's ID(s).
		 :param title: The song's title.
		 :param artists: The song's artists.
		 :param collection: The song's collection (album or EP).
		 :param cover: The song's cover art.
		 :param genre: Optional. The song's genre.
		 :param is_explicit: Optional. Whether the song is explicit or not.
		 :param meta: The technical metadata of the song.
	"""
	def __init__(self, service: str, type: str, urls: str | dict, ids: any | dict, title: str, artists: list[object], cover: object, meta: object, collection: object = None, genre: str = None, is_explicit: bool = None) -> object:
		urls = {service: urls} if not isinstance(urls, dict) else urls
		ids = {service: str(ids)} if not isinstance(ids, dict) else ids
		censored_title = title
		
		self.service = service
		self.type = type
		self.urls = urls
		self.ids = ids
		self.title = title
		self.censored_title = censored_title
		self.artists = artists
		self.collection = collection
		self.cover = cover
		self.genre = genre
		self.is_explicit = is_explicit
		self.meta = meta
		self.json = {
			'service': service,
			'type': type,
			'urls': urls,
			'ids': ids,
			'title': title,
			'censored_title': censored_title,
			'artists': [artist.json for artist in artists],
			'collection': collection.json,
			'cover': cover.json,
			'genre': genre,
			'is_explicit': is_explicit,
			'meta': meta.json
		}

class MusicVideo:
	"""
		# Astro Music Video Object

		This is a built-in Astro API object which identifies music videos.
		JSON representation available.
		
		 :param	service: The API service in which the object was formed.
		 :param urls: The music video's URL(s). To put multiple URL-s in an object, use dicts.
		 :param ids: The music video's ID(s). To put multiple ID-s in an object, use dicts.
		 :param title: The music video's title.
		 :param artists: The music video's artists.
		 :param cover: The music video's thumbnail.
		 :param genre: Optional. The music video's genre.
		 :param is_explicit: Optional. Whether the music video is explicit or not.
		 :param meta: The technical metadata of the music video.
	"""
	def __init__(self, service: str, urls: str | dict, ids: any | dict, title: str, artists: list[object], cover: object, meta: object, is_explicit: bool = None, genre: str = None) -> object:
		type = 'music_video'
		urls = {service: urls} if not isinstance(urls, dict) else urls
		ids = {service: str(ids)} if not isinstance(ids, dict) else ids
		censored_title = title
		
		self.service = service
		self.type = type
		self.urls = urls
		self.ids = ids
		self.title = title
		self.censored_title = censored_title
		self.artists = artists
		self.cover = cover
		self.genre = genre
		self.is_explicit = is_explicit
		self.meta = meta
		self.json = {
			'service': service,
			'type': type,
			'urls': urls,
			'ids': ids,
			'title': title,
			'censored_title': censored_title,
			'artists': [artist.json for artist in artists],
			'cover': cover.json,
			'genre': genre,
			'is_explicit': is_explicit,
			'meta': meta.json
		}

class Collection:
	"""
		# Astro Collection Object

		This is a built-in Astro API object which identifies collections.
		Astro identifies two different collection types: albums and EP-s.
		JSON representation available.

		 :param	service: The API service in which the object was formed.
		 :param type: The collection type, can either be `album` or `ep`.
		 :param urls: The collection's URL(s).
		 :param ids: The collection's ID(s).
		 :param title: The collection's title.
		 :param artists: The collection's artists.
		 :param release_year: Optional. The collection's release year.
		 :param cover_url: The collection's cover art URL.
		 :param cover_color_hex: Optional. The hex code of the average color of the collection's cover art.
		 :param genre: Optional. The collection's genre.
		 :param meta: The technical metadata of the collection.
	"""
	def __init__(self, service: str, type: str, urls: str | dict, ids: any | dict, title: str, artists: list[object], cover: object, meta = object, release_year: int = None, genre: str = None) -> object:
		urls = {service: urls} if not isinstance(urls, dict) else urls
		ids = {service: str(ids)} if not isinstance(ids, dict) else ids
		censored_title = title
		release_year = int(release_year) if release_year != None else None
		
		self.service = service
		self.type = type
		self.urls = urls
		self.ids = ids
		self.title = title
		self.censored_title = censored_title
		self.artists = artists
		self.release_year = release_year
		self.cover = cover
		self.genre = genre
		self.meta = meta
		self.json = {
			'service': service,
			'type': type,
			'urls': urls,
			'ids': ids,
			'title': title,
			'censored_title': censored_title,
			'artists': [artist.json for artist in artists],
			'release_year': release_year,
			'cover': cover.json,
			'genre': genre,
			'meta': meta.json
		}

class Podcast:
	"""
		# Astro Podcast Object

		This is a built-in Astro API object which identifies podcasts.
		JSON representation available.

		 :param	service: The API service in which the object was formed.
		 :param urls: The podcast's URL(s).
		 :param ids: The podcast's ID(s).
		 :param title: The podcast's title.
		 :param publisher: The podcast's publisher.
		 :param cover: The podcast's cover art.
		 :param is_explicit: Optional. Whether the podcast is explicit or not.
		 :param meta: The technical metadata of the podcast.
	"""
	def __init__(self, service: str, urls: str | dict, ids: any | dict, title: str, publisher: str, cover: object, meta = object, is_explicit: bool = None) -> object:
		type = 'podcast'
		urls = {service: urls} if not isinstance(urls, dict) else urls
		ids = {service: str(ids)} if not isinstance(ids, dict) else ids
		censored_title = title
		
		self.service = service
		self.type = type
		self.urls = urls
		self.ids = ids
		self.title = title
		self.censored_title = title
		self.publisher = publisher
		self.cover = cover
		self.is_explicit = is_explicit
		self.meta = meta
		self.json = {
			'service': service,
			'type': type,
			'urls': urls,
			'ids': ids,
			'title': title,
			'censored_title': censored_title,
			'publisher': publisher,
			'cover': cover.json,
			'is_explicit': is_explicit,
			'meta': meta.json
		}

class PodcastEpisode:
	"""
		# Astro Podcast Episode Object

		This is a built-in Astro API object which identifies podcast episodes.
		JSON representation available.

		 :param	service: The API service in which the object was formed.
		 :param urls: The podcast episode's URL(s).
		 :param ids: The podcast episode's ID(s).
		 :param title: The podcast episode's title.
		 :param publisher: The podcast episode's publisher.
		 :param release_year: The podcast episode's release year.
		 :param is_explicit: Optional. Whether the podcast episode is explicit or not.
		 :param meta: The technical metadata of the podcast episode.
	"""
	def __init__(self, service: str, urls: str | dict, ids: any | dict, title: str, release_year: int, cover: object, meta = object, is_explicit: bool = None) -> object:
		type = 'podcast_episode'
		urls = {service: urls} if not isinstance(urls, dict) else urls
		ids = {service: str(ids)} if not isinstance(ids, dict) else ids
		censored_title = title
		release_year = None if release_year == None else int(release_year)

		self.service = service
		self.type = type
		self.urls = urls
		self.ids = ids
		self.title = title
		self.censored_title = censored_title
		self.release_year = release_year
		self.cover = cover
		self.is_explicit = is_explicit
		self.meta = meta
		self.json = {
			'service': service,
			'type': type,
			'urls': urls,
			'ids': ids,
			'title': title,
			'censored_title': censored_title,
			'release_year': release_year,
			'cover': cover.json,
			'is_explicit': is_explicit,
			'meta': meta.json
		}


class Playlist:
	"""
		# Astro Playlist Object

		This is a built-in Astro API object which identifies service playlists.
		JSON representation available.

		 :param	service: The API service in which the object was formed.
		 :param urls: The playlist's URL(s).
		 :param ids: The playlist's ID(s).
		 :param title: The playlist's title.
		 :param owner: The playlist's owner (creator).
		 :param songs: The playlist's owner (creator).
		 :param owner: The playlist's owner (creator).
		 :param meta: The technical metadata of the playlist.
	"""
	def __init__(self, service: str, urls: str | dict, ids: any | dict, title: str, owner: str, songs: list[object], cover: object, meta: object) -> object:
		type = 'playlist'
		urls = {service: urls} if not isinstance(urls, dict) else urls
		ids = {service: str(ids)} if not isinstance(ids, dict) else ids
		censored_title = title

		self.service = service
		self.type = type
		self.urls = urls
		self.ids = ids
		self.title = title
		self.censored_title = censored_title
		self.owner = owner
		self.songs = songs
		self.cover = cover
		self.meta = meta
		self.json = {
			'service': service,
			'type': type,
			'urls': urls,
			'ids': ids,
			'title': title,
			'censored_title': title,
			'owner': owner,
			'songs': [song.json for song in songs],
			'cover': cover.json,
			'meta': meta.json
		}

class Audiobook:
	def __init__(self, service: str, url: str | dict, id: any, title: str, authors: list, narrators: list, publisher: str, chapters: int, cover_url: str, is_explicit: bool, meta = object, cover_color_hex: int = None) -> object:
		self.service = service
		self.type = 'audiobook'
		self.url = {service: url} if isinstance(url, str) else url
		self.id = {service: str(id)} if not isinstance(id, dict) else id
		self.title = title
		self.censored_title = title
		self.authors = authors
		self.narrators = narrators
		self.publisher = publisher
		self.chapters = chapters
		self.cover_url = cover_url
		self.cover_color_hex = cover_color_hex
		self.is_explicit = is_explicit
		self.meta = meta

class Artist:
	def __init__(self, service: str, urls: str | dict, ids: any, name: str, meta = object, profile_pic_url: str = None, profile_pic_color_hex: int = None, genres: list = None) -> object:
		urls = {service: urls} if isinstance(urls, str) else urls
		ids = {service: str(ids)} if not isinstance(ids, dict) else ids
		profile_pic_url = profile_pic_url if profile_pic_url != None else missing_image
		
		self.service = service
		self.type = 'artist'
		self.urls = urls
		self.ids = ids
		self.name = name
		self.genres = genres
		self.profile_pic_url = profile_pic_url
		self.profile_pic_color_hex = profile_pic_color_hex
		self.meta = meta
		self.json = {
			'service': service,
			'type': 'artist',
			'urls': urls,
			'ids': ids,
			'name': name,
			'genres': genres,
			'profile_pic': {
				'url': profile_pic_url,
				'color_hex': profile_pic_color_hex
			},
			'meta': meta.json
		}

class Cover:
	def __init__(self, service: str, type: str, hq_url: str | dict, lq_url: str | dict, title: str, artists: list, meta = object, color_hex: int = None) -> object:
		hq_url = {service: hq_url} if isinstance(hq_url, str) else hq_url if hq_url != None else missing_image
		lq_url = {service: lq_url} if isinstance(lq_url, str) else lq_url if lq_url != None else missing_image
		color_hex = color_hex if color_hex != None else astro_yellow
		
		self.service = service
		self.type = 'cover'
		self.media_type = type
		self.title = title
		self.censored_title = title
		self.artists = artists
		self.hq_url = {service: hq_url} if isinstance(hq_url, str) else hq_url
		self.lq_url = {service: lq_url} if isinstance(lq_url, str) else lq_url
		self.color_hex = color_hex
		self.meta = meta

class Knowledge:
	def __init__(self, service: str, media_type: str, url: str | dict, id: any, title: str, artists: list, cover_url: str, meta: object, description: str = None, cover_color_hex: int = None, collection: str = None, release_date: str = None, is_explicit: bool = None, genre: str = None, bpm: float = None, key: int = None, length: int = None, time_signature: int = None) -> object:
		pitch_class = {
			0: 'C',
			1: 'C♯/D♭',
			2: 'D',
			3: 'D♯/E♭',
			4: 'E',
			5: 'F',
			6: 'F♯/G♭',
			7: 'G',
			8: 'G♯/A♭',
			9: 'A',
			10: 'A♯/B♭',
			11: 'B',
			-1: None,
			None: None
		}

		self.service = service
		self.type = 'knowledge'
		self.media_type = media_type
		self.url = {service: url} if isinstance(url, str) else url
		self.id = {service: str(id)} if not isinstance(id, dict) else id
		self.title = title
		self.censored_title = title
		self.collection = collection
		self.artists = artists
		self.description = description if description != '?' or description != '' else None
		self.release_date = release_date
		self.cover_url = cover_url
		self.cover_color_hex = cover_color_hex
		self.genre = genre
		self.is_explicit = is_explicit
		self.bpm = bpm
		self.key = pitch_class[key]
		self.length = length
		self.time_signature = f'1/{time_signature}' if time_signature is not None else None
		self.meta = meta