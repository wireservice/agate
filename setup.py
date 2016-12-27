#!/usr/bin/env python

from setuptools import setup

install_requires = [
    'six>=1.6.1',
    'pytimeparse>=1.1.5',
    'parsedatetime>=2.1',
    'Babel>=2.0',
    'isodate>=0.5.4',
    'awesome-slugify>=1.6.5',
    'leather>=0.3.2'
]

setup(
    name='agate',
    version='1.5.5',
    description='A data analysis library that is optimized for humans instead of machines.',
    long_description=open('README.rst').read(),
    author='Christopher Groskopf',
    author_email='chrisgroskopf@gmail.com',
    url='http://agate.readthedocs.org/',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: IPython',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=[
        'agate',
        'agate.aggregations',
        'agate.computations',
        'agate.data_types',
        'agate.table',
        'agate.tableset'
    ],
    install_requires=install_requires
)
