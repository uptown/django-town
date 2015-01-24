from django_town.rest import RestApiView
from django_town.social.forms import SignInForm
from django.contrib import auth
from django_town.rest.exceptions import RestNotFound, RestFormInvalid


class SessionsApiView(RestApiView):
    crud_method_names = ['create', 'delete']

    def create(self, request, **kwargs):
        form = SignInForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = auth.authenticate(username=email, password=password)
            if not user:
                raise RestNotFound(resource_name="user")
            auth.login(request, user)
            return {}

        if form['email'].errors:
            raise RestFormInvalid('email')
        raise RestFormInvalid('password')

    def delete(self, request, **kwargs):
        auth.logout(request)
        return {}

    @classmethod
    def path(cls):
        return "sessions"