from decimal import Decimal

import pytest

import agate


@pytest.mark.parametrize('total', [12.5, Decimal('12.5')])
def test_percent_accepts_fractional_numeric_total(total):
    table = agate.Table([[Decimal('3.125')], [Decimal('9.375')]], ['amount'], [agate.Number()])
    result = table.compute([('percent', agate.Percent('amount', total=total))])
    assert result.columns['percent'].values() == (Decimal('25'), Decimal('75'))


def test_percent_integer_and_inferred_totals_are_unchanged():
    table = agate.Table([[5], [15]], ['amount'], [agate.Number()])
    for computation in (agate.Percent('amount', total=20), agate.Percent('amount')):
        assert computation.run(table) == [Decimal('25'), Decimal('75')]


@pytest.mark.parametrize('total', [0.0, -0.5])
def test_nonpositive_totals_remain_invalid(total):
    table = agate.Table([[5]], ['amount'], [agate.Number()])
    with pytest.raises(agate.DataTypeError, match='positive'):
        table.compute([('percent', agate.Percent('amount', total=total))])
