import logging
import urlparse

from django.conf import settings as django_settings
from django.template import Library

from django_faces.models import get_avatar_url
from django_faces.settings import *

register = Library()

@register.simple_tag
def pavatar_html_link():
    return '<link rel="pavatar" href="%s" />' % AUTHOR_AVATAR()

@register.inclusion_tag('faces/author_block.html')
def author_block():
    return {
        'avatar_url': AUTHOR_AVATAR(),
        'author_name': AUTHOR_NAME,
        'contacts_url': CONTACTS_URL,
    }

@register.inclusion_tag('faces/avatar.html')
def avatar(email, site):
    url, size = get_avatar_url(email, site)

    return {
        'MEDIA_URL': django_settings.MEDIA_URL,
        'url': url,
        'size': size,
    }
