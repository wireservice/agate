#!/usr/bin/env python

import io
import itertools

import six


@classmethod
def from_csv(cls, path, column_names=None, column_types=None, row_names=None, skip_lines=0, header=True, sniff_limit=0,
             encoding='utf-8', row_limit=None, **kwargs):
    """
    Create a new table from a CSV.

    This method uses agate's builtin CSV reader, which supplies encoding
    support for both Python 2 and Python 3.

    :code:`kwargs` will be passed through to the CSV reader.

    :param path:
        Filepath or file-like object from which to read CSV data. If a file-like
        object is specified, it must be seekable. If using Python 2, the file
        should be opened in binary mode (`rb`).
    :param column_names:
        See :meth:`.Table.__init__`.
    :param column_types:
        See :meth:`.Table.__init__`.
    :param row_names:
        See :meth:`.Table.__init__`.
    :param skip_lines:
        The number of lines to skip from the top of the file.
    :param header:
        If :code:`True`, the first row of the CSV is assumed to contain column
        names. If :code:`header` and :code:`column_names` are both specified
        then a row will be skipped, but :code:`column_names` will be used.
    :param sniff_limit:
        Limit CSV dialect sniffing to the specified number of bytes. Set to
        None to sniff the entire file. Defaults to 0 (no sniffing).
    :param encoding:
        Character encoding of the CSV file. Note: if passing in a file
        handle it is assumed you have already opened it with the correct
        encoding specified.
    :param row_limit:
        Limit how many rows of data will be read.
    """
    from agate import csv
    from agate.table import Table

    close = False

    try:
        if hasattr(path, 'read'):
            f = path
        else:
            if six.PY2:
                f = open(path, 'Urb')
            else:
                f = io.open(path, encoding=encoding)

            close = True

        if isinstance(skip_lines, int):
            while skip_lines > 0:
                f.readline()
                skip_lines -= 1
        else:
            raise ValueError('skip_lines argument must be an int')

        contents = six.StringIO(f.read())

        if sniff_limit is None:
            kwargs['dialect'] = csv.Sniffer().sniff(contents.getvalue())
        elif sniff_limit > 0:
            kwargs['dialect'] = csv.Sniffer().sniff(contents.getvalue()[:sniff_limit])

        if six.PY2:
            kwargs['encoding'] = encoding

        reader = csv.reader(contents, header=header, **kwargs)

        if header:
            if column_names is None:
                column_names = next(reader)
            else:
                next(reader)

        if row_limit is None:
            rows = tuple(reader)
        else:
            rows = tuple(itertools.islice(reader, row_limit))

    finally:
        if close:
            f.close()

    return Table(rows, column_names, column_types, row_names=row_names)
