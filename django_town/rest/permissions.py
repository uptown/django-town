#from __future__ import unicode_literals

from django.http import Http404

from django_town.rest.exceptions import RestUnauthorized


SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS']


class BasePermission(object):
    def check_permission(self, request, *args, **kwargs):
        pass


class OrPermissionClass(BasePermission):

    def __init__(self, permissions):
        self._permissions = permissions

    def check_permission(self, request, *args, **kwargs):
        for each_permission in self._permissions:
            try:
                each_permission().check_permission(request, *args, **kwargs)
            except RestUnauthorized:
                pass
        raise RestUnauthorized()

    def __call__(self, *args, **kwargs):
        #TODO check speed and change structure
        new_permission_class = type("NewPermissionClass", (BasePermission, ), {})
        new_permission_class._permissions = self._permissions
        new_permission_class.check_permission = self.check_permission
        return new_permission_class()


class AllowAny(BasePermission):
    """
    Allows any access
    """
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


