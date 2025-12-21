class Query:
    def __init__(self, service: str, meta: object, songs: list[object] = None, music_videos: list[object] = None, collections: list[object] = None, artists: list[object] = None, knowledge: list[object] = None):
        self._service = service
        self._type = 'query'
        self._songs = songs if songs != None else []
        self._music_videos = music_videos if music_videos != None else []
        self._collections = collections if collections != None else []
        self._artists = artists if artists != None else []
        self._knowledge = knowledge if knowledge != None else []
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

    @service.setter
    def music_videos(self, value: list):
        self._music_videos = value

    # Collections
    @property
    def collections(self):
        return self._collections

    @service.setter
    def collections(self, value: list):
        self._collections = value

    # Artists
    @property
    def artists(self):
        return self._artists

    @service.setter
    def artists(self, value: list):
        self._artists = value

    # Knowledge
    @property
    def knowledge(self):
        return self._knowledge

    @service.setter
    def knowledge(self, value: list):
        self._knowledge = value

    # Metadata
    @property
    def meta(self):
        return self._meta

    @service.setter
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
            'knowledge': [knowledge.json_lite for knowledge in self._knowledge] if self._knowledge != [] else [],
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
            'knowledge': [knowledge.json_lite for knowledge in self._knowledge] if self._knowledge != [] else [],
        }