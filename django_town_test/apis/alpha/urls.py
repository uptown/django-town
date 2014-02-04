from django_town_test.apis.alpha.session import SessionApiView
from django_town.rest import rest_api_manager
from django_town.social.apis import register_django_town_social

rest_api_manager('alpha').register_rest_api_view(SessionApiView)
register_django_town_social(rest_api_manager('alpha'))
urlpatterns = rest_api_manager('alpha').patterns
# )
