try:
    from django_town.rest.resources import ModelResource
    from django_town.oauth2.models import Client, Service

    class ClientResource(ModelResource):

        class Meta:
            model = Client
            cache_key_format = "_ut_cli:%(pk)s"
            filter = ['id', 'name']
            pk_regex = "[a-zA-Z0-9\-]+"

    class ServiceResource(ModelResource):

        class Meta:
            model = Service
            cache_key_format = "_ut_svc:%(pk)s"

except ImportError:
    from django_town.rest.resources import Resource

    class ClientResource(Resource):

        def instance_to_python(self, resource_instance, fields=None, exclude=None, **kwargs):
            return {}

        class Meta:
            cache_key_format = "_ut_cli:%(pk)s"


    class ServiceResource(Resource):

        def instance_to_python(self, resource_instance, fields=None, exclude=None, **kwargs):
            return {}

        class Meta:
            cache_key_format = "_ut_svc:%(pk)s"

