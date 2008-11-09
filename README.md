django-faces
------------

This application uses Pavatar protocol (http://pavatar.com/spec/) to
show avatar for web site, or fall back to the Favicon or Gravatar
(http://gravatar.com), which need a commenter's email.

If niether Pavatar, Favicon or Gravatar are not enabled for 'email'
and 'site', then algorithm fall back to the default avatar image,
which you can specify using `DEFAULT_AVATAR` option in the settings.py.

All pavatars are cached during specified time period. Gravatars' caching
is not realized yet.

Dependencies
============

This application depends on PIL -- Python Image Library.

Installation
============

* Add application `django_faces` to the `INSTALLED_APPS` list.
* Run `./manage.py syncdb` to create all neccessary tables.
* Add these variables to the settings.py:

    AUTHOR_AVATAR = 'images/author.jpg'          # site author's avatar
    DEFAULT_AVATAR = 'images/default_avatar.jpg' # default avatar image
    AVATARS_CACHE_DIR = 'cache/avatars'          # cache directory
    AVATARS_CACHE_DAYS = 1                       # how many days before
                                                 # another avatar check
    AVATAR_SIZE = 50                             # avatar's size in pixels,
                                                 # all images are resized to this size.
* Append `django_faces.middleware.XPavatar` line to the `MIDDLEWARE_CLASSES` to add X-Pavatar
  HTTP header or or use `{% pavatar_html_link %}` to your main template to add 'link' HTML element.

Template tags
=============

First os all, make tags import like this `{% load faces_tags %}`. After that, you can use these
tags in you template.

### pavatar_html_link ###

`{% pavatar_html_link %}` can be used instead of middleware to generate 'link' HTML element
for pavatar.

### author_block ###

This template tag can be used, to generate a simple HTML block with site's author's avatar.
It is called without any parameters:

    {% author_block %}

### avatar ###

Use template tag `{% avatar email site %}` to create simple block with `<img src="" />`
for the email's and site's owner.

For example, I use following code, to show avatars on my site, which uses threaded comments and
django-openid:

    {% load faces_tags %}
    <div class="b-avatar">
        {% avatar comment.user.email comment.user.openids.get.openid %}
    </div>

Very simple, is't it?

