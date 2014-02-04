try:
    from django_town.rest.resources import ModelResource
    from django_town.oauth2.models import Client, Service

    class ClientResource(ModelResource):
        model = Client
        cache_key_format = "_ut_cli:%(pk)s"


    class ServiceResource(ModelResource):
        model = Service
        cache_key_format = "_ut_svc:%(pk)s"

except ImportError:
    from django_town.rest.resources import Resource

    class ClientResource(Resource):
        cache_key_format = "_ut_cli:%(pk)s"

        def instance_to_python(self, resource_instance, fields=None, exclude=None, **kwargs):
            return {}


    class ServiceResource(Resource):
        cache_key_format = "_ut_svc:%(pk)s"

        def instance_to_python(self, resource_instance, fields=None, exclude=None, **kwargs):
            return {}

