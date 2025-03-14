from AstroAPI.components.ini import config



"""
	--- MEDIA OBJECTS ---

	This is the reference sheet of all Astro's supported media types.
	
	NOTE: Some of these aren't used *yet*

	This is a more sophisticated method of forming media objects, so devs have to work less
	to get nice, proper media objects. 

	All objects must contain a service, type and meta (technical metadata) variables.
"""



class Error:
	"""
		# Astro Error Object

		This is a built-in Astro API object which identifies errors.
		Use this to return *a thing* when something internally goes wrong.

		 :param	service: The API service in which the object was formed.
		 :param component: The API service component in which the object was formed.
		 :param error_msg: Optional, but recommended. The error message of the error.
		 :param meta: The technical metadata of this object.
	"""
	def __init__(self, service: str, component: str, meta: object, error_msg: str = None) -> object:
		self.service = service
		self.type = 'error'
		self.component = component
		self.error_msg = error_msg
		self.meta = meta

class Empty:
	"""
		# Astro Empty Object

		This is a built-in Astro API object which identifies empty responses.
		Use this to return *a thing* when a service you're using doesn't end up
		returning anything/returns an empty response.

		 :param	service: The API service in which the object was formed.
		 :param meta: The technical metadata of this object.
	"""
	def __init__(self, service: str, meta: object) -> object:
		self.service = service
		self.type = 'empty_response'
		self.meta = meta

class Meta:
	"""
		# Astro (Technical) Metadata Object

		This is a built-in Astro API object which identifies technical metadata.
		In it are shoved in stats and values useful for debugging or general
		handling.
		This is pretty much mandatory for every media object.

		 :param	service: The API service in which the object was formed.
		 :param request: The request dictionary (json) of all the data used to make the request.
		 :param http_code: Optional. The HTTP code returned by an Astro component.
		 :param processing_time: The amount of time in milliseconds that an Astro component took to form the orignial media object.
		 :param filter_confidence_percentage: Optional. Astro's confidence it got the correct media object.
	"""
	def __init__(self, service: str, request: dict, processing_time: int | dict, filter_confidence_percentage: dict = None, http_code: int = None):
		self.service = service
		self.request = request
		self.http_code = http_code
		self.processing_time = {service: processing_time} if isinstance(processing_time, int) else processing_time
		self.filter_confidence_percentage = filter_confidence_percentage

class Song:
	"""
		# Astro Song Object

		This is a built-in Astro API object which identifies songs.
		Astro identifies two types of songs: tracks and singles.
		It's an unwritten rule, but Astro should sort tracks as songs off albums, while
		singles are standalone tracks and tracks from EP-s.

		 :param	service: The API service in which the object was formed.
		 :param type: The song type, can either be `track` or `single`.
		 :param url: The song's URL(s).
		 :param id: The song's ID(s).
		 :param title: The song's title.
		 :param artists: The song's artists.
		 :param collection: The song's collection (album or EP).
		 :param genre: Optional. The song's genre.
		 :param is_explicit: Optional. Whether the song is explicit or not.
		 :param cover_url: The song's cover art URL.
		 :param cover_color_hex: The hex code of the average color of the song's cover art.
		 :param meta: The technical metadata of this song.
	"""
	def __init__(self, service: str, type: str, url: str | dict, id: any, title: str, artists: list, cover_url: str, meta: object, cover_color_hex: int = None, collection: str = None, genre: str = None, is_explicit: bool = None) -> object:
		self.service = service
		self.type = type
		self.url = {service: url} if isinstance(url, str) else url
		self.id = {service: str(id)} if not isinstance(id, dict) else id
		self.title = title
		self.censored_title = title
		self.collection = collection
		self.artists = artists
		self.cover_url = cover_url
		self.cover_color_hex = cover_color_hex
		self.genre = genre
		self.is_explicit = is_explicit
		self.meta = meta

