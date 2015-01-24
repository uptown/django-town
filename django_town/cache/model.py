from django.core.exceptions import ObjectDoesNotExist
from django.db import models, transaction, IntegrityError
from django.forms.models import model_to_dict
from django.utils.functional import cached_property, LazyObject

from django_town.core.settings import CORE_SETTINGS
from django_town.cache.manager import defaultCacheManager
from django_town.utils import CurrentTimestamp
from django.utils.six import iteritems


class CachedObject(LazyObject):
    def __init__(self, cached_dict, model, db_object=None):
        assert cached_dict or db_object
        if db_object:
            self._wrapped = db_object
        self.__dict__['_model'] = model
        self.__dict__['_cached_dict'] = cached_dict
        super(CachedObject, self).__init__()

    def getattr(self, name, default=None):

        if self.__dict__['_cached_dict'] and name in self.__dict__['_cached_dict']:
            return self.__dict__['_cached_dict']['name']

        return super(CachedObject, self).__getattr__(name, default=default)

    def _setup(self):
        self._wrapped = self.__dict__['_model'].objects.get(
            pk=self.__dict__['_cached_dict'][self.__dict__['_model']._meta.pk.name])


class CachingManager(models.Manager):
    def get_cached(self, **kwargs):
        key = self.cache_key(**kwargs)
        ret = defaultCacheManager.get(key)
        if not ret:
            db_object = super(CachingManager, self).get(**kwargs)
            ret = model_to_dict(db_object)
            ret['__cached_date'] = CurrentTimestamp()()
            defaultCacheManager.set(key, ret, self.cache_duration)
            return CachedObject(ret, self.model, db_object=db_object)
        return CachedObject(ret, self.model)

    # def get(self, **kwargs):
    # try:
    #         return super(CachingManager, self).get(**kwargs)
    #     except ObjectDoesNotExist:
    #         try:
    #             defaultCacheManager.delete(self.cache_key(**kwargs))
    #         except KeyError:
    #             pass
    #         raise

    def get_or_create_safe(self, **kwargs):
        created = False
        try:
            ret = self.get_cached(**kwargs)
        except ObjectDoesNotExist:
            with transaction.atomic():
                try:
                    self.create(**kwargs)
                    created = True
                except IntegrityError:
                    pass
            ret = self.get_cached(**kwargs)

        return ret, created

    @cached_property
    def cache_key_format(self):
        assert self.model
        return CORE_SETTINGS.CACHE_PREFIX + ":" + self.model.cache_key_format

    @cached_property
    def cache_duration(self):
        assert self.model
        return getattr(self.model, "cache_duration", CORE_SETTINGS.DEFAULT_CACHE_DURATION)

    def cache_key(self, **kwargs):
        param = {}
        for key, val in iteritems(kwargs):
            if isinstance(val, models.Model):
                param[key + "__pk"] = val.pk
            else:
                param[key] = val
        return self.cache_key_format % param

    def cache_key_with_instance(self, instance):
        param = {}
        for field in instance.__class__._meta.fields:
            field_name = field.name
            val = getattr(instance, field_name)
            if isinstance(val, models.Model):
                param[field_name + "__pk"] = val.pk
            else:
                param[field_name] = val
        return self.cache_key_format % param


class CachingRelatedManager(CachingManager):
    use_for_related_fields = True


class CachingModel(models.Model):
    # def delete_with_cache(self):
    #     defaultCacheManager.delete(self.__class__.objects.cache_key_with_instance(self))
    #     return super(CachingModel, self).delete()
    #
    # def save_with_cache(self, *args, **kwargs):
    #     defaultCacheManager.delete(self.__class__.objects.cache_key_with_instance(self))
    #     return super(CachingModel, self).save(*args, **kwargs)
    #
    # save = save_with_cache
    # delete = delete_with_cache
    objects = CachingManager()

    class Meta:
        abstract = True