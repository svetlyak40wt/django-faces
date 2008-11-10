from setuptools import setup, find_packages
setup(
    name = 'django-faces',
    version = '0.1.1',
    description = '''Django application for nonintrusive avatar support.'''
                  '''It uses site's URL and user's email for autodiscovery.''',
    keywords = 'django apps avatar pavatar gravatar favicon',
    license = 'New BSD License',
    author = 'Alexander Artemenko',
    author_email = 'svetlyak.40wt@gmail.com',
    url = 'http://github.com/svetlyak40wt/django-faces/',
    install_requires = ['PIL', 'Django>=1.0'],
    dependency_links = ['http://aartemenko.com/media/packages.html'],
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
)

