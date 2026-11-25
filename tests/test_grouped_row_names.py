import pytest

import agate


@pytest.mark.parametrize('key', ['region', lambda row: row['region']])
def test_grouped_rows_keep_their_own_names(key):
    table = agate.Table([['n1', 'north', 12], ['s1', 'south', 24], ['n2', 'north', 36]],
                        ['id', 'region', 'amount'],
                        [agate.Text(), agate.Text(), agate.Number()], row_names='id')
    groups = table.group_by(key)
    assert groups['north'].row_names == ('n1', 'n2')
    assert groups['south'].row_names == ('s1',)
    assert groups['north'].rows['n2']['amount'] == 36
    assert groups['south'].rows['s1']['amount'] == 24
    assert groups['south'].columns['amount']['s1'] == 24
    assert table.row_names == ('n1', 's1', 'n2')


def test_grouping_unnamed_rows_does_not_create_names():
    table = agate.Table([['north'], ['south']], ['region'], [agate.Text()])
    groups = table.group_by('region')
    assert groups['south'].row_names is None
