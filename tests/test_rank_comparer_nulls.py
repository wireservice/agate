import pytest

import agate


@pytest.mark.parametrize('reverse, expected', [
    (False, (4, 2, 1, 4, 2)),
    (True, (4, 1, 3, 4, 1)),
])
def test_custom_comparer_ranks_nulls_last(reverse, expected):
    table = agate.Table([[None], [2], [1], [None], [2]], ['amount'], [agate.Number()])

    def compare(left, right):
        assert left is not None and right is not None
        return (left > right) - (left < right)

    result = table.compute([('rank', agate.Rank('amount', comparer=compare, reverse=reverse))])
    assert result.columns['rank'].values() == expected


@pytest.mark.parametrize('values, expected', [([], ()), ([None, None], (1, 1))])
def test_custom_comparer_is_not_called_for_empty_or_all_null_columns(values, expected):
    table = agate.Table([[value] for value in values], ['amount'], [agate.Number()])

    def compare(left, right):
        pytest.fail('No non-null values to compare')

    result = table.compute([('rank', agate.Rank('amount', comparer=compare))])
    assert result.columns['rank'].values() == expected
