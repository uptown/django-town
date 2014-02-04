from __future__ import unicode_literals
from django.http import Http404
from django_town.rest.exceptions import RestUnauthorized

SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS']



class BasePermission(object):
    def check_permission(self, request, *args, **kwargs):
        pass


class AllowAny(BasePermission):
    pass


class IsAuthenticated(BasePermission):
    """
    Allows access only to authenticated users.
    """
    def check_permission(self, request, *args, **kwargs):
        if self.is_authenticated(request):
            return
        raise RestUnauthorized()

    def is_authenticated(self, request):
        if request.user and request.user.is_authenticated():
            return True
        return False


class IsAdminUser(BasePermission):
    """
    Allows access only to admin users.
    """
    def check_permission(self, request, *args, **kwargs):
        if request.user and request.user.is_staff:
            return
        raise Http404


class IsAuthenticatedOrReadOnly(IsAuthenticated):
    """
    The request is authenticated as a user, or is a read-only request.
    """

    def check_permission(self, request, *args, **kwargs):
        if (request.method in SAFE_METHODS) or self.is_authenticated(request):
            return
        raise RestUnauthorized()


