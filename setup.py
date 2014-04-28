#!/usr/bin/env python

from setuptools import setup
import sys

install_requires = [
    'six==1.6.1' 
]

if sys.version_info == (2, 6):
    install_requires.append('ordereddict>=1.1')

setup(
    name='journalism',
    version='0.2.0',
    description='',
    long_description=open('README').read(),
    author='Christopher Groskopf',
    author_email='staringmonkey@gmail.com',
    url='journalism takes the horror out of basic data analysis and manipulation.',
    license='MIT',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=[
        'journalism',
    ],
    install_requires=install_requires
)
