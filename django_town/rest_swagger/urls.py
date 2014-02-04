from django.conf.urls import patterns, url
from django_town.rest_swagger.views import ApiDocsView


urlpatterns = patterns('',
    url(r'^api-docs/(?P<api_version>[\w\.]+)$', ApiDocsView.as_rest_view()),
)
