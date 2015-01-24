from django.conf.urls import patterns, url
from django_town.oauth2.views import TokenView, AuthorizeView, CheckPermissionView

urlpatterns = patterns('',
    url(r'token', TokenView.as_view(), name="OAuth2TokenView"),
    url(r'authorize', AuthorizeView.as_view()),
    url(r'check-permission', CheckPermissionView.as_view()),
)
