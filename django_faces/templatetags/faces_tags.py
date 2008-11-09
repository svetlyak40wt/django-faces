import urlparse

from django.template import Library

from django_faces.models import get_avatar_url
from django_faces.settings import *

register = Library()

@register.simple_tag
def pavatar_html_link():
    return '<link rel="pavatar" href="%s" />' % AUTHOR_AVATAR

@register.inclusion_tag('avatars/author_block.html')
def author_block():
    return {'avatar_url': AUTHOR_AVATAR}

@register.inclusion_tag('avatars/avatar.html')
def avatar(email, site):
    url, size = get_avatar_url(email, site)
    return {
        'url': url,
        'size': size,
    }
