from django.db import models



#
# class Country(models.Model):
# name = models.CharField(max_length=200, unique=True)
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

class AddressComponentType(models.Model):
    name = models.CharField(max_length=50, unique=True)


class AddressComponent(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    ascii_name = models.CharField(max_length=200)
    parent = models.ForeignKey("AddressComponent", default=None, null=True)
    types = models.ManyToManyField(AddressComponentType)
    depth = models.SmallIntegerField(db_index=True)

    class Meta:
        unique_together = ('parent', 'name')
        app_label = 'social'

