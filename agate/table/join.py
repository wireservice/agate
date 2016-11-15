#!/usr/bin/env python
# pylint: disable=W0212

from agate.rows import Row
from agate import utils


def join(self, right_table, left_key, right_key=None, inner=False, require_match=False, columns=None):
    """
    Create a new table by joining two table's on common values.

    This method performs the equivalent of SQL's "left outer join", combining
    columns from this table and from :code:`right_table` anywhere that the
    :code:`left_key` and :code:`right_key` are equivalent.

    Where there is no match for :code:`left_key` the left columns will
    be included with the right columns set to :code:`None` unless
    the :code:`inner` argument is specified.

    If :code:`left_key` and :code:`right_key` are column names, only
    the left columns will be included in the output table.

    Column names from the right table which also exist in this table will
    be suffixed "2" in the new table.

    :param right_table:
        The "right" table to join to.
    :param left_key:
        Either the name of a column from the this table to join on, a
        sequence of such column names, or a :class:`function` that takes a
        row and returns a value to join on.
    :param right_key:
        Either the name of a column from :code:table` to join on, a
        sequence of such column names, or a :class:`function` that takes a
        row and returns a value to join on. If :code:`None` then
        :code:`left_key` will be used for both.
    :param inner:
        Perform a SQL-style "inner join" instead of a left outer join. Rows
        which have no match for :code:`left_key` will not be included in
        the output table.
    :param require_match:
        If true, an exception will be raised if there is a left_key with no
        matching right_key.
    :param columns:
        A sequence of column names from :code:`right_table` to include in
        the final output table. Defaults to all columns not in
        :code:`right_key`.
    :returns:
        A new :class:`.Table`.
    """
    if right_key is None:
        right_key = left_key

    # Get join columns
    right_key_indices = []

    left_key_is_func = hasattr(left_key, '__call__')
    left_key_is_sequence = utils.issequence(left_key)

    # Left key is a function
    if left_key_is_func:
        left_data = [left_key(row) for row in self._rows]
    # Left key is a sequence
    elif left_key_is_sequence:
        left_columns = [self._columns[key] for key in left_key]
        left_data = zip(*[column.values() for column in left_columns])
    # Left key is a column name/index
    else:
        left_data = self._columns[left_key].values()

    right_key_is_func = hasattr(right_key, '__call__')
    right_key_is_sequence = utils.issequence(right_key)

    # Right key is a function
    if right_key_is_func:
        right_data = [right_key(row) for row in right_table._rows]
    # Right key is a sequence
    elif right_key_is_sequence:
        right_columns = [right_table._columns[key] for key in right_key]
        right_data = zip(*[column.values() for column in right_columns])
        right_key_indices = [right_table._columns._keys.index(key) for key in right_key]
    # Right key is a column name/index
    else:
        right_column = right_table._columns[right_key]
        right_data = right_column.values()
        right_key_indices = [right_table._columns._keys.index(right_key)]

    # Build names and type lists
    column_names = list(self._column_names)
    column_types = list(self._column_types)

    for i, column in enumerate(right_table._columns):
        name = column.name

        if columns is None and i in right_key_indices:
            continue

        if columns is not None and name not in columns:
            continue

        if name in self.column_names:
            column_names.append('%s2' % name)
        else:
            column_names.append(name)

        column_types.append(column.data_type)

    if columns is not None:
        right_table = right_table.select([n for n in right_table._column_names if n in columns])

    right_hash = {}

    for i, value in enumerate(right_data):
        if value not in right_hash:
            right_hash[value] = []

        right_hash[value].append(right_table._rows[i])

    # Collect new rows
    rows = []

    if self._row_names is not None:
        row_names = []
    else:
        row_names = None

    # Iterate over left column
    for left_index, left_value in enumerate(left_data):
        matching_rows = right_hash.get(left_value, None)

        if require_match and matching_rows is None:
            raise ValueError('Left key "%s" does not have a matching right key.' % left_value)

        # Rows with matches
        if matching_rows:
            for right_row in matching_rows:
                new_row = list(self._rows[left_index])

                for k, v in enumerate(right_row):
                    if columns is None and k in right_key_indices:
                        continue

                    new_row.append(v)

                rows.append(Row(new_row, column_names))

                if self._row_names is not None:
                    row_names.append(self._row_names[left_index])
        # Rows without matches
        elif not inner:
            new_row = list(self._rows[left_index])

            for k, v in enumerate(right_table._column_names):
                if columns is None and k in right_key_indices:
                    continue

                new_row.append(None)

            rows.append(Row(new_row, column_names))

            if self._row_names is not None:
                row_names.append(self._row_names[left_index])

    return self._fork(rows, column_names, column_types, row_names=row_names)
