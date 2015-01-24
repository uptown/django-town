from django_town.mongoengine_extension.fields.extra import LocalStorageFileField
from django_town.helper.thumbnail import ThumbnailFile


class ThumbnailImageField(LocalStorageFileField):
    proxy_class = ThumbnailFile

    def __init__(self, sizes=None, **kwargs):
        self.sizes = sizes
        super(ThumbnailImageField, self).__init__(**kwargs)
