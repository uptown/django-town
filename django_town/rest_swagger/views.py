from django_town.rest import RestApiView, rest_api_manager
from django_town.http import http_json_response
from django_town.cache import SimpleCache


class ApiDocsView(RestApiView):

    def read(self, request, api_version):
        def load_cache(api_version="alpha"):
            manager = rest_api_manager(api_version)
            ret = {'apiVersion': manager.api_version, 'swaggerVersion': "1.2", 'basePath': manager.base_url,
                   'resourcePath': manager.base_url}
            apis = []
            for view_cls in manager.api_list:
                operations = []
                global_params = []
                path = view_cls.path()
                if '{}' in path:
                    path = path.replace('{}', '{pk}')
                    global_params.append({"paramType": "path",
                                          "name": 'pk',
                                          "description": 'primary key for object',
                                          "dataType": 'integer',
                                          "format": 'int64',
                                          "required": True,
                    })
                current_api = {
                    'path': path,
                    'description': view_cls.__doc__,
                }
                operations = []
                if 'create' in view_cls.crud_method_names and hasattr(view_cls, 'create'):
                    create_op = {
                        'httpMethod': 'POST',
                        'parameters': global_params,
                        'responseClass': 'string',
                        'errorResponses': [],
                        'nickname': 'create ' + path,
                    }
                    operations.append(create_op)
                if 'read' in view_cls.crud_method_names and hasattr(view_cls, 'read'):
                    create_op = {
                        'httpMethod': 'GET',
                        'parameters': global_params,
                        'responseClass': 'string',
                        'errorResponses': [],
                        'nickname': 'read ' + path,
                    }
                    operations.append(create_op)
                if 'update' in view_cls.crud_method_names and hasattr(view_cls, 'update'):
                    create_op = {
                        'httpMethod': 'UPDATE',
                        'parameters': global_params,
                        'responseClass': 'string',
                        'errorResponses': [],
                        'nickname': 'read ' + path,
                    }
                    operations.append(create_op)
                if 'delete' in view_cls.crud_method_names and hasattr(view_cls, 'delete'):
                    create_op = {
                        'httpMethod': 'DELETE',
                        'parameters': global_params,
                        'responseClass': 'string',
                        'errorResponses': [],
                        'nickname': 'read ' + path,
                    }
                    operations.append(create_op)
                current_api['operations'] = operations
                apis.append(current_api)

            ret['apis'] = apis
            return ret
        ret = SimpleCache(key_format="api-doc:%(api_version)s", duration=60*60*24,
                          load_callback=load_cache).get(api_version=api_version)
        response = http_json_response(ret)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET"
        response["Access-Control-Max-Age"] = "1000"
        response["Access-Control-Allow-Headers"] = "*"
        return response
