Introduction
============

This is the django application for nonintrusive avatar support.
It uses site's URL and user's email for autodiscovery.

In opposite to django-avatar_, this application does not allow
users to upload their own pictures to the servers. Instead of this,
django-faces tries to discover user's avatar using his site's URL or
his email.


Right now, django-faces can use `Pavatar protocol`_ to
show avatar for web site, or fall back to the Favicon_ or Gravatar_, which need a commenter's email.

If niether Pavatar, Favicon or Gravatar are not enabled for 'email'
and 'site', then algorithm fall back to the default avatar image,
which you can specify using ``DEFAULT_AVATAR`` option in the settings.py.

All pavatars are cached during specified time period. Gravatars' caching
is not realized yet.

Dependencies
------------

This application depends on PIL -- Python Image Library and PIL must be build with JPEG and
PNG (zlib) support.

On debian like systems, you need to install ``python-imaging`` package, or install development
packages ``libjpeg-dev`` and ``zlib1g-dev`` (or something like that) if you wish to build
PIL egg from the sources.


Installation
------------

* Add application ``django_faces`` to the ``INSTALLED_APPS`` list.
* Run ``./manage.py syncdb`` to create all neccessary tables.
* Add these variables to the settings.py::

        AUTHOR_AVATAR = 'images/author.jpg'          # site author's avatar
        DEFAULT_AVATAR = 'images/default_avatar.jpg' # default avatar image
                                                     # it can be relative to MEDIA_URL
                                                     # or absolute URL
        AVATARS_CACHE_DIR = 'cache/avatars'          # cache directory
        AVATARS_CACHE_DAYS = 1                       # how many days before
                                                     # another avatar check
        AVATAR_SIZE = 50                             # avatar's size in pixels,
                                                     # all images are resized to this size.
        AVATAR_DISCOVERY_ORDER = \
        ('pavatar', 'gravatar', 'favicon', 'default')
        DEFAULT_GRAVATAR = None                      # also, it can be 'monsterid' or 'identicon' or 'wavatar'

* Append ``django_faces.middleware.XPavatar`` line to the ``MIDDLEWARE_CLASSES`` to add X-Pavatar
  HTTP header or or use ``{% pavatar_html_link %}`` to your main template to add ``link`` HTML element.

Template tags
-------------

First os all, make tags import like this ``{% load faces_tags %}``. After that, you can use these
tags in you template.

pavatar_html_link
^^^^^^^^^^^^^^^^^

``{% pavatar_html_link %}`` can be used instead of middleware to generate 'link' HTML element
for pavatar.

author_block
^^^^^^^^^^^^

This template tag can be used, to generate a simple HTML block with site's author's avatar.
It is called without any parameters:

    {% load faces_tags %}
    {% author_block %}

You can overload ``faces/author_block.html`` template, to modify look and feel of this block.
This template's context contains following variables: ``avatar_url``, ``author_name`` and ``contacts_url``.

avatar
^^^^^^

Use template tag ``{% avatar email site %}`` to create simple block with ``<img src="" />``
for the email's and site's owner.

For example, I use following code, to show avatars on my site, which uses threaded comments and
django-openid::

    {% load faces_tags %}
    <div class="b-avatar">
        {% avatar comment.user.email comment.user.openids.get.openid %}
    </div>

Very simple, is't it?

To change avatar discovery order, set variable `AVATAR_DISCOVERY_ORDER` in your settings.py.
By default it is a tuple ('pavatar', 'gravatar', 'favicon', 'default'), but you can use
not only string identifiers, but also callables. Your custom function must accept `site`
and `email` keyword arguments and return result of the call to `urllib2.urlopen` or a
file-like object but with method geturl.

.. _django-avatar: http://code.google.com/p/django-avatar/
.. _pavatar protocol:  http://pavatar.com/spec/
.. _gravatar: http://gravatar.com/
.. _favicon: http://en.wikipedia.org/wiki/Favicon



.. image:: https://d2weczhvl823v0.cloudfront.net/svetlyak40wt/django-faces/trend.png
   :alt: Bitdeli badge
   :target: https://bitdeli.com/free

