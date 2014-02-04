from django.db import models
from django_town.social.define import ADDRESS_COMPONENT_TYPES
from django.utils.http import int_to_base36

#
# class Country(models.Model):
#     name = models.CharField(max_length=200, unique=True)
#     ascii_name = models.CharField(max_length=200, db_index=True)
#
#     class Meta:
#         app_label = 'social'
#
#
# class Locality(models.Model):
#     name = models.CharField(max_length=200)
#     ascii_name = models.CharField(max_length=200, db_index=True)
#     country = models.ForeignKey(Country)
#
#     class Meta:
#         unique_together = ('name', 'country')
#         app_label = 'social'


class AddressComponent(models.Model):
    code = models.CharField(max_length=40, unique=True, default=0)
    name = models.CharField(max_length=200, db_index=True)
    ser_no = models.SmallIntegerField(db_index=True, default=0)
    ascii_name = models.CharField(max_length=200)
    parent = models.ForeignKey("AddressComponent", default=None, null=True)
    type = models.SmallIntegerField(choices=ADDRESS_COMPONENT_TYPES)
    children_count = models.SmallIntegerField(default=0)

    class Meta:
        unique_together = ('parent', 'name')
        app_label = 'social'