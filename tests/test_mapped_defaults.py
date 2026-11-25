import pytest

import agate


@pytest.mark.parametrize('default', [0, False, '', [], {}, ()])
def test_named_data_lookup_preserves_explicit_default(default):
    table = agate.Table([['north', 12], ['south', 24]], ['region', 'amount'],
                        [agate.Text(), agate.Number()], row_names='region')
    assert table.rows[0].get('absent', default) is default
    assert table.columns['amount'].get('absent', default) is default
    assert table.rows[0].get('amount', default) == 12
    assert table.columns['amount'].get('south', default) == 24


def test_lookup_without_default_remains_none():
    row = agate.Table([['north']], ['region'], [agate.Text()]).rows[0]
    assert row.get('absent') is None
