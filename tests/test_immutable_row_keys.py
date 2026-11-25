import pytest

import agate


@pytest.mark.parametrize('populate_cache', [False, True])
def test_input_key_list_cannot_change_an_immutable_row(populate_cache):
    keys = ['first', 'second']
    row = agate.Row([12, 24], keys)
    if populate_cache:
        assert row['first'] == 12
    keys.reverse()
    keys.append('extra')
    assert row.keys() == ('first', 'second')
    assert row.items() == (('first', 12), ('second', 24))
    assert row['first'] == 12
    assert row['second'] == 24


def test_tuple_keys_can_be_reused_and_omitted_keys_stay_none():
    keys = ('first', 'second')
    assert agate.Row([12, 24], keys).keys() is keys
    assert agate.Row([12, 24]).keys() is None
