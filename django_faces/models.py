import datetime
import logging
import os
import re
import socket
import types
import urllib
import urllib2
import urlparse

from md5 import md5
from pdb import set_trace

try:
    from PIL import Image
except ImportError:
    import Image

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from django.db import models, IntegrityError
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.contrib.sites.models import Site

from utils import makeThumb
from django_faces.settings import \
    AUTHOR_AVATAR, \
    AVATAR_DISCOVERY_ORDER, \
    AVATARS_CACHE_DAYS, \
    AVATARS_CACHE_DIR, \
    AVATAR_SIZE, \
    DEFAULT_AVATAR, \
    DEFAULT_GRAVATAR, \
    DONT_FETCH_LOCAL_AVATARS


def log_exceptions(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception, e:
            logger = logging.getLogger('avatars.models')
            logger.exception('Exception during execution of %r' % func.__name__)
            raise
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
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
        try:
            if self.expire_after is None:
                self.expire_after = datetime.datetime.today() + datetime.timedelta(AVATARS_CACHE_DAYS)
            return super(CacheState, self).save()
        except IntegrityError:
            pass


def get_pavatar(site, email):
    logger = logging.getLogger('avatars.models')
    logger.info('Getting pavatar for site ' + site)
    import socket
    logger.info('Socket timeout: %r' % socket.getdefaulttimeout())
    avatar = None

    if site.startswith('http://%s' % Site.objects.get_current().domain):
        if DONT_FETCH_LOCAL_AVATARS:
            return None

        avatar_url = AUTHOR_AVATAR()
        if avatar_url:
            avatar = urllib2.urlopen(avatar_url)

    if avatar is None:
        source = urllib2.urlopen(site)

        try:
            url = source.info()['X-Pavatar']
            avatar = urllib2.urlopen(url)
        except (KeyError, urllib2.URLError):
            if source.info().subtype == 'html':
                regex = re.compile('<link rel="pavatar" href="([^"]+)" ?/?>', re.I)

                for line in source:
                    m = regex.search(line)
                    if m != None:
                        url = m.group(1)
                        try:
                            avatar = urllib2.urlopen(url)
                        except urllib2.URLError:
                            pass
                        break

    if avatar is None:
        protocol, host, path, _, _  = urlparse.urlsplit(site)
        if path == '':
            path = '/'
        if path[-1] != '/':
            pos = path.rfind('/')
            if pos != -1:
                path = path[:pos+1]
        urls_to_try = (
            urlparse.urlunsplit((protocol, host, path + 'pavatar.png', '', '')),
            urlparse.urlunsplit((protocol, host, 'pavatar.png', '', '')),
        )
        for url in urls_to_try:
            try:
                avatar = urllib2.urlopen(url)
                break
            except urllib2.URLError:
                pass
    return avatar


def get_favicon(site, email):
    logger = logging.getLogger('avatars.models')
    logger.info('Getting favicon for site ' + site)
    source = urllib2.urlopen(site)

    avatar = None

    if source.info().subtype == 'html':
        regex = re.compile('<link rel="icon" href="([^"]+)".*/?>', re.I)
        try:
            for line in source:
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
    return avatar

def get_gravatar(site, email):
    logger = logging.getLogger('avatars.models')
    logger.info('Getting gravatar for email ' + email)
    fake_url = 'http://example.com'
    gravatar_options = {
            'size': str(AVATAR_SIZE[0]),
            'default': DEFAULT_GRAVATAR or fake_url,
    }
    hash = md5(email.lower()).hexdigest()
    url = 'http://www.gravatar.com/avatar/%s?%s' % (hash, urllib.urlencode(gravatar_options))

    avatar = urllib2.urlopen(url)

    if avatar and avatar.geturl() != fake_url:
        return avatar
    return None


def get_default(site, email):
    logger = logging.getLogger('avatars.models')
    logger.info('Getting default avatar')
    avatar_url = DEFAULT_AVATAR()

    logger.debug('Default avatar url is %r' % avatar_url)
    if avatar_url:
        return urllib2.urlopen(avatar_url)
    return None


def fetch_and_save_avatar(avatar, cache):
    logger = logging.getLogger('avatars.models')
    if avatar:
        path = os.path.join(settings.MEDIA_ROOT, AVATARS_CACHE_DIR)
        if not os.path.exists(path):
            os.makedirs(path)
        file = open(os.path.join(path, cache.hash + '.png'), 'wb')
        try:
            logging.debug('retriving avatar from %r' % avatar.geturl())
            data = StringIO(avatar.read())
            try:
                image = Image.open(data)
            except IOError, e:
                logger.error('IOError when getting avatar for %s: %s' \
                        % (avatar.geturl(), e))
                cache.save()
                return

            orig_format = image.format
            thumb, cache.size = makeThumb(image, AVATAR_SIZE)
            try:
                logging.debug('original image format is %r, but I\'ll save it as PNG.' % orig_format)
                thumb.save(file, 'PNG')
            except Exception, e:
                logger.error(e)
            cache.enabled = True
        finally:
            file.close()
    cache.save()

def get_avatar(cache, site, email):
    logger = logging.getLogger('avatars.models')
    cache.enabled = False
    cache.expire_after = None

    avatar_retrivers = {
        'pavatar': get_pavatar,
        'gravatar': get_gravatar,
        'favicon': get_favicon,
        'default': get_default,
    }

    logging.debug('Using following avatar discovery order: %r' % (AVATAR_DISCOVERY_ORDER,))
    for retriver in AVATAR_DISCOVERY_ORDER:
        try:
            logger.debug('Getting avatar using %r' % retriver)
            if not callable(retriver):
                if not isinstance(retriver, types.StringTypes):
                    logger.error('bad retriver %s' % retriver)
                    continue
                retriver = avatar_retrivers.get(retriver, get_default)

            avatar = retriver(site, email)

            if avatar is not None:
                fetch_and_save_avatar(avatar, cache)
                if cache.enabled:
                    return
        except Exception:
            logger.exception('exception during avatar retriving')


def gen_hash(email, site):
    return md5(email.lower() + site.lower()).hexdigest()


def get_avatar_url(email, site):
    logger = logging.getLogger('avatars.models')
    hash = gen_hash(email, site)
    try:
        cache = CacheState.objects.get(hash=hash)
        if cache.expire_after <= datetime.datetime.today():
            logger.debug('cache for email=%s, site=%s, hash=%s is expired' % (email, site, hash))
            get_avatar(cache, site, email)

    except CacheState.DoesNotExist:
        cache = CacheState(hash=hash)
        get_avatar(cache, site, email)

    try:
        cache.save()
        if cache.enabled:
            return (urlparse.urljoin(settings.MEDIA_URL, os.path.join(AVATARS_CACHE_DIR, hash + '.png')),
                    dict(width = cache.actual_width, height = cache.actual_height))
    except Exception:
        logger.exception("can't save avatar cache")
    return (None, dict(width=0, height=0))

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
    try:
        from lfcomments.models import Comment
        dispatcher.connect(comment_postsave, signal=signals.post_save, sender=Comment)
    except Exception, e:
        logging.warning('post_save hook was disabled because of exception: %s' % e)

