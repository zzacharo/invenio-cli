# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
# Copyright (C) 2019 Northwestern University.
#
# Invenio-Cli is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module to ease the creation and management of applications."""

import os

from setuptools import find_packages, setup

readme = open('README.rst').read()
history = open('CHANGES.rst').read()

tests_require = [
    'check-manifest>=0.25',
    'coverage>=4.0',
    'isort>=4.3.3',
    'pydocstyle>=2.0.0',
    'pytest-cov>=2.5.1',
    'pytest-pep8>=1.0.6',
    'pytest-invenio>=1.0.5',
]

extras_require = {
    'docs': [
        'Sphinx>=1.5.1',
    ],
    'tests': tests_require,
}

extras_require['all'] = []
for reqs in extras_require.values():
    extras_require['all'].extend(reqs)

setup_requires = [
    'Babel>=1.3',
    'pytest-runner>=3.0.0,<5',
]

install_requires = [
    'cookiecutter>=1.7.0,<1.8.0',
    'click>=7.0,<7.1',
    'docker>=4.1.0,<4.2.0',
    'Flask-BabelEx>=0.9.3',
    'invenio-app>=1.2.0,<1.3.0',
    'invenio-base>=1.1.0,<1.2.0',
    'pipenv==2018.11.26',
    'PyYAML>=5.1.2,<5.2.0',
    'redis>=3.3.11,<3.4.0',
]

packages = find_packages()


# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join('invenio_cli', 'version.py'), 'rt') as fp:
    exec(fp.read(), g)
    version = g['__version__']

setup(
    name='invenio-cli',
    version=version,
    description=__doc__,
    long_description=readme + '\n\n' + history,
    keywords='invenio-cli',
    license='MIT',
    author='CERN',
    author_email='info@inveniosoftware.org',
    url='https://github.com/inveniosoftware/invenio-cli',
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={
        'console_scripts': [
            'invenio-cli = invenio_app.cli:cli',
        ],
        'flask.commands': [
            'init = invenio_cli.cli:init',
            'build = invenio_cli.cli:build',
            'assets = invenio_cli.cli:assets',
            'setup = invenio_cli.cli:setup',
            'server = invenio_cli.cli:server',
            'destroy = invenio_cli.cli:destroy',
            'update = invenio_cli.cli:update',
            'upgrade = invenio_cli.cli:upgrade',
            'demo = invenio_cli.cli:demo'
        ],
        'invenio_base.apps': [
            'invenio_cli = invenio_cli:InvenioCli',
        ],
        'invenio_base.blueprints': [
            'invenio_cli = invenio_cli.views:blueprint',
        ],
        'invenio_i18n.translations': [
            'messages = invenio_cli',
        ],
    },
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Development Status :: 3 - Alpha',
    ],
)
