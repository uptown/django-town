from django_town.rest import RestCollectionApiView, RestDocumentApiView
from django_town.social.resources.user import UserResource


class UsersApiView(RestCollectionApiView):

    resource = UserResource(name='user')
    crud_method_names = ['create']


class UserApiView(RestDocumentApiView):

    resource = UserResource(name='user')
    crud_method_names = ['read']
