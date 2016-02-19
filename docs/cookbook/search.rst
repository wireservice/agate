======
Search
======

Exact search
============

Find all individuals with the last_name "Groskopf":

.. code-block:: python

    family = table.where(lambda r: r['last_name'] == 'Groskopf')

Fuzzy search by edit distance
=============================

By leveraging an `existing Python library <https://pypi.python.org/pypi/python-Levenshtein/>`_ for computing the `Levenshtein edit distance <https://en.wikipedia.org/wiki/Levenshtein_distance>`_ it is trivially easy to implement a fuzzy string search.

For example, to find all names within 2 edits of "Groskopf":

.. code-block:: python

    from Levenshtein import distance

    fuzzy_family = table.where(lambda r: distance(r['last_name'], 'Groskopf') <= 2)

These results will now include all those "Grosskopfs" and "Groskoffs" whose mail I am always getting.

Fuzzy search by phonetic similarity
===================================

By using `Fuzzy <https://pypi.python.org/pypi/Fuzzy>`_ to calculate phonetic similarity, it is possible to implement a fuzzy phonetic search.

For example to find all rows with `first_name` phonetically similar to "Catherine":

.. code-block:: python

    import fuzzy

    dmetaphone = fuzzy.DMetaphone(4)
    phonetic_search = dmetaphone('Catherine')

    def phonetic_match(r):
        return any(x in dmetaphone(r['first_name']) for x in phonetic_search)

    phonetic_family = table.where(lambda r: phonetic_match(r))
