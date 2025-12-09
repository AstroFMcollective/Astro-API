class Meta:

    """
        # Astro Snitch API (Technical) Metadata Object

        This is a built-in Snitch API object which identifies technical metadata.
        In it are shoved in stats and values useful for debugging or general handling.
        JSON representation available.

         :param service: The API service in which the parent object was formed.
         :param request: The request dictionary (json) of all the data used to make the request.
         :param http_code: The HTTP code returned by an Astro component.
         :param processing_time: The amount of time in milliseconds that an Astro component took to form the orignial media object.
    """

    def __init__(self, service: str, request: dict, processing_time: int | dict, http_code: int | dict):
        self._service = service
        self._request = request
        self._http_code = http_code
        self._processing_time = processing_time if isinstance(processing_time, dict) else {service: processing_time}

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
    def json(self):
        return {
            'request': self._request,
            'http_code': self._http_code,
            'processing_time': self._processing_time,
        }

class Analysis:

    """
        # Astro Snitch API (Technical) Analysis Object

        Represents a single analysis entry produced by an Astro service.
        Holds basic contextual fields and a reference to a Meta-like object
        for technical metadata. Provides properties for controlled access
        and a self-updating JSON representation.

         :param service: The name of the service that performed the analysis.
         :param media_type: The media type (e.g. "image", "video", "audio") analysed.
         :param ai_generated_confidence: Confidence score produced by the AI (0.0 - 1.0).
         :param meta: A Meta-like object containing technical metadata (should provide .json).
    """

    def __init__(self, service: str, media_type: str, ai_generated_confidence: float, meta: object):
        self._service = service
        self._type = 'check'
        self._media_type = media_type
        self._ai_generated_confidence = float(ai_generated_confidence)
        self._meta = meta

    @property
    def service(self):
        return self._service

    @service.setter
    def service(self, value: str):
        self._service = value
    
    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value: str):
        self._type = value

    @property
    def media_type(self):
        return self._media_type

    @media_type.setter
    def media_type(self, value: str):
        self._media_type = value

    @property
    def ai_generated_confidence(self):
        return self._ai_generated_confidence

    @ai_generated_confidence.setter
    def ai_generated_confidence(self, value: float):
        try:
            self._ai_generated_confidence = float(value)
        except (TypeError, ValueError):
            self._ai_generated_confidence = 0.0

    @property
    def meta(self):
        return self._meta

    @meta.setter
    def meta(self, value: object):
        self._meta = value

    @property
    def json(self):
        """
            Self-updating JSON representation of this Analysis instance.
            Serializes nested meta using its .json if available.
        """
        meta_val = self._meta.json if hasattr(self._meta, 'json') else self._meta
        return {
            'service': self._service,
            'type': self._type,
            'media_type': self._media_type,
            'ai_generated_confidence': self._ai_generated_confidence,
            'meta': meta_val,
        }
    
    @property
    def json_lite(self):
        return {
            'service': self._service,
            'type': self._type,
            'media_type': self._media_type,
            'ai_generated_confidence': self._ai_generated_confidence,
        }


class SnitchAnalysis:
    
    """
        # Astro Snitch API (Technical) SnitchAnalysis Object

        Container for one or more Analysis entries related to a particular
        piece of analysed media. Keeps references to the analysed media and
        technical metadata. Provides getters/setters and a self-updating
        JSON representation suitable for serialization.

         :param service: The service grouping these analysis results.
         :param analysis: List of Analysis instances or plain dicts representing analyses.
         :param analysed_media: The media object that was analysed (may provide .json).
         :param meta: A Meta-like object for technical metadata (should provide .json).
    """

    def __init__(self, service: str, analysis: list, analysed_media: object, meta: object):
        self._service = service
        self._type = 'analysis'
        # store a list copy to avoid external mutation
        self._analysis = list(analysis) if analysis is not None else []
        self._analysed_media = analysed_media
        self._meta = meta

    @property
    def service(self):
        return self._service

    @service.setter
    def service(self, value: str):
        self._service = value

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value: str):
        self._type = value

    @property
    def analysis(self):
        return self._analysis

    @analysis.setter
    def analysis(self, value: list):
        self._analysis = list(value) if value is not None else []

    def add_analysis(self, item):
        """Convenience to append an Analysis or dict to the analysis list."""
        self._analysis.append(item)

    @property
    def analysed_media(self):
        return self._analysed_media

    @analysed_media.setter
    def analysed_media(self, value: object):
        self._analysed_media = value

    @property
    def meta(self):
        return self._meta

    @meta.setter
    def meta(self, value: object):
        self._meta = value

    @property
    def json(self):
        """
            Self-updating JSON representation of this SnitchAnalysis instance.
            Serializes nested Analysis entries, analysed_media and meta using their
            .json if available.
        """
        def serialize(obj):
            if hasattr(obj, 'json'):
                return obj.json
            return obj
        
        def serialize_lite(obj):
            if hasattr(obj, 'json_lite'):
                return obj.json_lite
            return obj

        return {
            'service': self._service,
            'type': self._type,
            'analysis': [serialize_lite(a) for a in self._analysis],
            'analysed_media': serialize(self._analysed_media),
            'meta': serialize(self._meta),
        }
    
print("[SnitchAPI] Media objects initialized")
