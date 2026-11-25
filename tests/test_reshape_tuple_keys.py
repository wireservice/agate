import pytest

import agate


@pytest.fixture
def table():
    return agate.Table([['alpha', 'north', 12, 8], ['beta', 'south', 24, 16]],
                       ['id', 'region', 'sales', 'cost'],
                       [agate.Text(), agate.Text(), agate.Number(), agate.Number()])


@pytest.mark.parametrize('keys', [('id',), ('id', 'region')])
def test_normalize_accepts_tuple_key_names(table, keys):
    expected = table.normalize(list(keys), ['sales', 'cost'])
    actual = table.normalize(keys, ('sales', 'cost'))
    assert actual.column_names == expected.column_names
    assert actual.rows == expected.rows
    assert len(actual.rows) == 4


@pytest.mark.parametrize('keys', [('id',), ('id', 'region')])
def test_denormalize_accepts_tuple_key_names(table, keys):
    normalized = table.normalize(list(keys), ['sales', 'cost'])
    expected = normalized.denormalize(list(keys))
    actual = normalized.denormalize(keys)
    assert actual.column_names == expected.column_names
    assert actual.rows == expected.rows
    assert actual.row_names == expected.row_names
