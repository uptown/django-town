from django_town.rest.permissions import BasePermission, SAFE_METHODS
from django_town.rest.exceptions import RestUnauthorized


class Authenticated(BasePermission):
    """
    Allows access only to authenticated users.
    """

    def check_permission(self, request, *args, **kwargs):
        if self.is_authenticated(request):
            return
        raise RestUnauthorized()

    def is_authenticated(self, request):
        if request.is_authenticated():
            return True
        return False


class AuthenticatedOrReadOnly(Authenticated):
    """
    The request is authenticated as a user, or is a read-only request.
    """

    def check_permission(self, request, *args, **kwargs):
        if (request.method in SAFE_METHODS) or self.is_authenticated(request):
            return
        raise RestUnauthorized()
