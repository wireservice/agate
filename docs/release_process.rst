===============
Release process
===============

If substantial changes were made to the code:

#. Ensure any new modules have been added to setup.py's ``packages`` list
#. Ensure any new public interfaces have been added to the documentation
#. Ensure TableSet proxy methods have been added for new Table methods

Then:

#. All tests pass on continuous integration
#. The changelog is up-to-date and dated
#. The version number is correct in:

   -  setup.py
   -  docs/conf.py

#. Check for new authors:

   .. code-block:: bash

      git log --perl-regexp --author='^((?!James McKinney).*)$'

#. Update images in the documentation:

   .. code-block:: bash

      python charts.py

#. Tag the release:

   .. code-block:: bash

      git tag -a x.y.z -m 'x.y.z release.'
      git push --follow-tags
