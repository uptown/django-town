from django.utils import six

if six.PY2:
    import urlparse
    from urllib import urlencode, quote_plus, quote
    from urllib2 import urlopen, Request, HTTPError
else:
    from urllib import parse as urlparse
    from urllib.parse import urlencode, quote_plus, quote
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError