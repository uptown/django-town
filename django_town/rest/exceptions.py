from django_town.http import http_json_response


class RestError(Exception):

    error = "internal_error"
    status = 500

    def to_dict(self):
        return {'error': self.error}

    def to_response(self, suppress_http_code=False):
        if suppress_http_code:
            ret = self.to_dict()
            ret['_http_status_code'] = self.status
            return http_json_response(ret)
        return http_json_response(self.to_dict(), status=self.status)


class RestRuntimeError(RestError):

    error = "internal_error"
    status = 500


class RestBadRequest(RestError):

    error = "bad_request"
    status = 400


class RestFormRequired(RestError):

    error = "form_required"
    status = 400

    def __init__(self, field):
        self.field = field

    def to_dict(self):
        if self.field:
            return {'error': self.error, 'field': self.field}
        return {'error': self.error}


class RestFormInvalid(RestError):

    error = "form_invalid"
    status = 400

    def __init__(self, field):
        self.field = field

    def to_dict(self):
        if self.field:
            return {'error': self.error, 'field': self.field}
        return {'error': self.error}


class RestUnauthorized(RestError):

    error = "unauthorized"
    status = 401


class RestPermissionDenied(RestError):

    error = "permission_denied"
    status = 401


class RestForbidden(RestError):

    error = "forbidden"
    status = 403


class RestNotFound(RestError):

    error = "not_found"
    status = 404

    def __init__(self, resource):
        self.resource = resource

    def to_dict(self):
        if self.resource:
            return {'error': self.error, 'resource': self.resource.name}
        return {'error': self.error}

class RestMethodNotAllowed(RestError):

    error = "method_not_allowed"
    status = 405
