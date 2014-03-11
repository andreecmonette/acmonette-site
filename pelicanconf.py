#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Andree Monette'
SITENAME = u'Andree Monette'
SITEURL = 'http://andreecmonette.github.io'

SITESUBTITLE = 'Thoughts, in stereo.'
SITETAG = "and cat mon"

STYLESHEETS = ("pygment.css", "voidybootstrap.css",)

CUSTOM_ARTICLE_SHARING = "sharing.html"
CUSTOM_ARTICLE_SCRIPTS = "sharing_scripts.html"

TIMEZONE = 'America/Toronto'

DEFAULT_LANG = u'en'

STATIC_PATHS = (['CNAME','images'])


# Feed generation is usually not desired when developing
FEED_DOMAIN = SITEURL
FEED_ALL_ATOM = 'feeds/all.atom.xml'
CATEGORY_FEED_ATOM = 'feeds/%s.atom.xml'
TRANSLATION_FEED_ATOM = None
TAG_FEED_ATOM = 'feeds/tags/%s.atom.xml'

# Blogroll
LINKS =  (('Pelican', 'http://getpelican.com/'),
          ('Python.org', 'http://python.org/'),
          ('Jinja2', 'http://jinja.pocoo.org/'),
          ('You can modify those links in your config file', '#'),)

# Social widget
SOCIAL = (('Twitter', 'http://twitter.com/andreemonette','fa fa-twitter-square fa-fw fa-lg'),
    ('GitHub', 'http://github.com/andreecmonette','fa fa-github-square fa-fw fa-lg'),)

DEFAULT_PAGINATION = 10

THEME = "pelican-themes/voidy-bootstrap"

# Uncomment following line if you want document-relative URLs when developing
RELATIVE_URLS = True
