from django.conf import settings


def media_url_processor(request):
    my_dict = {
        'media_url': settings.MEDIA_URL,
    }

    return my_dict
