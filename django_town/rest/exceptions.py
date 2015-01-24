from django_town.http import http_json_response


class RestError(Exception):
    """
    Default Exception.

    =============  ===================
    http code      message
    =============  ===================
    500            internal_error
    =============  ===================
    """
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
    """
    Runtime Exception.

    =============  ===================
    http code      message
    =============  ===================
    500            internal_error
    =============  ===================
    """
    error = "internal_error"
    status = 500


class RestBadRequest(RestError):
    """
    Bad Request.

    =============  ===================
    http code      message
    =============  ===================
    400            bad_request
    =============  ===================
    """

    error = "bad_request"
    status = 400

    def __init__(self, message=None):
        self.message = message

    def to_dict(self):
        ret = {'error': self.error}
        if self.message:
            ret['message'] = self.message
        return ret


class RestDuplicate(RestBadRequest):
    pass


class RestFormRequired(RestError):
    """
    Form Required

    =============  ===================
    http code      message
    =============  ===================
    400            form_required
    =============  ===================
    """
    error = "form_required"
    status = 400

    def __init__(self, field):
        self.field = field
        # self.message = message

    def to_dict(self):
        return {'error': self.error, 'field': self.field}


class RestFormInvalid(RestError):
    """
    Form Invalid

    =============  ===================
    http code      message
    =============  ===================
    400            form_invalid
    =============  ===================
    """

    error = "form_invalid"
    status = 400

    def __init__(self, field, message=None):
        self.field = field
        self.message = message

    def to_dict(self):
        if self.message:
            return {'error': self.error, 'field': self.field, 'message': self.message}
        return {'error': self.error, 'field': self.field}


class RestFormError(RestError):
    """
    Form Error

    =============  ===================
    http code      message
    =============  ===================
    400            form_error_message
    =============  ===================
    """

    status = 400
    def __init__(self, form_error):
        self.form_error = form_error

    def to_dict(self):
        return self.form_error


class RestUnauthorized(RestError):
    """
    Unauthorized

    =============  ===================
    http code      message
    =============  ===================
    401            unauthorized
    =============  ===================
    """

    error = "unauthorized"
    status = 401


class RestPermissionDenied(RestError):
    """
    Permission Denied

    =============  ===================
    http code      message
    =============  ===================
    401            permission_denied
    =============  ===================
    """

    error = "permission_denied"
    status = 401


class RestForbidden(RestError):
    """
    Forbidden

    =============  ===================
    http code      message
    =============  ===================
    403            forbidden
    =============  ===================
    """

    error = "forbidden"
    status = 403


class RestConflict(RestError):
    """
    Conflict

    =============  ===================
    http code      message
    =============  ===================
    409            conflict
    =============  ===================
    """

    error = "conflict"
    status = 409

    def __init__(self, field=None):
        self.field = field

    def to_dict(self):
        if self.field:
            return {'error': self.error, 'field': self.field}
        return {'error': self.error}


class RestAlreadyExists(RestError):
    """
    Conflict

    =============  ===================
    http code      message
    =============  ===================
    409            already_exists
    =============  ===================
    """

    error = "already_exists"
    status = 409

    def __init__(self, field=None):
        self.field = field

    def to_dict(self):
        if self.field:
            return {'error': self.error, 'field': self.field}
        return {'error': self.error}


class RestNotFound(RestError):
    """
    Not Found

    =============  ===================
    http code      message
    =============  ===================
    404            not_found
    =============  ===================
    """

    error = "not_found"
    status = 404

    def __init__(self, resource=None, resource_name=None):
        self.resource = resource
        self.resource_name = resource_name

    def to_dict(self):
        if self.resource:
            return {'error': self.error, 'resource': self.resource._meta.name}
        elif self.resource_name:
            return {'error': self.error, 'resource': self.resource_name}
        return {'error': self.error}


class RestMethodNotAllowed(RestError):
    """
    Method Not Allowed

    =============  ===================
    http code      message
    =============  ===================
    405            method_not_allowed
    =============  ===================
    """

    error = "method_not_allowed"
    status = 405
