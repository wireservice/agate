#!/usr/bin/env python

from collections import OrderedDict
from decimal import Decimal
import json


@classmethod
def from_json(cls, path, row_names=None, key=None, newline=False, column_types=None, **kwargs):
    """
    Create a new table from a JSON file.

    Once the JSON has been deseralized, the resulting Python object is
    passed to :meth:`.Table.from_object`.

    If the file contains a top-level dictionary you may specify what
    property contains the row list using the :code:`key` parameter.

    :code:`kwargs` will be passed through to :meth:`json.load`.

    :param path:
        Filepath or file-like object from which to read JSON data.
    :param row_names:
        See the :meth:`.Table.__init__`.
    :param key:
        The key of the top-level dictionary that contains a list of row
        arrays.
    :param newline:
        If `True` then the file will be parsed as "newline-delimited JSON".
    :param column_types:
        See :meth:`.Table.__init__`.
    """
    from agate.table import Table

    if key is not None and newline:
        raise ValueError('key and newline may not be specified together.')

    if newline:
        js = []

        if hasattr(path, 'read'):
            for line in path:
                js.append(json.loads(line, object_pairs_hook=OrderedDict, parse_float=Decimal, **kwargs))
        else:
            with open(path, 'r') as f:
                for line in f:
                    js.append(json.loads(line, object_pairs_hook=OrderedDict, parse_float=Decimal, **kwargs))
    else:
        if hasattr(path, 'read'):
            js = json.load(path, object_pairs_hook=OrderedDict, parse_float=Decimal, **kwargs)
        else:
            with open(path, 'r') as f:
                js = json.load(f, object_pairs_hook=OrderedDict, parse_float=Decimal, **kwargs)

    if isinstance(js, dict):
        if not key:
            raise TypeError('When converting a JSON document with a top-level dictionary element, a key must be specified.')

        js = js[key]

    return Table.from_object(js, row_names=row_names, column_types=column_types)
