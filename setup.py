# encoding: utf-8

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import re
import sys

common_requires = [
    'jmespath',
    'docopt',
    'requests',
    'aliyun-python-sdk-core',
    'aliyun-python-sdk-sts',
]

if sys.version_info[:2] == (2, 6):
    common_requires += ['ordereddict']

requirements_py3 = common_requires + [
    'aliyun-log-python-sdk>=0.8.11,<0.10.0',
]

requirements_py2 = common_requires + [
    'aliyun-log-python-sdk>=0.9.9,<0.10.0',
]

if sys.version_info[0] == 2:
    requirements = requirements_py2
elif sys.version_info[0] == 3:
    requirements = requirements_py3

packages = [
    'aliyunlogcli'
]

version = '0.1'
with open('aliyunlogcli/version.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

classifiers = [
    'Development Status :: 4 - Beta',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: Implementation :: PyPy'
]

long_description = """
Command Line Interface for Aliyun Log Service 
http://aliyun-log-cli.readthedocs.io
"""

setup(
    name='aliyun-log-cli',
    version=version,
    description='Aliyun log service CLI',
    author='Aliyun',
    url='https://github.com/aliyun/aliyun-log-cli',
    install_requires=requirements,
    packages=packages,
    classifiers=classifiers,
    long_description=long_description,
    entry_points={
        'console_scripts': [
            'aliyunlog=aliyunlogcli.cli:main'
        ],
    }
)
