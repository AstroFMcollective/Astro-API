from AstroAPI.components.ini import text

missing_image = text['images']['missing_image']
astro_yellow = int(text['color_hex']['astro_yellow'], base=16)



"""
	--- MEDIA OBJECTS ---

	Astro uses these to form usable representations of a piece of media (song, album, etc.)

	Astro's media objects are an useful and efficient way of forming these representations,
	with a few key details they're able to:
	- Nicely format everything in more usable formats
	- Generate censored titles and names of select objects
	- Generate JSON versions of these objects for use in the REST interface
	- Include an abundance of technical and debug info.

	Use these literally whenever you have to form a media object. They're easily reusable
	and simple to form.
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
		self.json_lite = {
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
		self.json_lite = {
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
		 :param http_code: The HTTP code returned by an Astro component.
		 :param processing_time: The amount of time in milliseconds that an Astro component took to form the orignial media object.
		 :param filter_confidence_percentage: Optional. Astro's confidence in how accurately it got the correct media object.
	"""

	def __init__(self, service: str, request: dict, processing_time: int | dict, http_code: int | dict, filter_confidence_percentage: float | dict = None):
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
		 :param collection: Optional. The song's collection (album or EP).
		 :param cover: The song's cover art.
		 :param genre: Optional. The song's genre.
		 :param is_explicit: Optional. Whether the song is explicit or not.
		 :param meta: The technical metadata of the song.
	"""

	def __init__(self, service: str, type: str, urls: str | dict, ids: str | dict, title: str, artists: list[object], cover: object, meta: object, collection: object = None, genre: str = None, is_explicit: bool = None) -> object:
		urls = {service: urls} if not isinstance(urls, dict) else urls
		ids = {service: ids} if not isinstance(ids, dict) else ids
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
			'artists': [artist.json_lite for artist in artists],
			'collection': collection.json_lite if collection else None,
			'cover': cover.json_lite,
			'genre': genre,
			'is_explicit': is_explicit,
			'meta': meta.json
		}
		self.json_lite = {
			'type': type,
			'urls': urls,
			'ids': ids,
			'title': title,
			'censored_title': censored_title,
			'artists': [artist.json_lite for artist in artists],
			'collection': collection.json_lite if collection else None,
			'cover': cover.json_lite,
			'genre': genre,
			'is_explicit': is_explicit,
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

	def __init__(self, service: str, urls: str | dict, ids: str | dict, title: str, artists: list[object], cover: object, meta: object, is_explicit: bool = None, genre: str = None) -> object:
		type = 'music_video'
		urls = {service: urls} if not isinstance(urls, dict) else urls
		ids = {service: ids} if not isinstance(ids, dict) else ids
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
			'artists': [artist.json_lite for artist in artists],
			'cover': cover.json_lite,
			'genre': genre,
			'is_explicit': is_explicit,
			'meta': meta.json
		}
		self.json_lite = {
			'type': type,
			'urls': urls,
			'ids': ids,
			'title': title,
			'censored_title': censored_title,
			'artists': [artist.json_lite for artist in artists],
			'cover': cover.json_lite,
			'genre': genre,
			'is_explicit': is_explicit,
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
		 :param cover: The collection's cover art.
		 :param genre: Optional. The collection's genre.
		 :param meta: The technical metadata of the collection.
	"""

	def __init__(self, service: str, type: str, urls: str | dict, ids: str | dict, title: str, artists: list[object], cover: object, meta = object, release_year: int = None, genre: str = None) -> object:
		urls = {service: urls} if not isinstance(urls, dict) else urls
		ids = {service: ids} if not isinstance(ids, dict) else ids
		censored_title = title
		
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
			'artists': [artist.json_lite for artist in artists],
			'release_year': release_year,
			'cover': cover.json_lite,
			'genre': genre,
			'meta': meta.json
		}
		self.json_lite = {
			'type': type,
			'urls': urls,
			'ids': ids,
			'title': title,
			'censored_title': censored_title,
			'artists': [artist.json_lite for artist in artists],
			'release_year': release_year,
			'cover': cover.json_lite,
			'genre': genre,
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

	def __init__(self, service: str, urls: str | dict, ids: str | dict, title: str, publisher: str, cover: object, meta = object, is_explicit: bool = None) -> object:
		type = 'podcast'
		urls = {service: urls} if not isinstance(urls, dict) else urls
		ids = {service: ids} if not isinstance(ids, dict) else ids
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
			'cover': cover.json_lite,
			'is_explicit': is_explicit,
			'meta': meta.json
		}
		self.json_lite = {
			'type': type,
			'urls': urls,
			'ids': ids,
			'title': title,
			'censored_title': censored_title,
			'publisher': publisher,
			'cover': cover.json_lite,
			'is_explicit': is_explicit,
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

	def __init__(self, service: str, urls: str | dict, ids: str | dict, title: str, release_year: int, cover: object, meta = object, is_explicit: bool = None) -> object:
		type = 'podcast_episode'
		urls = {service: urls} if not isinstance(urls, dict) else urls
		ids = {service: ids} if not isinstance(ids, dict) else ids
		censored_title = title

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
		self.json_lite = {
			'type': type,
			'urls': urls,
			'ids': ids,
			'title': title,
			'censored_title': censored_title,
			'release_year': release_year,
			'cover': cover.json,
			'is_explicit': is_explicit,
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
		 :param songs: The playlist's songs.
		 :param cover: The playlist's cover.
		 :param meta: The technical metadata of the playlist.
	"""

	def __init__(self, service: str, urls: str | dict, ids: str | dict, title: str, owner: str, songs: list[object], cover: object, meta: object) -> object:
		type = 'playlist'
		urls = {service: urls} if not isinstance(urls, dict) else urls
		ids = {service: ids} if not isinstance(ids, dict) else ids
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
			'songs': [song.json_lite for song in songs],
			'cover': cover.json_lite,
			'meta': meta.json
		}
		self.json_lite = {
			'type': type,
			'urls': urls,
			'ids': ids,
			'title': title,
			'censored_title': title,
			'owner': owner,
			'songs': [song.json_lite for song in songs],
			'cover': cover.json_lite,
		}



class Audiobook:

	"""
		# Astro Audiobook Object

		This is a built-in Astro API object which identifies audiobooks.
		JSON representation available.

		 :param	service: The API service in which the object was formed.
		 :param urls: The audiobook's URL(s).
		 :param ids: The audiobook's ID(s).
		 :param title: The audiobook's title.
		 :param authors: The audiobook's authors.
		 :param narrators: The audiobook's narrators.
		 :param publisher: The audiobook's publisher.
		 :param chapters: The number of chapters the audiobook has.
		 :param cover: The audiobook's cover.
		 :param is_explicit: Whether the audiobook is explicit or not.
		 :param meta: The technical metadata of the audiobook.
	"""

	def __init__(self, service: str, urls: str | dict, ids: str | dict, title: str, authors: list, narrators: list, publisher: str, chapters: int, cover: object, is_explicit: bool, meta: object) -> object:
		type = 'audiobook'
		urls = {service: urls} if not isinstance(urls, dict) else urls
		ids = {service: ids} if not isinstance(ids, dict) else ids
		censored_title = title

		self.service = service
		self.type = 'audiobook'
		self.urls = urls
		self.ids = ids
		self.title = title
		self.censored_title = censored_title
		self.authors = authors
		self.narrators = narrators
		self.publisher = publisher
		self.chapters = chapters
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
			'authors': authors,
			'narrators': narrators,
			'publisher': publisher,
			'chapters': chapters,
			'cover': cover.json,
			'is_explicit': is_explicit,
			'meta': meta.json
		}
		self.json_lite = {
			'type': type,
			'urls': urls,
			'ids': ids,
			'title': title,
			'censored_title': censored_title,
			'authors': authors,
			'narrators': narrators,
			'publisher': publisher,
			'chapters': chapters,
			'cover': cover.json,
			'is_explicit': is_explicit,
		}



class Artist:

	"""
		# Astro Artist Object

		This is a built-in Astro API object which identifies artists.
		JSON representation available.

		 :param	service: The API service in which the object was formed.
		 :param urls: The artist's URL(s).
		 :param ids: The artist's ID(s).
		 :param name: The artist's name.
		 :param genre: Optional. The artist's main genre.
		 :param profile_picture: The artist's profile picture.
		 :param meta: The technical metadata of the artist.
	"""

	def __init__(self, service: str, urls: str | dict, ids: str | dict, name: str, meta: object, profile_picture: object = None, genre: str = None) -> object:
		type = 'artist'
		urls = {service: urls} if not isinstance(urls, dict) else urls
		ids = {service: ids} if not isinstance(ids, dict) else ids
		
		self.service = service
		self.type = type
		self.urls = urls
		self.ids = ids
		self.name = name
		self.genre = genre
		self.profile_picture = profile_picture
		self.meta = meta
		self.json = {
			'service': service,
			'type': type,
			'urls': urls,
			'ids': ids,
			'name': name,
			'genres': genre,
			'profile_picture': profile_picture.json_lite if profile_picture != None else None,
			'meta': meta.json
		}
		self.json_lite = {
			'type': type,
			'urls': urls,
			'ids': ids,
			'name': name,
			'genres': genre,
			'profile_picture': profile_picture.json_lite if profile_picture != None else None,
		}



class Cover:

	"""
		# Astro Cover Object

		This is a built-in Astro API object which identifies covers.
		Astro identifies two types of covers: regular covers and thumbnails.
		Use thumbnails for music videos, covers for everything else.
		JSON representation available.

		 :param	service: The API service in which the object was formed.
		 :param media_type: The cover's media type.
		 :param title: The media's title.
		 :param artists: The media's artists.
		 :param hq_urls: The cover's high quality URL(s).
		 :param lq_urls: The cover's low quality URL(s).
		 :param color_hex: Optional. The cover's color hex code.
		 :param meta: The technical metadata of the artist.
	"""

	def __init__(self, service: str, media_type: str, title: str, artists: list[object], hq_urls: str | dict | None, lq_urls: str | dict | None, meta: object, color_hex: int = None) -> object:
		type = 'cover'
		hq_urls = {service: hq_urls} if isinstance(hq_urls, str) else hq_urls if hq_urls != None else missing_image
		lq_urls = {service: lq_urls} if isinstance(lq_urls, str) else lq_urls if lq_urls != None else missing_image
		censored_title = title
		color_hex = color_hex if color_hex != None else astro_yellow
		
		self.service = service
		self.type = type
		self.media_type = media_type
		self.title = title
		self.censored_title = censored_title
		self.artists = artists
		self.hq_urls = hq_urls
		self.lq_urls = lq_urls
		self.color_hex = color_hex
		self.meta = meta
		self.json = {
			'service': service,
			'type': type,
			'media_type': media_type,
			'title': title,
			'censored_title': censored_title,
			'artists': [artist.json_lite for artist in artists],
			'hq_urls': hq_urls,
			'lq_urls': lq_urls,
			'color_hex': color_hex,
			'meta': meta.json
		}
		self.json_lite = {
			'type': type,
			'hq_urls': hq_urls,
			'lq_urls': lq_urls,
			'color_hex': color_hex,
		}



class ProfilePicture:

	"""
		# Astro Profile Picture Object

		This is a built-in Astro API object which identifies profile pictures.
		Use this instead of covers for artists.
		JSON representation available.

		 :param	service: The API service in which the object was formed.
		 :param user_type: The type of user of the profile picture, can either be `user` or `artist`.
		 :param hq_urls: The profile picture's high quality URL(s).
		 :param lq_urls: The profile picture's low quality URL(s).
		 :param color_hex: Optional The profile picture's color hex code.
		 :param meta: The technical metadata of the artist.
	"""

	def __init__(self, service: str, user_type: str, meta: object, hq_urls: str | dict = None, lq_urls: str | dict = None, color_hex: int = None):
		type = 'profile_picture'
		hq_urls = {service: hq_urls} if isinstance(hq_urls, str) else hq_urls if hq_urls != None else missing_image
		lq_urls = {service: lq_urls} if isinstance(lq_urls, str) else lq_urls if lq_urls != None else missing_image
		color_hex = color_hex if color_hex != None else astro_yellow

		self.service = service
		self.type = type
		self.user_type = user_type
		self.hq_urls = hq_urls
		self.lq_urls = lq_urls
		self.color_hex = color_hex
		self.meta = meta
		self.json = {
			'service': service,
			'type': type,
			'user_type': user_type,
			'hq_urls': hq_urls,
			'lq_urls': lq_urls,
			'color_hex': color_hex,
			'meta': meta.json
		}
		self.json_lite = {
			'type': type,
			'hq_urls': hq_urls,
			'lq_urls': lq_urls,
			'color_hex': color_hex,
		}



class Knowledge:

	"""
		# Astro Knowledge Object

		This is a built-in Astro API object which identifies song knowledge.
		It provides more details about a song, such as a small content description, length, BPM, etc.
		JSON representation available.

		 :param	service: The API service in which the object was formed.
		 :param media_type: The song type, can either be `track` or `single`.
		 :param urls: The song's URL(s).
		 :param ids: The song's ID(s).
		 :param title: The song's title.
		 :param collection: Optional. The song's collection (album or EP).
		 :param artists: The song's artists.
		 :param description: Optional. The song's description.
		 :param release_date: Optional. The song's full release date.
		 :param cover: The song's cover.
		 :param genre: Optional. The song's genre.
		 :param is_explicit: Optional. Whether the song is explicit or not.
		 :param bpm: Optional. sThe song's tempo/BPM (beats per minute).
		 :param key: Optional. The song's key pitch class.
		 :param length: Optional. The song's length.
		 :param time_signature: Optional. The song's time signature fraction.
		 :param meta: The technical metadata of the song.
	"""

	def __init__(self, service: str, media_type: str, urls: str | dict, ids: str | dict, title: str, artists: list[object], cover: object, meta: object, description: str = None, collection: object = None, release_date: str = None, is_explicit: bool = None, genre: str = None, bpm: float = None, key: int = None, length: int = None, time_signature: int = None) -> object:
		type = 'knowledge'
		urls = {service: urls} if not isinstance(urls, dict) else urls
		ids = {service: ids} if not isinstance(ids, dict) else ids
		description = description if description != '?' or description != '' else None
		censored_description = description
		time_signature = f'1/{time_signature}' if time_signature is not None else None
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
		key = pitch_class[key]

		self.service = service
		self.type = type
		self.media_type = media_type
		self.urls = urls
		self.ids = ids
		self.title = title
		self.censored_title = title
		self.artists = artists
		self.collection = collection
		self.description = description
		self.censored_description = censored_description
		self.release_date = release_date
		self.cover = cover
		self.genre = genre
		self.is_explicit = is_explicit
		self.bpm = bpm
		self.key = key
		self.length = length
		self.time_signature = time_signature
		self.meta = meta
		self.json = {
			'service': service,
			'type': type,
			'media_type': media_type,
			'urls': urls,
			'ids': ids,
			'title': title,
			'censored_title': title,
			'artists': [artist.json_lite for artist in artists],
			'collection': collection.json_lite if collection else None,
			'description': description,
			'censored_description': censored_description,
			'release_date': release_date,
			'cover': cover.json_lite,
			'genre': genre,
			'is_explicit': is_explicit,
			'bpm': bpm,
			'key': key,
			'length': length,
			'time_signature': time_signature,
			'meta': meta.json
		}
		self.json = {
			'type': type,
			'media_type': media_type,
			'urls': urls,
			'ids': ids,
			'title': title,
			'censored_title': title,
			'artists': [artist.json_lite for artist in artists],
			'collection': collection.json_lite if collection else None,
			'description': description,
			'censored_description': censored_description,
			'release_date': release_date,
			'cover': cover.json_lite,
			'genre': genre,
			'is_explicit': is_explicit,
			'bpm': bpm,
			'key': key,
			'length': length,
			'time_signature': time_signature,
		}
