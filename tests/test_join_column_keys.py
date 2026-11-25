import pytest

import agate


@pytest.mark.parametrize('full_outer', [False, True])
def test_joined_row_keys_match_disambiguated_column_names(full_outer):
    left = agate.Table([['a', 'left name', 'existing name2']], ['id', 'name', 'name2'],
                       [agate.Text(), agate.Text(), agate.Text()])
    right = agate.Table([['a', 'right name']], ['id', 'name'], [agate.Text(), agate.Text()])
    with pytest.warns(RuntimeWarning):
        result = left.join(right, 'id', full_outer=full_outer)
    row = result.rows[0]
    assert row['name2'] == 'existing name2'
    assert row['name2_2'] == 'right name'
    assert tuple(row.keys()) == result.column_names
    for index, name in enumerate(result.column_names):
        assert row[name] == row[index]


def test_ordinary_join_suffix_is_unchanged():
    left = agate.Table([['a', 'left']], ['id', 'name'], [agate.Text(), agate.Text()])
    right = agate.Table([['a', 'right']], ['id', 'name'], [agate.Text(), agate.Text()])
    result = left.join(right, 'id')
    assert result.column_names == ('id', 'name', 'name2')
    assert result.rows[0]['name2'] == 'right'
