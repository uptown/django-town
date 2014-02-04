from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^alpha/', include('django_town_test.apis.alpha.urls')),
)
