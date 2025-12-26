from AstroAPI.InternalComponents.Legacy.ini import text
from AstroAPI.InternalComponents.Legacy.text_manipulation import censor_text

missing_image = text['images']['missing_image']

"""
	# Search Catalog API Media Objects

	Astro's specialty is manipulating media metadata and using it to do other things,
	so obviously that data needs to be reusable, intelligent and efficient.
	The Service Catalog API uses these media objects for that, to form usable representations
	of a piece of media (song, album, etc.).

	Service Catalog API's media objects are able to:
	- Nicely format everything in more usable formats
	- Generate censored titles and names of select objects
	- Generate JSON versions of these objects for use by the REST API for developers
	- Include an abundance of technical and debug info.

	Use these literally whenever you have to form a media object. They're easily reusable
	and simple to form.
"""



class Meta:

	"""
		# Service Catalog API (Technical) Metadata Object

		This is a built-in Service Catalog API object which identifies technical metadata.
		In it are shoved in stats and values useful for debugging or general handling.
		JSON representation available.

		 :param service: The API service in which the parent object was formed.
		 :param request: The request dictionary (json) of all the data used to make the request.
		 :param http_code: The HTTP code returned by an Astro component.
		 :param processing_time: The amount of time in milliseconds that an Astro component took to form the orignial media object.
		 :param filter_confidence_percentage: Optional. Astro's confidence in how accurately it got the correct media object.
	"""

	def __init__(self, service: str, request: dict, processing_time: int | dict, http_code: int | dict, filter_confidence_percentage: int | float | dict | None = None):
		self._service = service
		self._request = request
		self._http_code = http_code
		self._processing_time = processing_time if isinstance(processing_time, dict) else {service: processing_time}
		self._filter_confidence_percentage = filter_confidence_percentage

	@property
	def service(self):
		return self._service

	@service.setter
	def service(self, value):
		self._service = value

	@property
	def request(self):
		return self._request

	@request.setter
	def request(self, value):
		self._request = value

	@property
	def http_code(self):
		return self._http_code

	@http_code.setter
	def http_code(self, value):
		self._http_code = value

	@property
	def processing_time(self):
		return self._processing_time

	@processing_time.setter
	def processing_time(self, value):
		# If given a dict, store it directly.
		if isinstance(value, dict):
			self._processing_time = value
		else:
			service = self._service
			self._processing_time = {service: value}

	@property
	def filter_confidence_percentage(self):
		return self._filter_confidence_percentage

	@filter_confidence_percentage.setter
	def filter_confidence_percentage(self, value: int | float | dict | None):
		self._filter_confidence_percentage = value

	@property
	def json(self):
		return {
			'request': self._request,
			'http_code': self._http_code,
			'processing_time': self._processing_time,
			'filter_confidence_percentage': self._filter_confidence_percentage,
		}



