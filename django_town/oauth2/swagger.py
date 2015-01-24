from copy import copy
from django_town.core.settings import OAUTH2_SETTINGS


OAUTH2_SWAGGER = {
    "oauth2": {
      "type": "oauth2",
      "scopes": [
      ],
      "grantTypes": {
        # "implicit": {
        #   "loginEndpoint": {
        #     "url": ""
        #   },
        #   "tokenName": "access_token"
        # },
        "authorization_code": {
          "tokenRequestEndpoint": {
            "clientIdName": "client_id",
            "clientSecretName": "client_secret"
          },
          "tokenEndpoint": {
            "tokenName": "access_token"
          }
        }
      }
    }
}


def swagger_authorizations_data():
    ret = copy(OAUTH2_SWAGGER)
    ret['oauth2']['grantTypes']['authorization_code']['tokenRequestEndpoint']['url'] = \
        OAUTH2_SETTINGS.BASE_URL + "/authorize"
    ret['oauth2']['grantTypes']['authorization_code']['tokenEndpoint']['url'] = OAUTH2_SETTINGS.BASE_URL + "/token"
    scopes = []
    for each in OAUTH2_SETTINGS.SCOPE:
        scopes.append({"scope": each, "description": ""})
    ret['oauth2']['scopes'] = scopes
    return ret


