import urlparse

from django.conf import settings
from django.template import Library

from avatars.models import get_avatar_url, get_self_pavatar_url

register = Library()

author_avatar = get_self_pavatar_url()

@register.simple_tag
def pavatar_html_link():
    return '<link rel="pavatar" href="%s" />' % author_avatar

@register.inclusion_tag('avatars/author_block.html')
def author_block():
    return {'avatar_url': author_avatar}

@register.inclusion_tag('avatars/avatar.html')
def avatar(email, site):
    return {
        'url': get_avatar_url(email, site),
        'size': settings.AVATAR_SIZE,
    }
