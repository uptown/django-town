from django_town.social.apis.post import PostApiView, PostsApiView
from django_town.social.apis.user import UsersApiView, UserApiView
from django_town.social.apis.place import PlaceApiView, PlacesApiView


def register_django_town_social(manager, exclude=None):
    manager.register_rest_api_view(PostApiView)
    manager.register_rest_api_view(PostsApiView)
    manager.register_rest_api_view(UserApiView)
    manager.register_rest_api_view(UsersApiView)
    manager.register_rest_api_view(PlaceApiView)
    manager.register_rest_api_view(PlacesApiView)