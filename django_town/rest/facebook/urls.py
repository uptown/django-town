from django.conf.urls import patterns, url
from django_town.rest.facebook.views import FacebookOAuth2View, facebook_js_channel

urlpatterns = patterns(
    '',
    url(r'^sign-in$', FacebookOAuth2View.as_view(), name="FacebookOAuth2View"),
    url(r'^channel', facebook_js_channel),
)
