import os
import sys
from setuptools import setup, find_packages

sys.path.insert(0, os.path.dirname(__file__))
from django_faces import __version__ as version

setup(
    name = 'django-faces',
    version = version,
    description = '''Django application for nonintrusive avatar support.'''
                  '''It uses site's URL and user's email for autodiscovery.''',
    keywords = 'django apps avatar pavatar gravatar favicon',
    license = 'New BSD License',
    author = 'Alexander Artemenko',
    author_email = 'svetlyak.40wt@gmail.com',
    url = 'http://github.com/svetlyak40wt/django-faces/',
    install_requires = ['PIL'],
    dependency_links = ['http://pypi.aartemenko.com', 'http://dist.repoze.org'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Plugins',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages = find_packages(),
    include_package_data = True,
    zip_safe = False,
)

