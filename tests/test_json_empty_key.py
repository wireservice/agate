from io import StringIO

import pytest

import agate


@pytest.mark.parametrize('as_file', [False, True])
def test_import_explicit_empty_top_level_key(tmp_path, as_file):
    source = '{"": [{"name": "alpha", "amount": 12}], "other": []}'
    if as_file:
        path = tmp_path / 'rows.json'
        path.write_text(source, encoding='utf-8')
    else:
        path = StringIO(source)
    table = agate.Table.from_json(path, key='')
    assert table.column_names == ('name', 'amount')
    assert tuple(table.rows[0]) == ('alpha', 12)


def test_top_level_object_still_requires_explicit_key():
    with pytest.raises(TypeError, match='a key must be specified'):
        agate.Table.from_json(StringIO('{"": []}'))
