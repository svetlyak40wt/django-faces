from md5 import md5
import datetime
import re
import socket
import urllib
import urllib2
import urlparse
import os
import logging
from functools import wraps
from pdb import set_trace

import Image
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from django.db import models
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.contrib.sites.models import Site

from utils import makeThumb
from django_faces.settings import *


logger = logging.getLogger('avatars.models')

def log_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception, e:
            logger.exception('Exception during execution of %r' % func.__name__)
            raise
    return wrapper


class CacheState(models.Model):
    hash = models.CharField( _('Hash'), max_length=32, unique = True)
    enabled = models.BooleanField(_("Avatar enabled"), default=False)
    expire_after = models.DateTimeField(_("Cache expire date"))
    actual_width = models.IntegerField(_('Actual avatar\'s width'), default = 0)
    actual_height = models.IntegerField(_('Actual avatar\'s height'), default = 0)

    def _get_size(self):
        return (self.actual_width, self.actual_height)
    def _set_size(self, size):
        self.actual_width, self.actual_height = size

    size = property(_get_size, _set_size)

    def save(self):
        if self.expire_after is None:
            self.expire_after = datetime.datetime.today() + datetime.timedelta(AVATARS_CACHE_DAYS)
        return super(CacheState, self).save()

@log_exceptions
def get_pavatar(cache, site):
    logger.info('Getting avatar for site ' + site)
    avatar = None

    if site.startswith('http://%s' % Site.objects.get_current().domain):
        try:
            if DONT_FETCH_LOCAL_AVATARS:
                return None

            if AUTHOR_AVATAR:
                avatar = urllib2.urlopen(AUTHOR_AVATAR)
        except urllib2.URLError, e:
            logger.error(e)
            cache.save()
            return

    if avatar is None:
        try:
            source = urllib2.urlopen(site)
        except Exception, e:
            logger.error(e)
            cache.save()
            return

        try:
            url = source.info()['X-Pavatar']
            avatar = urllib2.urlopen(url)
        except (KeyError, urllib2.URLError):
            if source.info().subtype == 'html':
                regex = re.compile('<link rel="pavatar" href="([^"]+)" ?/?>', re.I)
                try:
                    for line in source:
                        m = regex.search(line)
                        if m != None:
                            url = m.group(1)
                            try:
                                avatar = urllib2.urlopen(url)
                            except urllib2.URLError:
                                pass
                            break
                except socket.timeout:
                    pass

    if avatar is None:
        protocol, host, path, _, _  = urlparse.urlsplit(site)
        if path == '':
            path = '/'
        if path[-1] != '/':
            pos = path.rfind('/')
            if pos != -1:
                path = path[:pos+1]
        url = urlparse.urlunsplit((protocol, host, path + 'pavatar.png', '', ''))
        try:
            avatar = urllib2.urlopen(url)
        except urllib2.URLError:
            url = urlparse.urlunsplit((protocol, host, 'pavatar.png', '', ''))
            try:
                avatar = urllib2.urlopen(url)
            except urllib2.URLError:
                pass

    fetch_and_save_avatar(avatar, cache)


@log_exceptions
def get_favicon(cache, site):
    logger.info('Getting favicon for site ' + site)
    try:
        source = urllib2.urlopen(site)
    except Exception, e:
        logger.error(e)
        cache.save()
        return

    avatar = None

    if source.info().subtype == 'html':
        regex = re.compile('<link rel="icon" href="([^"]+)".*/?>', re.I)
        try:
            for line in source:
                logging.getLogger('get_favicon').debug('searching link in line: %r' % line)
                m = regex.search(line)
                if m != None:
                    url = m.group(1)
                    if url:
                        if not url.startswith('http'):
                            url = urlparse.urljoin(site, url)

                        try:
                            avatar = urllib2.urlopen(url)
                        except urllib2.URLError:
                            pass
                        break
        except socket.timeout:
            pass

    if avatar is None:
        protocol, host, path, _, _  = urlparse.urlsplit(site)
        if path == '':
            path = '/'
        if path[-1] != '/':
            pos = path.rfind('/')
            if pos != -1:
                path = path[:pos+1]

        urls_to_try = (
                urlparse.urlunsplit((protocol, host, path + 'favicon.png', '', '')),
                urlparse.urlunsplit((protocol, host, path + 'favicon.ico', '', '')),
                urlparse.urlunsplit((protocol, host, 'favicon.png', '', '')),
                urlparse.urlunsplit((protocol, host, 'favicon.ico', '', '')),
        )
        for url in urls_to_try:
            try:
                avatar = urllib2.urlopen(url)
                break
            except urllib2.URLError:
                pass

    fetch_and_save_avatar(avatar, cache)

@log_exceptions
def fetch_and_save_avatar(avatar, cache):
    if avatar:
        path = os.path.join(settings.MEDIA_ROOT, AVATARS_CACHE_DIR)
        if not os.path.exists(path):
            os.makedirs(path)
        file = open(os.path.join(path, cache.hash), 'wb')
        try:
            data = StringIO(avatar.read())
            try:
                image = Image.open(data)
            except IOError, e:
                logger.error('IOError when getting avatar for %s: %s' \
                        % (site, e))
                cache.save()
                return

            orig_format = image.format
            thumb, cache.size = makeThumb(image, AVATAR_SIZE)
            try:
                thumb.save(file, orig_format)
            except Exception, e:
                logger.error(e)
            cache.enabled = True
        finally:
            file.close()
    cache.save()

def gen_hash(email, site):
    return md5(email.lower() + site.lower()).hexdigest()

def get_avatar(cache, site):
    cache.enabled = False
    cache.expire_after = None

    if site is None or site == '':
        cache.save()
        return

    get_pavatar(cache, site)
    if not cache.enabled:
        get_favicon(cache, site)


def get_avatar_url(email, site):
    hash = gen_hash(email, site)
    try:
        cache = CacheState.objects.get(hash=hash)
        if cache.expire_after <= datetime.datetime.today():
            logger.debug('cache for email=%s, site=%s, hash=%s is expired' % (email, site, hash))
            get_avatar(cache, site)

    except CacheState.DoesNotExist:
        cache = CacheState(hash=hash)
        get_avatar(cache, site)

    if cache.enabled:
        return (urlparse.urljoin(settings.MEDIA_URL, os.path.join(AVATARS_CACHE_DIR, hash)), (cache.actual_width, cache.actual_height))
    else:
        gravatar_options = {
                'gravatar_id': md5(
                    email.lower()).hexdigest(),
                'size': str(AVATAR_SIZE[0])
        }
        if DEFAULT_AVATAR is not None:
            gravatar_options['default'] = DEFAULT_AVATAR

        return ('http://www.gravatar.com/avatar.php?%s' % \
                urllib.urlencode(gravatar_options), AVATAR_SIZE)

def comment_postsave(sender, instance):
    hash = gen_hash(instance.author_email, instance.author_site)
    try:
        cache = CacheState.objects.get(hash=hash)
        cache.expire_after = datetime.datetime.today()
        cache.save()
    except CacheState.DoesNotExist:
        pass

if __name__ == 'avatars.models':
    from django.dispatch import dispatcher
    from django.db.models import signals
    from lfcomments.models import Comment
    dispatcher.connect(comment_postsave, signal=signals.post_save, sender=Comment)
