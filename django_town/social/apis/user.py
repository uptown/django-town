from django_town.rest import RestCollectionApiView, RestDocumentApiView, RestSpecifiedDocumentApiView, \
    RestApiView, RestFormRequired, RestFormInvalid
from django_town.social.resources.user import UserResource
from django_town.social.resources.page import PageLikeResource
from django_town.social.oauth2.permissions import OAuth2Authenticated
from django_town.social.models.device import Device, Client
from django.db import IntegrityError
from django_town.cache.utlis import SimpleCache


class UsersApiView(RestCollectionApiView):
    resource = UserResource(name='user')
    crud_method_names = ['create']


class UserApiView(RestDocumentApiView):
    resource = UserResource(name='user')
    crud_method_names = ['read']


class UserMeApiView(RestSpecifiedDocumentApiView):
    resource = UserResource(name='user')
    crud_method_names = ['read', 'update']
    permission_classes = [OAuth2Authenticated]

    def get_pk(self, request):
        return request.oauth2_user.pk

    @classmethod
    def path(cls):
        return cls.resource._meta.name + "/me"


class UserFollowsApiView(RestCollectionApiView):
    resource = UserResource(name='user')
    crud_method_names = ['create', 'read']


class UserLikesPagesApiView(RestCollectionApiView):
    resource = PageLikeResource()
    crud_method_names = ['read']
    permission_classes = [OAuth2Authenticated]

    def query_set(self, **kwargs):
        return self.resource._meta.model.objects.filter(user=kwargs['pk']). \
            order_by('-created')

    @classmethod
    def path(cls):
        return "users/{}/likes/pages"


class UserMeLikesPagesApiView(RestCollectionApiView):
    resource = PageLikeResource(filter=["-user"])
    crud_method_names = ['read']
    permission_classes = [OAuth2Authenticated]

    def query_set(self, **kwargs):
        return self.resource._meta.model.objects.filter(user=kwargs['request'].oauth2_user.pk). \
            order_by('-created')

    @classmethod
    def path(cls):
        return "users/me/likes/pages"


class UserMeNewsFeedApiView(RestCollectionApiView):
    pass


class DevicesApiView(RestApiView):

    crud_method_names = ['create']
    # permission_classes = [OAuth2Authenticated]

    def create(self, request, **kwargs):
        # print request
        # print request.POST, request.POST.get('client')
        # user = request.oauth2_user
        client_id = request.POST.get('client[client_id]')
        if not client_id:
            raise RestFormRequired("client[client_id]")
        device_identifier = request.POST.get('device_identifier')
        if not device_identifier:
            raise RestFormRequired("device_identifier")
        # print user
        try:
            client_pk = Client.objects.get_cached(client_id=client_id).pk
        except Client.DoesNotExist:
            raise RestFormInvalid("client[client_id]")
        try:
            try:
                device = Device.objects.get(client_id=client_pk, device_identifier=device_identifier)
                if request.POST.get('device_token'):
                    Device.objects.filter(device_token=request.POST.get('device_token')).delete()
                # print "123213"
            except Device.DoesNotExist:
                try:
                    # print "1233"
                    if request.POST.get('device_token'):
                        # print "1235"
                        device = Device.objects.get(device_token=request.POST.get('device_token'))
                    else:
                        # print "fgfg"
                        raise Device.DoesNotExist
                except Device.DoesNotExist:
                    # print "1233"
                    device = Device(client_id=client_pk, device_identifier=device_identifier,
                                    device_token=request.POST.get('device_token'))
                    device.save()
        except IntegrityError:
            # print "asd"
            try:
                device = Device.objects.get(device_token=request.POST.get('device_token'))
                # print "1"
            except Device.DoesNotExist:
                device = Device(device_token=request.POST.get('device_token'), client_id=client_pk,
                               device_identifier=device_identifier)

        if device:
            device.model = request.POST.get('model')
            device.version = request.POST.get('version')
            device.device_version = request.POST.get('device_version', "")
            if request.POST.get('device_token'):
                device.device_token = request.POST.get('device_token')
            if request.POST.get('system_version'):
                device.system_version = request.POST.get('system_version')
            device.system_type = 0 if (request.POST.get('device_type') == 'iOS') else 1
            if request.oauth2_user.pk:
                device.user_id = request.oauth2_user.pk
            device.save()
        if request.oauth2_user.pk:
            SimpleCache("_ut_user_device:%(user_id)s", 60 * 60 * 24 * 14, None).delete(user_id=request.oauth2_user.pk)
        return {}

    @classmethod
    def path(cls):
        return "devices"


class UserMeDeviceApiView(RestApiView):

    crud_method_names = ['update', 'delete']
    permission_classes = [OAuth2Authenticated]

    def update(self, request, device_identifier):
        # print device_identifier, request.PUT, request.oauth2_user.pk
        client_id = request.PUT.get('client[client_id]')
        if not client_id:
            raise RestFormRequired("client[client_id]")
        if not device_identifier:
            raise RestFormRequired("device_identifier")
        # device_token = request.PUT
        # print user
        try:
            client_pk = Client.objects.get_cached(client_id=client_id).pk
        except Client.DoesNotExist:
            raise RestFormInvalid("client[client_id]")
        try:
            try:
                device = Device.objects.get(client_id=client_pk, device_identifier=device_identifier)
                if request.POST.get('device_token'):
                    Device.objects.filter(device_token=request.POST.get('device_token')).delete()
            except Device.DoesNotExist:
                try:
                    if request.POST.get('device_token'):
                        device = Device.objects.get(device_token=request.POST.get('device_token'))
                    else:
                        raise Device.DoesNotExist
                except Device.DoesNotExist:
                    device = Device(client_id=client_pk, device_identifier=device_identifier,
                                    device_token=request.POST.get('device_token'))
                    device.save()
        except IntegrityError:
            try:
                device = Device.objects.get(device_token=request.POST.get('device_token'))
            except Device.DoesNotExist:
                device = Device(device_token=request.POST.get('device_token'), client_id=client_pk,
                               device_identifier=device_identifier)
        if device:
            device.user_id = request.oauth2_user.pk
            device.save()
        if request.oauth2_user.pk:
            SimpleCache("_ut_user_device:%(user_id)s", 60 * 60 * 24 * 14, None).delete(user_id=request.oauth2_user.pk)
        return {}

    def delete(self, request, device_identifier):
        client_id = request.DELETE.get('client[client_id]')
        if not client_id:
            raise RestFormRequired("client[client_id]")
        if not device_identifier:
            raise RestFormRequired("device_identifier")
        # print user
        try:
            client_pk = Client.objects.get_cached(client_id=client_id).pk
        except Client.DoesNotExist:
            raise RestFormInvalid("client[client_id]")
        try:
            device = Device.objects.get(client_id=client_pk, device_identifier=device_identifier)
            if device:
                device.user_id = None
                device.save()
        except Device.DoesNotExist:
            pass
        if request.oauth2_user.pk:
            SimpleCache("_ut_user_device:%(user_id)s", 60 * 60 * 24 * 14, None).delete(user_id=request.oauth2_user.pk)
        return {}

    @classmethod
    def path(cls):
        return "user/me/device/(?P<device_identifier>[a-zA-Z0-9\-]+)"