class Song:

	"""
		# Service Catalog API Song Object

		This is a built-in Service Catalog API object which identifies songs.
		Service Catalog API identifies two types of songs: tracks and singles.
		It's an unwritten rule, but Service Catalog API should sort tracks as songs off albums, while
		singles are standalone tracks and sometimes tracks from EP-s.
		JSON representation available.

		 :param	service: The API service in which the object was formed.
		 :param type: The song type, should either be `track` or `single`.
		 :param urls: The song's URL(s). To put multiple URL-s in an object, use dicts.
		 :param ids: The song's ID(s). To put multiple ID-s in an object, use dicts.
		 :param previews: Optional. The song's preview URL(s). To put multiple preview URL-s in an object, use dicts.
		 :param title: The song's title.
		 :param artists: The song's artists.
		 :param collection: Optional. The song's collection (album or EP).
		 :param cover: The song's cover art.
		 :param genre: Optional. The song's genre.
		 :param is_explicit: Optional. Whether the song is explicit or not.
		 :param meta: The technical metadata of the song.
	"""

	def __init__(self, service: str, type: str, urls: str | dict, ids: str | dict, title: str, artists: list[object], cover: object, meta: object, previews: str | dict = None, collection: object = None, genre: str = None, is_explicit: bool = None) -> object:
		urls = {service: urls} if not isinstance(urls, dict) else urls
		ids = {service: str(ids)} if not isinstance(ids, dict) else ids
		previews = {service: previews} if not isinstance(previews, dict) else previews
		censored_title = censor_text(title)
		
		self._service = service
		self._type = type
		self._urls = urls
		self._ids = ids
		self._previews = previews
		self._title = title
		self._censored_title = censored_title
		self._artists = artists
		self._collection = collection
		self._cover = cover
		self._genre = genre
		self._is_explicit = is_explicit
		self._meta = meta

	# Service
	@property
	def service(self):
		return self._service

	@service.setter
	def service(self, value: str):
		self._service = value

	# Type
	@property
	def type(self):
		return self._type

	@type.setter
	def type(self, value: str):
		self._type = value

	# URL-s
	@property
	def urls(self):
		return self._urls

	@urls.setter
	def urls(self, value: str):
		self._urls = {self._service: value} if not isinstance(value, dict) else value

	# ID-s
	@property
	def ids(self):
		return self._ids

	@ids.setter
	def ids(self, value: str):
		self._ids = {self._service: value} if not isinstance(value, dict) else value

	# Previews
	@property
	def previews(self):
		return self._previews

	@previews.setter
	def previews(self, value: str):
		self._previews = {self._service: value} if not isinstance(value, dict) else value

	# Title
	@property
	def title(self):
		return self._title

	@title.setter
	def title(self, value: str):
		self._title = value

	# Censored title
	@property
	def censored_title(self):
		return self._censored_title

	@censored_title.setter
	def censored_title(self, value: str):
		self._censored_title = value

	# Artists
	@property
	def artists(self):
		return self._artists

	@artists.setter
	def artists(self, value: list):
		self._artists = value

	# Collection
	@property
	def collection(self):
		return self._collection

	@collection.setter
	def collection(self, value: list):
		self._collection = value

	# Cover
	@property
	def cover(self):
		return self._cover

	@cover.setter
	def cover(self, value: object):
		self._cover = value

	# Genre
	@property
	def genre(self):
		return self._genre

	@genre.setter
	def genre(self, value: list):
		self._genre = value

	# Genre
	@property
	def genre(self):
		return self._genre

	@genre.setter
	def genre(self, value: str):
		self._genre = value

	# Explicitness
	@property
	def is_explicit(self):
		return self._is_explicit

	@is_explicit.setter
	def is_explicit(self, value: bool):
		self._is_explicit = value

	# Metadata
	@property
	def meta(self):
		return self._meta

	@meta.setter
	def meta(self, value: object):
		self._meta = value

	# JSON representation
	@property
	def json(self):
		meta = self._meta.json if hasattr(self._meta, 'json') else self._meta
		return {
			'service': self._service,
			'type': self._type,
			'urls': self._urls,
			'ids': self._ids,
			'previews': self._previews,
			'title': self._title,
			'censored_title': self._censored_title,
			'artists': [artist.json_lite for artist in self.artists],
			'collection': self._collection.json_lite if self._collection else None,
			'cover': self._cover.json_lite if self.cover else None,
			'genre': self._genre,
			'is_explicit': self.is_explicit,
			'meta': meta
		}
	
	# Light JSON representation (without technical metadata)
	@property
	def json_lite(self):
		return {
			'service': self._service,
			'type': self._type,
			'urls': self._urls,
			'ids': self._ids,
			'previews': self._previews,
			'title': self._title,
			'censored_title': self._censored_title,
			'artists': [artist.json_lite for artist in self.artists],
			'collection': self._collection.json_lite if self._collection else None,
			'cover': self._cover.json_lite if self.cover else None,
			'genre': self._genre,
			'is_explicit': self.is_explicit
		}
	


class MusicVideo:

	"""
		# Service Catalog API Music Video Object

		This is a built-in Service Catalog API object which identifies music videos.
		JSON representation available.
		
		 :param	service: The API service in which the object was formed.
		 :param urls: The music video's URL(s). To put multiple URL-s in an object, use dicts.
		 :param ids: The music video's ID(s). To put multiple ID-s in an object, use dicts.
		 :param previews: Optional. The music video's preview URL(s).
		 :param title: The music video's title.
		 :param artists: The music video's artists.
		 :param cover: The music video's thumbnail.
		 :param genre: Optional. The music video's genre.
		 :param is_explicit: Optional. Whether the music video is explicit or not.
		 :param meta: The technical metadata of the music video.
	"""

	def __init__(self, service: str, urls: str | dict, ids: str | dict, title: str, artists: list[object], cover: object, meta: object, previews: str | dict = None, is_explicit: bool = None, genre: str = None) -> object:
		type = 'music_video'
		urls = {service: urls} if not isinstance(urls, dict) else urls
		ids = {service: str(ids)} if not isinstance(ids, dict) else ids
		previews = {service: previews} if not isinstance(previews, dict) else previews
		censored_title = censor_text(title)
		
		self._service = service
		self._type = type
		self._urls = urls
		self._ids = ids
		self._previews = previews
		self._title = title
		self._censored_title = censored_title
		self._artists = artists
		self._cover = cover
		self._genre = genre
		self._is_explicit = is_explicit
		self._meta = meta

	# Service
	@property
	def service(self):
		return self._service

	@service.setter
	def service(self, value: str):
		self._service = value

	# Type (constant)
	@property
	def type(self):
		return self._type

	# URL-s
	@property
	def urls(self):
		return self._urls

	@urls.setter
	def urls(self, value: str):
		self._urls = {self._service: value} if not isinstance(value, dict) else value

	# ID-s
	@property
	def ids(self):
		return self._ids

	@ids.setter
	def ids(self, value: str):
		self._ids = {self._service: value} if not isinstance(value, dict) else value

	# Previews
	@property
	def previews(self):
		return self._previews

	@previews.setter
	def previews(self, value: str):
		self._previews = {self._service: value} if not isinstance(value, dict) else value

	# Title
	@property
	def title(self):
		return self._title

	@title.setter
	def title(self, value: str):
		self._title = value

	# Censored title
	@property
	def censored_title(self):
		return self._censored_title

	@censored_title.setter
	def censored_title(self, value: str):
		self._censored_title = value

	# Artists
	@property
	def artists(self):
		return self._artists

	@artists.setter
	def artists(self, value: list):
		self._artists = value

	# Cover
	@property
	def cover(self):
		return self._cover

	@cover.setter
	def cover(self, value: object):
		self._cover = value

	# Genre
	@property
	def genre(self):
		return self._genre

	@genre.setter
	def genre(self, value: str):
		self._genre = value

	# Explicitness
	@property
	def is_explicit(self):
		return self._is_explicit

	@is_explicit.setter
	def is_explicit(self, value: bool):
		self._is_explicit = value

	# Metadata
	@property
	def meta(self):
		return self._meta

	@meta.setter
	def meta(self, value: object):
		self._meta = value

	# JSON representation
	@property
	def json(self):
		meta = self._meta.json if hasattr(self._meta, 'json') else self._meta
		return {
			'service': self._service,
			'type': self._type,
			'urls': self._urls,
			'ids': self._ids,
			'previews': self._previews,
			'title': self._title,
			'censored_title': self._censored_title,
			'artists': [artist.json_lite for artist in self.artists],
			'cover': self.cover.json_lite,
			'genre': self.genre,
			'is_explicit': self.is_explicit,
			'meta': meta
		}
	
	# Light JSON representation (without technical metadata)
	@property
	def json_lite(self):
		return {
			'service': self._service,
			'type': self._type,
			'urls': self._urls,
			'ids': self._ids,
			'previews': self._previews,
			'title': self._title,
			'censored_title': self._censored_title,
			'artists': [artist.json_lite for artist in self.artists],
			'cover': self.cover.json_lite,
			'genre': self.genre,
			'is_explicit': self.is_explicit
		}



class Collection:

	"""
		# Service Catalog API Collection Object

		This is a built-in Service Catalog API object which identifies collections.
		Service Catalog API identifies two different collection types: albums and EP-s.
		JSON representation available.

		 :param	service: The API service in which the object was formed.
		 :param type: The collection type, should either be `album` or `ep`.
		 :param urls: The collection's URL(s).
		 :param ids: The collection's ID(s).
		 :param title: The collection's title.
		 :param artists: The collection's artists.
		 :param release_year: Optional. The collection's release year.
		 :param cover: The collection's cover art.
		 :param genre: Optional. The collection's genre.
		 :param meta: The technical metadata of the collection.
	"""

	def __init__(self, service: str, type: str, urls: str | dict, ids: str | dict, title: str, artists: list[object], cover: object, meta: object, release_year: int = None, genre: str = None) -> object:
		urls = {service: urls} if not isinstance(urls, dict) else urls
		ids = {service: str(ids)} if not isinstance(ids, dict) else ids
		censored_title = censor_text(title)

		self._service = service
		self._type = type
		self._urls = urls
		self._ids = ids
		self._title = title
		self._censored_title = censored_title
		self._artists = artists
		self._release_year = release_year
		self._cover = cover
		self._genre = genre
		self._meta = meta

	# Service
	@property
	def service(self):
		return self._service

	@service.setter
	def service(self, value: str):
		self._service = value

	# Type
	@property
	def type(self):
		return self._type

	@type.setter
	def type(self, value: str):
		self._type = value

	# URL-s
	@property
	def urls(self):
		return self._urls

	@urls.setter
	def urls(self, value: str):
		self._urls = {self._service: value} if not isinstance(value, dict) else value

	# ID-s
	@property
	def ids(self):
		return self._ids

	@ids.setter
	def ids(self, value: str):
		self._ids = {self._service: value} if not isinstance(value, dict) else value

	# Title
	@property
	def title(self):
		return self._title

	@title.setter
	def title(self, value: str):
		self._title = value

	# Censored title
	@property
	def censored_title(self):
		return self._censored_title

	@censored_title.setter
	def censored_title(self, value: str):
		self._censored_title = value

	# Artists
	@property
	def artists(self):
		return self._artists

	@artists.setter
	def artists(self, value: list):
		self._artists = value

	# Release year
	@property
	def release_year(self):
		return self._release_year

	@release_year.setter
	def release_year(self, value: int):
		self._release_year = value

	# Cover
	@property
	def cover(self):
		return self._cover

	@cover.setter
	def cover(self, value: object):
		self._cover = value

	# Genre
	@property
	def genre(self):
		return self._genre

	@genre.setter
	def genre(self, value: str):
		self._genre = value

	# Metadata
	@property
	def meta(self):
		return self._meta

	@meta.setter
	def meta(self, value: object):
		self._meta = value

	# JSON representation
	@property
	def json(self):
		meta = self._meta.json if hasattr(self._meta, 'json') else self._meta
		return {
			'service': self._service,
			'type': self._type,
			'urls': self._urls,
			'ids': self._ids,
			'title': self._title,
			'censored_title': self._censored_title,
			'artists': [artist.json_lite for artist in self._artists],
			'release_year': self._release_year,
			'cover': self._cover.json_lite if self._cover else None,
			'genre': self._genre,
			'meta': meta
		}

	# Light JSON representation (without technical metadata)
	@property
	def json_lite(self):
		return {
			'service': self._service,
			'type': self._type,
			'urls': self._urls,
			'ids': self._ids,
			'title': self._title,
			'censored_title': self._censored_title,
			'artists': [artist.json_lite for artist in self._artists],
			'release_year': self._release_year,
			'cover': self._cover.json_lite if self._cover else None,
			'genre': self._genre
		}



