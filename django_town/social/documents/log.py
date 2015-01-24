import mongoengine

from django_town.mongoengine_extension import OptionField, DynamicResourceField, ResourceIntField
from django_town.social.resources.user import UserResource
from django_town.social.resources.page import PageResource
from django_town.social.resources.oauth2 import ClientResource
from django_town.social.define.log_actions import LOG_ACTIONS


class Log(mongoengine.Document):
    _from = DynamicResourceField((UserResource(filter=('name', 'id', 'photo')),
                                  PageResource(filter=('name', 'id', 'photo'))), db_field="from")
    client = ResourceIntField(ClientResource(), default=ClientResource()(pk=1))
    action = OptionField(option=LOG_ACTIONS)
