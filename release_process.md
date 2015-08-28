This is the release process for agate:

#. Verify all unit tests pass with fresh environments: `tox -r`.
#. Verify 100% test coverage: `nosetests --with-coverage --cover-package=agate`.
#. Make sure the example script still works: `python example.py`.
#. Ensure CHANGELOG is up to date.
#. Create a release tag: `git tag -a x.y.z -m "x.y.z release."
#. Push tags upstream: `git push --tags`
#. Upload to [PyPI](https://pypi.python.org/pypi/agate): `python setup.py sdist bdist_wheel upload`.
#. Flag the release to build on [RTFD](https://readthedocs.org/dashboard/agate/versions/).
#. Update the "default version" on [RTFD](https://readthedocs.org/dashboard/agate/versions/) to the latest.
#. Rev to latest version: `docs/conf.py`, `setup.py` and `CHANGELOG` need updates.
#. Commit revision: `git commit -am "Update to version x.y.z for development."`.
