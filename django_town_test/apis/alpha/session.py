from django_town.rest import RestApiView, RestFormInvalid, RestFormRequired
from django.contrib import auth


class SessionApiView(RestApiView):

    crud_method_names = ['create', 'delete']

    def create(self, request):
        data = request.POST
        if data:
            if 'facebook_access_token' in data:
                user = auth.authenticate(type="facebook", access_token=data['facebook_access_token'])
                if user:
                    auth.login(request, user)
                    return {}
                raise RestFormInvalid('facebook_access_token')
            elif 'google_access_token' in data:
                user = auth.authenticate(type="google", access_token=data['google_access_token'])
                if user:
                    auth.login(request, user)
                    return {}
                raise RestFormInvalid('facebook_access_token')
        raise RestFormRequired('email')

    def delete(self, request):
        if request.user.is_authenticated():
            auth.logout(request)
        return {}

    @classmethod
    def path(cls):
        return "sessions"