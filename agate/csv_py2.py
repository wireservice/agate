#!/usr/bin/env python

"""
This module contains the Python 2 replacement for :mod:`csv`.
"""

import codecs
import csv
import warnings

import six

from agate.exceptions import FieldSizeLimitError

EIGHT_BIT_ENCODINGS = [
    'utf-8', 'u8', 'utf', 'utf8',
    'latin-1', 'iso-8859-1', 'iso8859-1', '8859', 'cp819', 'latin', 'latin1', 'l1'
]

POSSIBLE_DELIMITERS = [',', '\t', ';', ' ', ':', '|']


class UTF8Recoder(six.Iterator):
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8.
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.reader).encode('utf-8')


class UnicodeReader(object):
    """
    A CSV reader which will read rows from a file in a given encoding.
    """
    def __init__(self, f, encoding='utf-8', field_size_limit=None, line_numbers=False, header=True, **kwargs):
        self.line_numbers = line_numbers
        self.header = header

        f = UTF8Recoder(f, encoding)

        self.reader = csv.reader(f, **kwargs)

        if field_size_limit:
            csv.field_size_limit(field_size_limit)

    def next(self):
        try:
            row = next(self.reader)
        except csv.Error as e:
            # Terrible way to test for this exception, but there is no subclass
            if 'field larger than field limit' in str(e):
                raise FieldSizeLimitError(csv.field_size_limit(), self.line_num)
            else:
                raise e

        if self.line_numbers:
            if self.header and self.line_num == 1:
                row.insert(0, 'line_numbers')
            else:
                row.insert(0, str(self.line_num - 1 if self.header else self.line_num))

        return [six.text_type(s, 'utf-8') for s in row]

    def __iter__(self):
        return self

    @property
    def dialect(self):
        return self.reader.dialect

    @property
    def line_num(self):
        return self.reader.line_num


class UnicodeWriter(object):
    """
    A CSV writer which will write rows to a file in the specified encoding.

    NB: Optimized so that eight-bit encodings skip re-encoding. See:
        https://github.com/wireservice/csvkit/issues/175
    """
    def __init__(self, f, encoding='utf-8', **kwargs):
        self.encoding = encoding
        self._eight_bit = (self.encoding.lower().replace('_', '-') in EIGHT_BIT_ENCODINGS)

        if self._eight_bit:
            self.writer = csv.writer(f, **kwargs)
        else:
            # Redirect output to a queue for reencoding
            self.queue = six.StringIO()
            self.writer = csv.writer(self.queue, **kwargs)
            self.stream = f
            self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        if self._eight_bit:
            self.writer.writerow([six.text_type(s if s is not None else '').encode(self.encoding) for s in row])
        else:
            self.writer.writerow([six.text_type(s if s is not None else '').encode('utf-8') for s in row])
            # Fetch UTF-8 output from the queue...
            data = self.queue.getvalue()
            data = data.decode('utf-8')
            # ...and reencode it into the target encoding
            data = self.encoder.encode(data)
            # write to the file
            self.stream.write(data)
            # empty the queue
            self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


class UnicodeDictReader(csv.DictReader):
    """
    Defer almost all implementation to :class:`csv.DictReader`, but wraps our
    unicode reader instead of :func:`csv.reader`.
    """
    def __init__(self, f, fieldnames=None, restkey=None, restval=None, *args, **kwargs):
        reader = UnicodeReader(f, *args, **kwargs)

        if 'encoding' in kwargs:
            kwargs.pop('encoding')

        csv.DictReader.__init__(self, f, fieldnames, restkey, restval, *args, **kwargs)

        self.reader = reader


class UnicodeDictWriter(csv.DictWriter):
    """
    Defer almost all implementation to :class:`csv.DictWriter`, but wraps our
    unicode writer instead of :func:`csv.writer`.
    """
    def __init__(self, f, fieldnames, restval='', extrasaction='raise', *args, **kwds):
        self.fieldnames = fieldnames
        self.restval = restval

        if extrasaction.lower() not in ('raise', 'ignore'):
            raise ValueError('extrasaction (%s) must be "raise" or "ignore"' % extrasaction)

        self.extrasaction = extrasaction

        self.writer = UnicodeWriter(f, *args, **kwds)


class Reader(UnicodeReader):
    """
    A unicode-aware CSV reader.
    """
    pass


class Writer(UnicodeWriter):
    """
    A unicode-aware CSV writer.
    """
    def __init__(self, f, encoding='utf-8', line_numbers=False, **kwargs):
        self.row_count = 0
        self.line_numbers = line_numbers

        if 'lineterminator' not in kwargs:
            kwargs['lineterminator'] = '\n'

        UnicodeWriter.__init__(self, f, encoding, **kwargs)

    def _append_line_number(self, row):
        if self.row_count == 0:
            row.insert(0, 'line_number')
        else:
            row.insert(0, self.row_count)

        self.row_count += 1

    def writerow(self, row):
        if self.line_numbers:
            row = list(row)
            self._append_line_number(row)

        # Convert embedded Mac line endings to unix style line endings so they get quoted
        row = [i.replace('\r', '\n') if isinstance(i, six.string_types) else i for i in row]

        UnicodeWriter.writerow(self, row)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


class DictReader(UnicodeDictReader):
    """
    A unicode-aware CSV DictReader.
    """
    pass


class DictWriter(UnicodeDictWriter):
    """
    A unicode-aware CSV DictWriter.
    """
    def __init__(self, f, fieldnames, encoding='utf-8', line_numbers=False, **kwargs):
        self.row_count = 0
        self.line_numbers = line_numbers

        if 'lineterminator' not in kwargs:
            kwargs['lineterminator'] = '\n'

        UnicodeDictWriter.__init__(self, f, fieldnames, encoding=encoding, **kwargs)

    def _append_line_number(self, row):
        if self.row_count == 0:
            row['line_number'] = 0
        else:
            row['line_number'] = self.row_count

        self.row_count += 1

    def writerow(self, row):
        if self.line_numbers:
            row = list(row)
            self._append_line_number(row)

        # Convert embedded Mac line endings to unix style line endings so they get quoted
        row = dict([
            (k, v.replace('\r', '\n')) if isinstance(v, basestring) else (k, v) for k, v in row.items()  # noqa: F821
        ])

        UnicodeDictWriter.writerow(self, row)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


class Sniffer(object):
    """
    A functional wrapper of ``csv.Sniffer()``.
    """
    def sniff(self, sample):
        """
        A functional version of ``csv.Sniffer().sniff``, that extends the
        list of possible delimiters to include some seen in the wild.
        """
        try:
            dialect = csv.Sniffer().sniff(sample, POSSIBLE_DELIMITERS)
        except csv.Error as e:
            warnings.warn('Error sniffing CSV dialect: %s' % e, RuntimeWarning, stacklevel=2)
            dialect = None

        return dialect


def reader(*args, **kwargs):
    """
    A replacement for Python's :func:`csv.reader` that uses
    :class:`.csv_py2.Reader`.
    """
    return Reader(*args, **kwargs)


def writer(*args, **kwargs):
    """
    A replacement for Python's :func:`csv.writer` that uses
    :class:`.csv_py2.Writer`.
    """
    return Writer(*args, **kwargs)
