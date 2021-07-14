===============
Release process
===============

This is the release process for agate:

#. Verify all tests pass on continuous integration.
3. Ensure any new modules have been added to setup.py's ``packages`` list.
#. Ensure any new public interfaces have been added to the documentation.
#. Ensure TableSet proxy methods have been added for new Table methods.
#. Run ``python charts.py`` to update images in the documentation.
#. Ensure ``CHANGELOG.rst`` is up to date. Add the release date and summary.
#. Create a release tag: ``git tag -a x.y.z -m "x.y.z release."``
#. Push tags upstream: ``git push --follow-tags``
#. Upload to `PyPI <https://pypi.python.org/pypi/agate>`_: ``python setup.py sdist bdist_wheel upload``.
#. Flag the release to build on `RTFD <https://readthedocs.org/dashboard/agate/versions/>`_.
#. Rev to latest version: ``docs/conf.py``, ``setup.py``, ``CHANGELOG.rst`` need updates.
#. Find/replace ``en/[old version]`` to ``en/[new version]`` in ``tutorial.ipynb``.
#. Commit revision: ``git commit -am "Update to version x.y.z for development."``.
