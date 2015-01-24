try:
    from mongoengine import connect
    from django_town.core.settings import MONGODB_SETTINGS
    from django_town.mongoengine_extension.fields import *
    from django_town.mongoengine_extension.patch import *

    try:
        connect(MONGODB_SETTINGS.DATABASES['default'], username=MONGODB_SETTINGS.USERNAME,
                password=MONGODB_SETTINGS.PASSWORD,
                host=MONGODB_SETTINGS.HOST, port=int(MONGODB_SETTINGS.PORT))
    except KeyError:
        pass
    except:
        import traceback
        traceback.print_exc()
        pass
except ImportError:
    pass