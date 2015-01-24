from mongoengine.python_support import str_types
from django.db.models.fields.files import ImageFieldFile
from django.core.files.base import File

from django_town.mongoengine_extension.fields.extra import LocalStorageFileField


class DimensionImageFieldFile(ImageFieldFile):
    pass


class ImageField(LocalStorageFileField):
    proxy_class = ImageFieldFile
    #
    # def __get__(self, instance, owner):
    # if instance is None:
    #         return self
    #
    #     value = instance._data.get(self.name)
    #     file = value['source']
    #
    #     if isinstance(file, str_types) or file is None:
    #         attr = self.proxy_class(instance, self, file)
    #         attr._dimensions_cache = (value['width'], value['height'])
    #         value['source'] = attr
    #         instance._data[self.name] = value
    #
    #     return instance._data[self.name]
    #
    # def __set__(self, instance, value):
    #     key = self.name
    #     source = value
    #     if isinstance(source, File) and not isinstance(source, ImageFieldFile):
    #         value = instance._data.get(self.name)
    #         file = value['source']
    #         value['width'] = file.width
    #         value['height'] = file.height
    #         file._dimensions_cache = (value['width'], value['height'])
    #         if file:
    #             try:
    #                 file.delete()
    #             except:
    #                 pass
    #         # Create a new proxy object as we don't already have one
    #         file_copy = self.proxy_class(instance, self, source.name)
    #         file_copy.file = source
    #         value['source'] = file_copy
    #         instance._data[key] = value
    #     else:
    #         instance._data[key] = value
    #
    #     instance._mark_as_changed(key)

    def __get__(self, instance, owner):
        if instance is None:
            return self

        file = instance._data.get(self.name)

        if isinstance(file, str_types) or file is None:
            attr = self.proxy_class(instance, self, file)
            instance._data[self.name] = attr
        elif isinstance(file, ImageFieldFile):
            file.instance = instance

        return instance._data[self.name]

    def __set__(self, instance, value):
        key = self.name
        if isinstance(value, File) and not isinstance(value, ImageFieldFile):
            file = instance._data.get(self.name)
            if file:
                try:
                    file.delete()
                except:
                    pass
            # Create a new proxy object as we don't already have one
            file_copy = self.proxy_class(instance, self, value.name)
            file_copy.file = value
            instance._data[key] = file_copy
        else:
            instance._data[key] = value

        instance._mark_as_changed(key)

    def to_mongo(self, value):
        if hasattr(value, 'name'):
            return {'source': value.name, 'height': value.height, 'width': value.width}
        return {'source': value, 'height': value.height, 'width': value.width}

    def to_python(self, value):
        value = self.proxy_class(None, self, value['source'])
        value._dimensions_cache = (value['width'], value['height'])
        return value
