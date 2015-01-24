from django_town.rest import RestApiView, rest_api_manager
from django_town.http import http_json_response
from django_town.cache.utlis import SimpleCache
from django_town.oauth2.swagger import swagger_authorizations_data
from django_town.social.oauth2.permissions import OAuth2Authenticated, OAuth2AuthenticatedOrReadOnly
from django_town.social.permissions import Authenticated, AuthenticatedOrReadOnly


class ApiDocsView(RestApiView):
    def read(self, request, api_version):
        def load_cache(api_version="alpha"):
            manager = rest_api_manager(api_version)

            ret = {'title': manager.name,
                   'description': manager.description,
                   'apiVersion': manager.api_version, 'swaggerVersion': "1.2", 'basePath': manager.base_url,
                   'resourcePath': manager.base_url, 'info': manager.info,
                   'authorizations': swagger_authorizations_data()}
            apis = []
            models = {
                "Error": {
                    "id": "Error",
                    "required": ['error'],
                    "properties": {
                        "error": {
                            "type": "string"
                        },
                        "field": {
                            "type": "string"
                        },
                        "message": {
                            "type": "string"
                        },
                        "resource": {
                            "type": "string"
                        }
                    }
                }
            }
            for view_cls in manager.api_list:
                operations = []
                global_params = []
                path = view_cls.path()
                if path == "":
                    continue
                if '{}' in path:
                    path = path.replace('{}', '{pk}')
                    global_params.append(
                        {
                            "paramType": "path",
                            "name": 'pk',
                            "description": 'primary key for object',
                            "dataType": 'integer',
                            "format": 'int64',
                            "required": True,
                        }
                    )
                responseMessages = [
                    {
                        'code': 404,
                        "message": "not_found",
                        "responseModel": "Error"
                    },
                    {
                        'code': 500,
                        "message": "internal_error",
                        "responseModel": "Error"
                    },
                    {
                        'code': 409,
                        "message": "method_not_allowed",
                        "responseModel": "Error"
                    },
                    {
                        'code': 409,
                        "message": "conflict",
                        "responseModel": "Error"
                    },
                    {
                        'code': 403,
                        "message": "forbidden",
                        "responseModel": "Error"
                    },
                    {
                        'code': 401,
                        "message": "permission_denied",
                        "responseModel": "Error"
                    },
                    {
                        'code': 401,
                        "message": "unauthorized",
                        "responseModel": "Error"
                    },
                    {
                        'code': 400,
                        "message": "form_invalid",
                        "responseModel": "Error"
                    },
                    {
                        'code': 400,
                        "message": "form_required",
                        "responseModel": "Error"
                    },
                    {
                        'code': 400,
                        "message": "bad_request",
                        "responseModel": "Error"
                    },
                ]
                current_api = {
                    'path': path,
                    'description': view_cls.__doc__,
                }
                operations = []

                if 'create' in view_cls.crud_method_names and hasattr(view_cls, 'create'):
                    create_op = {
                        'method': 'POST',
                        'parameters': global_params,
                        'responseMessages': responseMessages,
                        'nickname': 'create ' + path,
                    }
                    operations.append(create_op)
                if 'read' in view_cls.crud_method_names and hasattr(view_cls, 'read'):
                    op = {
                        'method': 'GET',
                        'responseMessages': responseMessages,
                        'nickname': 'read ' + path
                    }
                    params = global_params.copy()

                    for each_permission in view_cls.permission_classes:
                        if issubclass(each_permission, OAuth2Authenticated):
                            params.append(
                                {
                                    "paramType": "query",
                                    "name": 'access_token',
                                    "dataType": 'string',
                                    "required": True,
                                }
                            )
                    if hasattr(view_cls, 'read_safe_parameters'):
                        for each in view_cls.read_safe_parameters:
                            if isinstance(each, tuple):
                                if each[1] == int:
                                    params.append(
                                        {
                                            "paramType": "query",
                                            "name": each[0],
                                            "dataType": 'int',
                                            "format": 'int64',
                                            "required": True,
                                        }
                                    )
                                elif each[1] == float:
                                    params.append(
                                        {
                                            "paramType": "query",
                                            "name": each[0],
                                            "dataType": 'float',
                                            "format": 'float',
                                            "required": True,
                                        }
                                    )
                                else:
                                    params.append(
                                        {
                                            "paramType": "query",
                                            "name": each[0],
                                            "dataType": 'string',
                                            "required": True,
                                        }
                                    )
                            else:
                                params.append(
                                    {
                                        "paramType": "query",
                                        "name": each,
                                        "dataType": 'string',
                                        "required": True,
                                    }
                                )
                                pass
                        pass
                    op['parameters'] = params
                    operations.append(op)
                if 'update' in view_cls.crud_method_names and hasattr(view_cls, 'update'):
                    op = {
                        'method': 'UPDATE',
                        'parameters': global_params,
                        'responseMessages': responseMessages,
                        'errorResponses': [],
                        'nickname': 'read ' + path,
                    }
                    operations.append(op)
                if 'delete' in view_cls.crud_method_names and hasattr(view_cls, 'delete'):
                    op = {
                        'method': 'DELETE',
                        'parameters': global_params,
                        'responseMessages': responseMessages,
                        'errorResponses': [],
                        'nickname': 'read ' + path,
                    }
                    operations.append(op)
                current_api['operations'] = operations
                apis.append(current_api)

            ret['apis'] = apis
            ret["models"] = models
            return ret

        ret = SimpleCache(key_format="api-doc:%(api_version)s", duration=60 * 60 * 24,
                          load_callback=load_cache).get(api_version=api_version)
        response = http_json_response(ret)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET"
        response["Access-Control-Max-Age"] = "1000"
        response["Access-Control-Allow-Headers"] = "*"
        return response
