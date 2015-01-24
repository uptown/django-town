from django_town.oauth2.errors import InvalidRequestError


class OAuth2User(object):

    def __init__(self, django_user):
        if django_user is None:
            raise InvalidRequestError()
        self._django_user = django_user

    @property
    def pk(self):
        return self._django_user.pk

    @property
    def id(self):
        return self._django_user.id
