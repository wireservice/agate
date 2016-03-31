#!/usr/bin/env python

import io

import six

from agate import utils


@classmethod
def from_csv(cls, path, column_names=None, column_types=None, row_names=None, skip_lines=0, header=True, sniff_limit=0, encoding='utf-8', **kwargs):
    """
    Create a new table from a CSV.

    This method uses agate's builtin CSV reader, which supplies encoding
    support for both Python 2 and Python 3.

    :code:`kwargs` will be passed through to the CSV reader.

    :param path:
        Filepath or file-like object from which to read CSV data.
    :param column_names:
        See :meth:`.Table.__init__`.
    :param column_types:
        See :meth:`.Table.__init__`.
    :param row_names:
        See :meth:`.Table.__init__`.
    :param skip_lines:
        Either a single number indicating the number of lines to skip from
        the top of the file or a sequence of line indexes to skip where the
        first line is index 0.
    :param header:
        If `True`, the first row of the CSV is assumed to contains headers
        and will be skipped. If `header` and `column_names` are both
        specified then a row will be skipped, but `column_names` will be
        used.
    :param sniff_limit:
        Limit CSV dialect sniffing to the specified number of bytes. Set to
        None to sniff the entire file. Defaults to 0 or no sniffing.
    :param encoding:
        Character encoding of the CSV file. Note: if passing in a file
        handle it is assumed you have already opened it with the correct
        encoding specified.
    """
    from agate import csv
    from agate import Table

    if hasattr(path, 'read'):
        lines = path.readlines()
    else:
        with io.open(path, encoding=encoding) as f:
            lines = f.readlines()

    if utils.issequence(skip_lines):
        lines = [line for i, line in enumerate(lines) if i not in skip_lines]
        contents = ''.join(lines)
    elif isinstance(skip_lines, int):
        contents = ''.join(lines[skip_lines:])
    else:
        raise ValueError('skip_lines argument must be an int or sequence')

    if sniff_limit is None:
        kwargs['dialect'] = csv.Sniffer().sniff(contents)
    elif sniff_limit > 0:
        kwargs['dialect'] = csv.Sniffer().sniff(contents[:sniff_limit])

    if six.PY2:
        contents = contents.encode('utf-8')

    rows = list(csv.reader(six.StringIO(contents), header=header, **kwargs))

    if header:
        if column_names is None:
            column_names = rows.pop(0)
        else:
            rows.pop(0)

    return Table(rows, column_names, column_types, row_names=row_names)
