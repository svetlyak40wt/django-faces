import urlparse

from django.conf import settings
from django.contrib.sites.models import Site

def _get_url(settings_name):
    def _getter():
        url = getattr(settings, settings_name, None)
        if url is None or url.startswith('http'):
            return url

        media_url = settings.MEDIA_URL
        if not media_url.startswith('http'):
            media_url = urlparse.urljoin('http://' + Site.objects.get_current().domain, media_url)
        return urlparse.urljoin(media_url, url)
    return _getter

DONT_FETCH_LOCAL_AVATARS = getattr(settings, 'DONT_FETCH_LOCAL_AVATARS', False)
AVATARS_CACHE_DAYS = getattr(settings, 'AVATARS_CACHE_DAYS', 1)
AVATARS_CACHE_DIR = getattr(settings, 'AVATARS_CACHE_DIR', 'avatars_cache')

AVATAR_SIZE = getattr(settings, 'AVATAR_SIZE', (50, 50))
if isinstance(AVATAR_SIZE, int):
    AVATAR_SIZE = (AVATAR_SIZE, AVATAR_SIZE)

AUTHOR_AVATAR = _get_url('AUTHOR_AVATAR')
DEFAULT_AVATAR = _get_url('DEFAULT_AVATAR')
AUTHOR_NAME = getattr(settings, 'AUTHOR_NAME', None)
CONTACTS_URL = getattr(settings, 'CONTACTS_URL', None)
AVATAR_DISCOVERY_ORDER = getattr(
    settings,
    'AVATAR_DISCOVERY_ORDER',
    ('pavatar', 'gravatar', 'favicon', 'default')
)
# also, it can be 'monsterid' or 'identicon' or 'wavatar'
DEFAULT_GRAVATAR = getattr(settings, 'DEFAULT_GRAVATAR', None)