class Artist:

	"""
		# Service Catalog API Artist Object

		This is a built-in Service Catalog API object which identifies artists.
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
		ids = {service: str(ids)} if not isinstance(ids, dict) else ids

		self._service = service
		self._type = type
		self._urls = urls
		self._ids = ids
		self._name = name
		self._genre = genre
		self._profile_picture = profile_picture
		self._meta = meta

	# Service
	@property
	def service(self):
		return self._service

	@service.setter
	def service(self, value: str):
		self._service = value

	# Type (constant)
	@property
	def type(self):
		return self._type

	# URL-s
	@property
	def urls(self):
		return self._urls

	@urls.setter
	def urls(self, value: str):
		self._urls = {self._service: value} if not isinstance(value, dict) else value

	# ID-s
	@property
	def ids(self):
		return self._ids

	@ids.setter
	def ids(self, value: str):
		self._ids = {self._service: value} if not isinstance(value, dict) else value

	# Name
	@property
	def name(self):
		return self._name

	@name.setter
	def name(self, value: str):
		self._name = value

	# Profile picture
	@property
	def profile_picture(self):
		return self._profile_picture

	@profile_picture.setter
	def profile_picture(self, value: object):
		self._profile_picture = value

	# Genre
	@property
	def genre(self):
		return self._genre

	@genre.setter
	def genre(self, value: str):
		self._genre = value

	# Metadata
	@property
	def meta(self):
		return self._meta

	@meta.setter
	def meta(self, value: object):
		self._meta = value

	# JSON representation
	@property
	def json(self):
		meta = self._meta.json if hasattr(self._meta, 'json') else self._meta
		return {
			'service': self._service,
			'type': self._type,
			'urls': self._urls,
			'ids': self._ids,
			'name': self._name,
			'genre': self._genre,
			'profile_picture': self._profile_picture.json_lite if self._profile_picture else None,
			'meta': meta
		}

	# Light JSON representation (without technical metadata)
	@property
	def json_lite(self):
		return {
			'type': self._type,
			'urls': self._urls,
			'ids': self._ids,
			'name': self._name,
			'genre': self._genre,
			'profile_picture': self._profile_picture.json_lite if self._profile_picture else None
		}



class Cover:

	"""
		# Service Catalog API Cover Object

		This is a built-in Service Catalog API object which identifies covers and thumbnails.
		JSON representation available.

		 :param	service: The API service in which the object was formed.
		 :param media_type: The cover's media type.
		 :param title: The media's title.
		 :param artists: The media's artists.
		 :param hq_urls: The cover's high quality URL(s).
		 :param lq_urls: The cover's low quality URL(s).
		 :param meta: The technical metadata of the artist.
	"""

	def __init__(self, service: str, media_type: str, title: str, artists: list[object], hq_urls: str | dict | None, lq_urls: str | dict | None, meta: object) -> object:
		hq_urls = {service: hq_urls} if not isinstance(hq_urls, dict) else hq_urls
		hq_urls = {service: missing_image} if hq_urls is None else hq_urls
		lq_urls = {service: lq_urls} if not isinstance(lq_urls, dict) else lq_urls
		lq_urls = {service: missing_image} if lq_urls is None else lq_urls
		censored_title = censor_text(title)

		self._service = service
		self._type = 'cover'  # constant, no setter per request
		self._media_type = media_type
		self._title = title
		self._censored_title = censored_title
		self._artists = artists
		self._hq_urls = hq_urls
		self._lq_urls = lq_urls
		self._meta = meta

	# Service
	@property
	def service(self):
		return self._service

	@service.setter
	def service(self, value: str):
		self._service = value

	# Type (constant)
	@property
	def type(self):
		return self._type

	# Media type
	@property
	def media_type(self):
		return self._media_type

	@media_type.setter
	def media_type(self, value: str):
		self._media_type = value

	# Title
	@property
	def title(self):
		return self._title

	@title.setter
	def title(self, value: str):
		self._title = value

	# Censored title
	@property
	def censored_title(self):
		return self._censored_title

	@censored_title.setter
	def censored_title(self, value: str):
		self._censored_title = value

	# Artists
	@property
	def artists(self):
		return self._artists

	@artists.setter
	def artists(self, value: list):
		self._artists = value

	# High-quality URLs
	@property
	def hq_urls(self):
		return self._hq_urls

	@hq_urls.setter
	def hq_urls(self, value: str | dict | None):
		value = {self._service: value} if not isinstance(value, dict) else value
		self._hq_urls = {self._service: missing_image} if value is None else value

	# Low-quality URLs
	@property
	def lq_urls(self):
		return self._lq_urls

	@lq_urls.setter
	def lq_urls(self, value: str | dict | None):
		value = {self._service: value} if not isinstance(value, dict) else value
		self._lq_urls = {self._service: missing_image} if value is None else value

	# Metadata
	@property
	def meta(self):
		return self._meta

	@meta.setter
	def meta(self, value: object):
		self._meta = value

	# JSON representation
	@property
	def json(self):
		meta_val = self._meta.json if hasattr(self._meta, 'json') else self._meta
		return {
			'service': self._service,
			'type': self._type,
			'media_type': self._media_type,
			'title': self._title,
			'censored_title': self._censored_title,
			'artists': [artist.json_lite for artist in self._artists],
			'hq_urls': self._hq_urls,
			'lq_urls': self._lq_urls,
			'meta': meta_val
		}

	# Light JSON representation (without technical metadata)
	@property
	def json_lite(self):
		return {
			'type': self._type,
			'hq_urls': self._hq_urls,
			'lq_urls': self._lq_urls
		}



class ProfilePicture:

	"""
		# Service Catalog API Profile Picture Object

		This is a built-in Service Catalog API object which identifies profile pictures.
		Use this instead of covers for artists and users.
		JSON representation available.

		 :param	service: The API service in which the object was formed.
		 :param user_type: The type of user of the profile picture, can either be `user` or `artist`.
		 :param hq_urls: The profile picture's high quality URL(s).
		 :param lq_urls: The profile picture's low quality URL(s).
		 :param meta: The technical metadata of the profile picture.
	"""

	def __init__(self, service: str, user_type: str, meta: object, hq_urls: str | dict = None, lq_urls: str | dict = None) -> object:
		hq_urls = {service: hq_urls} if not isinstance(hq_urls, dict) else hq_urls
		hq_urls = {service: missing_image} if hq_urls is None else hq_urls
		lq_urls = {service: lq_urls} if not isinstance(lq_urls, dict) else lq_urls
		lq_urls = {service: missing_image} if lq_urls is None else lq_urls

		self._service = service
		self._type = 'profile_picture'
		self._user_type = user_type
		self._hq_urls = hq_urls
		self._lq_urls = lq_urls
		self._meta = meta

	# Service
	@property
	def service(self):
		return self._service

	@service.setter
	def service(self, value: str):
		self._service = value

	# Type (constant)
	@property
	def type(self):
		return self._type

	# User type
	@property
	def user_type(self):
		return self._user_type

	@user_type.setter
	def user_type(self, value: str):
		self._user_type = value

	# High-quality URLs
	@property
	def hq_urls(self):
		return self._hq_urls

	@hq_urls.setter
	def hq_urls(self, value: str | dict | None):
		value = {self._service: value} if not isinstance(value, dict) else value
		self._hq_urls = {self._service: missing_image} if value is None else value

	# Low-quality URLs
	@property
	def lq_urls(self):
		return self._lq_urls

	@lq_urls.setter
	def lq_urls(self, value: str | dict | None):
		value = {self._service: value} if not isinstance(value, dict) else value
		self._lq_urls = {self._service: missing_image} if value is None else value

	# Metadata
	@property
	def meta(self):
		return self._meta

	@meta.setter
	def meta(self, value: object):
		self._meta = value

	# JSON representation
	@property
	def json(self):
		meta_val = self._meta.json if hasattr(self._meta, 'json') else self._meta
		return {
			'service': self._service,
			'type': self._type,
			'user_type': self._user_type,
			'hq_urls': self._hq_urls,
			'lq_urls': self._lq_urls,
			'meta': meta_val
		}

	# Light JSON representation (without technical metadata)
	@property
	def json_lite(self):
		return {
			'type': self._type,
			'hq_urls': self._hq_urls,
			'lq_urls': self._lq_urls
		}



class SongKnowledge:

	"""
		# Service Catalog API Song Knowledge Object

		This is a built-in Service Catalog API object which identifies song knowledge.
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
		 :param bpm: Optional. The song's tempo/BPM (beats per minute).
		 :param key: Optional. The song's key pitch class (set by index, see guide below).
		 :param length: Optional. The song's length.
		 :param time_signature: Optional. The song's time signature fraction.
		 :param meta: The technical metadata of the song.
	"""

	# Guide for key indices — use these indices when setting .key
	_PITCH_CLASS = {
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

	def __init__(self, service: str, media_type: str, urls: str | dict, ids: str | dict, title: str, artists: list[object], cover: object, meta: object, description: str = None, collection: object = None, release_date: str = None, is_explicit: bool = None, genre: str = None, bpm: float = None, key: int = None, length: int = None, time_signature: int = None) -> object:
		urls = {service: urls} if not isinstance(urls, dict) else urls
		ids = {service: str(ids)} if not isinstance(ids, dict) else ids
		description = description if description != '?' and description != '' else None
		censored_title = censor_text(title)
		censored_description = censor_text(description)
		time_signature = f'1/{time_signature}' if time_signature is not None else None
		key_mapped = self._PITCH_CLASS.get(key, None)

		self._service = service
		self._type = 'knowledge'
		self._media_type = media_type
		self._urls = urls
		self._ids = ids
		self._title = title
		self._censored_title = censored_title
		self._artists = artists
		self._collection = collection
		self._description = description
		self._censored_description = censored_description
		self._release_date = release_date
		self._cover = cover
		self._genre = genre
		self._is_explicit = is_explicit
		self._bpm = bpm
		self._key = key_mapped
		self._length = length
		self._time_signature = time_signature
		self._meta = meta

	# Service
	@property
	def service(self):
		return self._service

	@service.setter
	def service(self, value: str):
		self._service = value

	# Type
	@property
	def type(self):
		return self._type

	@type.setter
	def type(self, value: str):
		self._type = value

	# Media type
	@property
	def media_type(self):
		return self._media_type

	@media_type.setter
	def media_type(self, value: str):
		self._media_type = value

	# URLs
	@property
	def urls(self):
		return self._urls

	@urls.setter
	def urls(self, value: str | dict):
		self._urls = {self._service: value} if not isinstance(value, dict) else value

	# IDs
	@property
	def ids(self):
		return self._ids

	@ids.setter
	def ids(self, value: str | dict):
		self._ids = {self._service: value} if not isinstance(value, dict) else value

	# Title
	@property
	def title(self):
		return self._title

	@title.setter
	def title(self, value: str):
		self._title = value

	# Censored title
	@property
	def censored_title(self):
		return self._censored_title

	@censored_title.setter
	def censored_title(self, value: str):
		self._censored_title = value

	# Artists
	@property
	def artists(self):
		return self._artists

	@artists.setter
	def artists(self, value: list):
		self._artists = value

	# Collection
	@property
	def collection(self):
		return self._collection

	@collection.setter
	def collection(self, value: object):
		self._collection = value

	# Description
	@property
	def description(self):
		return self._description

	@description.setter
	def description(self, value: str):
		self._description = value
		self._censored_description = censor_text(value)

	# Censored description
	@property
	def censored_description(self):
		return self._censored_description

	@censored_description.setter
	def censored_description(self, value: str):
		self._censored_description = value

	# Release date
	@property
	def release_date(self):
		return self._release_date

	@release_date.setter
	def release_date(self, value: str):
		self._release_date = value

	# Cover
	@property
	def cover(self):
		return self._cover

	@cover.setter
	def cover(self, value: object):
		self._cover = value

	# Genre
	@property
	def genre(self):
		return self._genre

	@genre.setter
	def genre(self, value: str):
		self._genre = value

	# Explicitness
	@property
	def is_explicit(self):
		return self._is_explicit

	@is_explicit.setter
	def is_explicit(self, value: bool):
		self._is_explicit = value

	# BPM
	@property
	def bpm(self):
		return self._bpm

	@bpm.setter
	def bpm(self, value: float):
		self._bpm = value

	# Key (must be set using index from the pitch class guide above)
	@property
	def key(self):
		return self._key

	@key.setter
	def key(self, index):
		"""
			# Pitch class mapping guide
			- 0: 'C'
			- 1: 'C♯/D♭'
			- 2: 'D'
			- 3: 'D♯/E♭'
			- 4: 'E'
			- 5: 'F'
			- 6: 'F♯/G♭'
			- 7: 'G'
			- 8: 'G♯/A♭'
			- 9: 'A'
			- 10: 'A♯/B♭'
			- 11: 'B'
			- -1: None
			- None: None
		"""
		# Accept an index (int or None) that maps to a pitch class via _PITCH_CLASS
		if index not in self._PITCH_CLASS:
			raise ValueError(f"Invalid key index: {index}. Use indices from the pitch class guide.")
		self._key = self._PITCH_CLASS[index]

	# Length
	@property
	def length(self):
		return self._length

	@length.setter
	def length(self, value: int):
		self._length = value

	# Time signature
	@property
	def time_signature(self):
		return self._time_signature

	@time_signature.setter
	def time_signature(self, value: int):
		self._time_signature = f'1/{value}' if value is not None else None

	# Metadata
	@property
	def meta(self):
		return self._meta

	@meta.setter
	def meta(self, value: object):
		self._meta = value

	# JSON representation
	@property
	def json(self):
		meta_val = self._meta.json if hasattr(self._meta, 'json') else self._meta
		return {
			'service': self._service,
			'type': self._type,
			'media_type': self._media_type,
			'urls': self._urls,
			'ids': self._ids,
			'title': self._title,
			'censored_title': self._censored_title,
			'artists': [artist.json_lite for artist in self._artists],
			'collection': self._collection.json_lite if self._collection else None,
			'description': self._description,
			'censored_description': self._censored_description,
			'release_date': self._release_date,
			'cover': self._cover.json_lite if self._cover else None,
			'genre': self._genre,
			'is_explicit': self._is_explicit,
			'bpm': self._bpm,
			'key': self._key,
			'length': self._length,
			'time_signature': self._time_signature,
			'meta': meta_val
		}

	# Light JSON representation (without technical metadata)
	@property
	def json_lite(self):
		return {
			'type': self._type,
			'media_type': self._media_type,
			'urls': self._urls,
			'ids': self._ids,
			'title': self._title,
			'censored_title': self._censored_title,
			'artists': [artist.json_lite for artist in self._artists],
			'collection': self._collection.json_lite if self._collection else None,
			'description': self._description,
			'censored_description': self._censored_description,
			'release_date': self._release_date,
			'cover': self._cover.json_lite if self._cover else None,
			'genre': self._genre,
			'is_explicit': self._is_explicit,
			'bpm': self._bpm,
			'key': self._key,
			'length': self._length,
			'time_signature': self._time_signature
		}



class CollectionKnowledge:

	"""
		# Service Catalog API Collection Knowledge Object

		This is a built-in Service Catalog API object which identifies collection knowledge.
		It provides more details about a collection, such as a small content description, etc.
		JSON representation available.

		 :param	service: The API service in which the object was formed.
		 :param media_type: The song type, can either be `track` or `single`.
		 :param urls: The song's URL(s).
		 :param ids: The song's ID(s).
		 :param title: The song's title.
		 :param artists: The song's artists.
		 :param description: Optional. The song's description.
		 :param release_date: Optional. The song's full release date.
		 :param cover: The song's cover.
		 :param genre: Optional. The song's genre.
		 :param meta: The technical metadata of the song.
	"""

	def __init__(self, service: str, media_type: str, urls: str | dict, ids: str | dict, title: str, artists: list[object], cover: object, meta: object, description: str = None, release_date: str = None, genre: str = None) -> object:
		urls = {service: urls} if not isinstance(urls, dict) else urls
		ids = {service: str(ids)} if not isinstance(ids, dict) else ids
		description = description if description != '?' and description != '' else None
		censored_title = censor_text(title)
		censored_description = censor_text(description)

		self._service = service
		self._type = 'knowledge'
		self._media_type = media_type
		self._urls = urls
		self._ids = ids
		self._title = title
		self._censored_title = censored_title
		self._artists = artists
		self._description = description
		self._censored_description = censored_description
		self._release_date = release_date
		self._cover = cover
		self._genre = genre
		self._meta = meta

	# Service
	@property
	def service(self):
		return self._service

	@service.setter
	def service(self, value: str):
		self._service = value

	# Type
	@property
	def type(self):
		return self._type

	@type.setter
	def type(self, value: str):
		self._type = value

	# Media type
	@property
	def media_type(self):
		return self._media_type

	@media_type.setter
	def media_type(self, value: str):
		self._media_type = value

	# URLs
	@property
	def urls(self):
		return self._urls

	@urls.setter
	def urls(self, value: str | dict):
		self._urls = {self._service: value} if not isinstance(value, dict) else value

	# IDs
	@property
	def ids(self):
		return self._ids

	@ids.setter
	def ids(self, value: str | dict):
		self._ids = {self._service: value} if not isinstance(value, dict) else value

	# Title
	@property
	def title(self):
		return self._title

	@title.setter
	def title(self, value: str):
		self._title = value

	# Censored title
	@property
	def censored_title(self):
		return self._censored_title

	@censored_title.setter
	def censored_title(self, value: str):
		self._censored_title = value

	# Artists
	@property
	def artists(self):
		return self._artists

	@artists.setter
	def artists(self, value: list):
		self._artists = value

	# Description
	@property
	def description(self):
		return self._description

	@description.setter
	def description(self, value: str):
		self._description = value
		self._censored_description = censor_text(value)

	# Censored description
	@property
	def censored_description(self):
		return self._censored_description

	@censored_description.setter
	def censored_description(self, value: str):
		self._censored_description = value

	# Release date
	@property
	def release_date(self):
		return self._release_date

	@release_date.setter
	def release_date(self, value: str):
		self._release_date = value

	# Cover
	@property
	def cover(self):
		return self._cover

	@cover.setter
	def cover(self, value: object):
		self._cover = value

	# Genre
	@property
	def genre(self):
		return self._genre

	@genre.setter
	def genre(self, value: str):
		self._genre = value

	# Metadata
	@property
	def meta(self):
		return self._meta

	@meta.setter
	def meta(self, value: object):
		self._meta = value

	# JSON representation
	@property
	def json(self):
		meta_val = self._meta.json if hasattr(self._meta, 'json') else self._meta
		return {
			'service': self._service,
			'type': self._type,
			'media_type': self._media_type,
			'urls': self._urls,
			'ids': self._ids,
			'title': self._title,
			'censored_title': self._censored_title,
			'artists': [artist.json_lite for artist in self._artists],
			'description': self._description,
			'censored_description': self._censored_description,
			'release_date': self._release_date,
			'cover': self._cover.json_lite if self._cover else None,
			'genre': self._genre,
			'meta': meta_val
		}

	# Light JSON representation (without technical metadata)
	@property
	def json_lite(self):
		return {
			'type': self._type,
			'media_type': self._media_type,
			'urls': self._urls,
			'ids': self._ids,
			'title': self._title,
			'censored_title': self._censored_title,
			'artists': [artist.json_lite for artist in self._artists],
			'description': self._description,
			'censored_description': self._censored_description,
			'release_date': self._release_date,
			'cover': self._cover.json_lite if self._cover else None,
			'genre': self._genre,
		}




class Query:
	def __init__(self, service: str, meta: object, songs: list[object] = None, music_videos: list[object] = None, collections: list[object] = None, artists: list[object] = None, knowledge: list[object] = None):
		self._service = service
		self._type = 'query'
		self._songs = songs if songs != None else []
		self._music_videos = music_videos if music_videos != None else []
		self._collections = collections if collections != None else []
		self._artists = artists if artists != None else []
		self._meta = meta

	# Service
	@property
	def service(self):
		return self._service

	@service.setter
	def service(self, value: str):
		self._service = value

	# Songs
	@property
	def songs(self):
		return self._songs

	@service.setter
	def songs(self, value: list):
		self._songs = value

	# Music videos
	@property
	def music_videos(self):
		return self._music_videos

	@music_videos.setter
	def music_videos(self, value: list):
		self._music_videos = value

	# Collections
	@property
	def collections(self):
		return self._collections

	@collections.setter
	def collections(self, value: list):
		self._collections = value

	# Artists
	@property
	def artists(self):
		return self._artists

	@artists.setter
	def artists(self, value: list):
		self._artists = value

	# Metadata
	@property
	def meta(self):
		return self._meta

	@meta.setter
	def meta(self, value: list):
		self._meta = value

	# JSON representation
	@property
	def json(self):
		meta_val = self._meta.json if hasattr(self._meta, 'json') else self._meta
		return {
			'service': self._service,
			'type': self._type,
			'songs': [song.json_lite for song in self._songs] if self._songs != [] else [],
			'music_videos': [mv.json_lite for mv in self._music_videos] if self._music_videos != [] else [],
			'collections': [collection.json_lite for collection in self._collections] if self._collections != [] else [],
			'artists': [artist.json_lite for artist in self._artists] if self._artists != [] else [],
			'meta': meta_val
		}
	
	# Light JSON representation (without technical metadata)
	@property
	def json_lite(self):
		return {
			'service': self._service,
			'type': self._type,
			'songs': [song.json_lite for song in self._songs] if self._songs != [] else [],
			'music_videos': [mv.json_lite for mv in self._music_videos] if self._music_videos != [] else [],
			'collections': [collection.json_lite for collection in self._collections] if self._collections != [] else [],
			'artists': [artist.json_lite for artist in self._artists] if self._artists != [] else [],
		}
	
print('[ServiceCatalogAPI] Media objects initialized')