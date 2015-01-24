from django_town.utils.common import *
from django_town.utils.rand import *
from django_town.utils.crypto import *
from django_town.utils.plural import pluralize
from django_town.utils.with3 import *


try:
    import ujson as json

except ImportError:
    import json as json