class MusicVideo:
	"""
		# Astro Music Video Object

		This is a built-in Astro API object which identifies music videos.
		
		 :param	service: The API service in which the object was formed.
		 :param url: The music video's URL(s).
		 :param id: The music video's ID(s).
		 :param title: The music video's title.
		 :param artists: The music video's artists.
		 :param genre: Optional. The music video's genre.
		 :param is_explicit: Optional. Whether the music video is explicit or not.
		 :param thumbnail_url: The music video's thumbnail URL.
		 :param thumbnail_color_hex: The hex code of the average color of the music video's thumbnail.
		 :param meta: The technical metadata of this music video.
	"""
	def __init__(self, service: str, url: str | dict, id: any, title: str, artists: list, thumbnail_url: str, meta = object, thumbnail_color_hex: int = None, is_explicit: bool = None, genre: str = None) -> object:
		self.service = service
		self.type = 'music_video'
		self.url = {service: url} if isinstance(url, str) else url
		self.id = {service: str(id)} if not isinstance(id, dict) else id
		self.title = title
		self.censored_title = title
		self.artists = artists
		self.thumbnail_url = thumbnail_url
		self.thumbnail_color_hex = thumbnail_color_hex
		self.genre = genre
		self.is_explicit = is_explicit
		self.meta = meta

class Collection:
	def __init__(self, service: str, type: str, url: str | dict, id: any, title: str, artists: list, cover_url: str, meta = object, cover_color_hex: int = None, release_year: int = None, genre: str = None) -> object:
		self.service = service
		self.type = type
		self.url = {service: url} if isinstance(url, str) else url
		self.id = {service: str(id)} if not isinstance(id, dict) else id
		self.title = title
		self.censored_title = title
		self.artists = artists
		self.release_year = None if release_year == None else int(release_year)
		self.cover_url = cover_url
		self.cover_color_hex = cover_color_hex
		self.genre = genre
		self.meta = meta

class Podcast:
	def __init__(self, service: str, url: str | dict, id: any, title: str, publisher: str, cover_url: str, is_explicit: bool, meta = object, cover_color_hex: int = None) -> object:
		self.service = service
		self.type = 'podcast'
		self.url = {service: url} if isinstance(url, str) else url
		self.id = {service: str(id)} if not isinstance(id, dict) else id
		self.title = title
		self.censored_title = title
		self.publisher = publisher
		self.cover_url = cover_url
		self.cover_color_hex = cover_color_hex
		self.is_explicit = is_explicit
		self.meta = meta

class PodcastEpisode:
	def __init__(self, service: str, url: str | dict, id: any, title: str, release_year: str, cover_url: str, is_explicit: bool, meta = object, cover_color_hex: int = None) -> object:
		self.service = service
		self.type = 'podcast_episode'
		self.url = {service: url} if isinstance(url, str) else url
		self.id = {service: str(id)} if not isinstance(id, dict) else id
		self.title = title
		self.censored_title = title
		self.release_year = None if release_year == None else int(release_year)
		self.cover_url = cover_url
		self.cover_color_hex = cover_color_hex
		self.is_explicit = is_explicit
		self.meta = meta

class Playlist:
	def __init__(self, service: str, url: str | dict, id: any, title: str, owner: str, songs: list, cover_url: int, meta = object, cover_color_hex: int = None) -> object:
		self.service = service
		self.type = 'playlist'
		self.url = {service: url} if isinstance(url, str) else url
		self.id = {service: str(id)} if not isinstance(id, dict) else id
		self.title = title
		self.censored_title = title
		self.owner = owner
		self.songs = songs
		self.cover_url = cover_url
		self.cover_color_hex = cover_color_hex
		self.meta = meta

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
	def __init__(self, service: str, url: str | dict, id: any, name: str, meta = object, profie_pic_url: str = None, profile_pic_color_hex: int = None, genres: list = None) -> object:
		self.service = service
		self.type = 'artist'
		self.url = {service: url} if isinstance(url, str) else url
		self.id = {service: str(id)} if not isinstance(id, dict) else id
		self.name = name
		self.genres = genres
		self.profile_pic_url = profie_pic_url if profie_pic_url != None else 'https://developer.valvesoftware.com/w/images/thumb/8/8b/Debugempty.png/200px-Debugempty.png'
		self.profile_pic_color_hex = profile_pic_color_hex
		self.meta = meta

class Cover:
	def __init__(self, service: str, type: str, hq_url: str | dict, lq_url: str | dict, title: str, artists: list, meta = object, color_hex: int = None) -> object:
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
		self.description = description if description != '?' else None
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
