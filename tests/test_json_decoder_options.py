from collections import OrderedDict
from decimal import Decimal
from io import StringIO

import pytest

import agate


@pytest.mark.parametrize('newline', [False, True])
@pytest.mark.parametrize('as_file', [False, True])
def test_json_float_decoder_can_be_overridden(tmp_path, newline, as_file):
    source = '{"amount": 2.5}'
    source = source + '\n' if newline else '[' + source + ']'
    if as_file:
        path = tmp_path / 'rows.json'
        path.write_text(source, encoding='utf-8')
    else:
        path = StringIO(source)
    seen = []

    def parse_float(value):
        seen.append(value)
        return 'value:' + value

    table = agate.Table.from_json(path, newline=newline, parse_float=parse_float)
    assert seen == ['2.5']
    assert table.rows[0]['amount'] == 'value:2.5'


def test_json_object_pairs_hook_can_be_overridden():
    table = agate.Table.from_json(StringIO('[{"first": "alpha", "second": "beta"}]'),
                                  object_pairs_hook=lambda pairs: OrderedDict(reversed(pairs)))
    assert table.column_names == ('second', 'first')
    assert tuple(table.rows[0]) == ('beta', 'alpha')


def test_default_json_decoder_preserves_decimal_precision():
    table = agate.Table.from_json(StringIO('[{"amount": 0.1234567890123456789}]'))
    assert table.rows[0]['amount'] == Decimal('0.1234567890123456789')
