from django_town.rest.resources import MongoResource
from django_town.social.documents import Post


class PostResource(MongoResource):
    document = Post
    cache_key_format = "_ut_post:%(pk)s"