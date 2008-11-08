from md5 import md5
import datetime
import re
import socket
import urllib
import urllib2
import urlparse
import os
import logging
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

from gallery.templatetags.gallery_tags import makeThumb

logger = logging.getLogger('avatars.models')

def log_exceptions(f):
    def _log(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception, e:
            logger.debug(e)
            raise
    return _log

default_avatar = getattr(settings, 'DEFAULT_AVATAR', None)
if default_avatar is not None:
    default_avatar = settings.MEDIA_URL + default_avatar

class CacheState(models.Model):
    hash = models.CharField( _('Hash'), max_length=32, unique = True)
    enabled = models.BooleanField(_("Pavatars enabled"), default=False)
    expire_after = models.DateTimeField(_("Cache expire date"))

    def save(self):
        if self.expire_after is None:
            self.expire_after = datetime.datetime.today() + datetime.timedelta(settings.AVATARS_CACHE_DAYS)
        return super(CacheState, self).save()

def get_self_pavatar_url():
    return urlparse.urljoin(
        settings.MEDIA_URL,
        settings.AUTHOR_AVATAR)

@log_exceptions
def get_pavatar(cache, site):
    logger.info('Getting avatar for site ' + site)
    cache.enabled = False
    cache.expire_after = datetime.datetime.today() + datetime.timedelta(settings.AVATARS_CACHE_DAYS)

    if site is None or site == '':
        cache.save()
        return

    pavatar = None

    if site.startswith('http://%s' % Site.objects.get_current().domain):
        try:
            pavatar = urllib2.urlopen(get_self_pavatar_url())
        except urllib2.URLError, e:
            logger.error(e)
            cache.save()
            return

    if pavatar is None:
        try:
            source = urllib2.urlopen(site)
        except Exception, e:
            logger.error(e)
            cache.save()
            return

        try:
            url = source.info()['X-Pavatar']
            pavatar = urllib2.urlopen(url)
        except (KeyError, urllib2.URLError):
            if source.info().subtype == 'html':
                regex = re.compile('<link rel="pavatar" href="([^"]+)" ?/?>', re.I)
                try:
                    for line in source:
                        m = regex.search(line)
                        if m != None:
                            url = m.group(1)
                            try:
                                pavatar = urllib2.urlopen(url)
                            except urllib2.URLError:
                                pass
                            break
                except socket.timeout:
                    pass

    if pavatar is None:
        protocol, host, path, _, _  = urlparse.urlsplit(site)
        if path == '':
            path = '/'
        if path[-1] != '/':
            pos = path.rfind('/')
            if pos != -1:
                path = path[:pos+1]
        url = urlparse.urlunsplit((protocol, host, path + 'pavatar.png', '', ''))
        try:
            pavatar = urllib2.urlopen(url)
        except urllib2.URLError:
            url = urlparse.urlunsplit((protocol, host, 'pavatar.png', '', ''))
            try:
                pavatar = urllib2.urlopen(url)
            except urllib2.URLError:
                pass

    if pavatar:
        path = os.path.join(settings.MEDIA_ROOT, settings.AVATARS_CACHE_DIR)
        if not os.path.exists(path):
            os.makedirs(path)
        file = open(os.path.join(path, cache.hash), 'wb')
        try:
            data = StringIO(pavatar.read())
            try:
                image = Image.open(data)
            except IOError, e:
                logger.error('IOError when getting pavatar for %s: %s' \
                        % (site, e))
                cache.save()
                return

            orig_format = image.format
            thumb, resized = makeThumb(image, (settings.AVATAR_SIZE, settings.AVATAR_SIZE))
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

def get_avatar_url(email, site):
    hash = gen_hash(email, site)
    try:
        cache = CacheState.objects.get(hash=hash)
        if cache.expire_after <= datetime.datetime.today():
            logger.debug('cache for email=%s, site=%s, hash=%s is expired' % (email, site, hash))
            get_pavatar(cache, site)

    except CacheState.DoesNotExist:
        cache = CacheState(hash=hash)
        get_pavatar(cache, site)

    if cache.enabled:
        return urlparse.urljoin(settings.MEDIA_URL, '/'.join((settings.AVATARS_CACHE_DIR, hash)))
    else:
        gravatar_options = {
                'gravatar_id': md5(
                    email.lower()).hexdigest(),
                'size': str(settings.AVATAR_SIZE)
        }
        if default_avatar is not None:
            gravatar_options['default'] = default_avatar

        return 'http://www.gravatar.com/avatar.php?%s' % \
                urllib.urlencode(gravatar_options)

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
