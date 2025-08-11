from rest_framework.renderers import JSONRenderer

class GeoJSONRenderer(JSONRenderer):
    media_type = 'application/geo+json'
    format = 'geojson'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return super().render(data, accepted_media_type, renderer_context)

    def get_media_type(self, accepted_media_type):
        if accepted_media_type in ('application/geo+json', 'application/json'):
            return accepted_media_type
        return self.media_type