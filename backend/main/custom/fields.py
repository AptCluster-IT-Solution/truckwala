from rest_framework import serializers


class ImageUrlField(serializers.RelatedField):  # noqa
    def to_representation(self, instance):
        url = instance.image.url
        request = self.context.get('request', None)
        if request is not None:
            return request.build_absolute_uri(url)
        return url
