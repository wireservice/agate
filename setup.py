from setuptools import find_packages, setup

with open('README.rst') as f:
    long_description = f.read()

setup(
    name='agate',
    version='1.6.3',
    description='A data analysis library that is optimized for humans instead of machines.',
    long_description=long_description,
    long_description_content_type='text/x-rst',
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
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=find_packages(exclude=['benchmarks', 'tests', 'tests.*']),
    install_requires=[
        'Babel>=2.0',
        'isodate>=0.5.4',
        'leather>=0.3.2',
        # KeyError: 's' https://github.com/bear/parsedatetime/pull/233 https://github.com/wireservice/agate/issues/743
        # AttributeError: 'module' object has no attribute 'Locale' https://github.com/bear/parsedatetime/pull/247
        'parsedatetime>=2.1,!=2.5,!=2.6',
        'python-slugify>=1.2.1',
        'pytimeparse>=1.1.5',
        'six>=1.9.0',
    ],
    extras_require={
        'test': [
            'coverage>=3.7.1',
            'cssselect>=0.9.1',
            'lxml>=3.6.0',
            'nose>=1.1.2',
            # CI is not configured to install PyICU on macOS and Windows.
            'PyICU>=2.4.2;sys_platform=="linux"',
            'pytz>=2015.4',
            'mock>=1.3.0;python_version<"3"',
            'unittest2>=1.1.0;python_version<"3"',
        ],
        'docs': [
            'Sphinx>=1.2.2',
            'sphinx_rtd_theme>=0.1.6',
        ],
    }
)
