from django.db import models
from django.utils import timezone


class Site(models.Model):
    name = models.CharField(max_length=60, db_index=True)
    about = models.TextField(default="")
    category = models.SmallIntegerField(default=0)
    url = models.URLField()
    created = models.DateTimeField(default=timezone.now)
    # photo = ImageField(upload_to='image/page/', default=None, null=True, blank=True)

    class Meta:
        app_label = 'social'
