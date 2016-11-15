===============
Release process
===============

This is the release process for agate:

1. Verify all unit tests pass with fresh environments: ``tox -r``.
2. Verify 100% test coverage: ``nosetests --with-coverage tests``.
3. Ensure any new modules have been added to setup.py's ``packages`` list.
#. Ensure any new public interfaces have been added to the documentation.
#. Ensure TableSet proxy methods have been added for new Table methods.
#. Make sure the example script still works: ``python example.py``.
#. Ensure ``python charts.py`` works and has been run recently.
#. Ensure ``CHANGELOG.rst`` is up to date. Add the release date and summary.
#. Create a release tag: ``git tag -a x.y.z -m "x.y.z release."``
#. Push tags upstream: ``git push --tags``
#. If this is a major release, merge ``master`` into ``stable``: ``git checkout stable; git merge master; git push``
#. Upload to `PyPI <https://pypi.python.org/pypi/agate>`_: ``python setup.py sdist bdist_wheel upload``.
#. Flag the release to build on `RTFD <https://readthedocs.org/dashboard/agate/versions/>`_.
#. Update the "default version" on `RTFD <https://readthedocs.org/dashboard/agate/versions/>`_ to the latest.
#. Rev to latest version: ``docs/conf.py``, ``docs/tutorial.rst``, ``setup.py``, ``CHANGELOG.rst`` need updates.
#. Find/replace ``en/[old version]`` to ``en/[new version]`` in ``tutorial.ipynb``.
#. Commit revision: ``git commit -am "Update to version x.y.z for development."``.
