from django_town.rest import RestDocumentApiView, RestNotFound
from django_town.social.resources.oauth2 import ClientResource, Client


class ClientApiView(RestDocumentApiView):
    resource = ClientResource(name='client', filter=['id', 'name', 'client_min_version', 'client_cur_version',
                                                     'client_store_id'])
    crud_method_names = ['read']


    def read(self, request, pk):
        try:
            client = Client.objects.get(client_id=pk)
        except Client.DoesNotExist:
            raise RestNotFound()
        return self.resource(client.pk, instance=client).to_dict(request=request)


