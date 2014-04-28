This is the release process for journalism:

#. Verify all unit tests pass.
#. Make sure the example script still works.
#. Ensure CHANGELOG is up to date.
#. Create a release tag: `git tag - x.y.z -m "x.y.z release."
#. Push tags upstream: `git push --tags`
#. Upload to [PyPI](https://pypi.python.org/pypi/journalism).
#. Flag the release to build on [RTFD](https://readthedocs.org/dashboard/journalism/versions/).
#. Update the "default version" on [RTFD](https://readthedocs.org/dashboard/journalism/versions/) to the latest.
#. Rev to latest version: `docs/conf.py`, `setup.py` and `CHANGELOG` need updates.
#. Commit revision: `git commit -am "Update to version x.y.z for development."`.
