import agate


def test_full_outer_join_does_not_reuse_incomplete_left_row_names():
    left = agate.Table([['a', 12]], ['id', 'left'],
                       [agate.Text(), agate.Number()], row_names='id')
    right = agate.Table([['a', 24], ['b', 36]], ['id', 'right'],
                        [agate.Text(), agate.Number()])
    result = left.join(right, 'id', full_outer=True)
    assert [tuple(row) for row in result.rows] == [('a', 12, 'a', 24), (None, None, 'b', 36)]
    assert result.row_names is None
    assert result.rows.keys() is None
    assert result.columns['right'].keys() is None
    assert left.row_names == ('a',)


def test_left_join_keeps_matching_left_row_names():
    left = agate.Table([['a'], ['b']], ['id'], [agate.Text()], row_names='id')
    right = agate.Table([['b', 36]], ['id', 'right'], [agate.Text(), agate.Number()])
    result = left.join(right, 'id')
    assert result.row_names == ('a', 'b')
    assert result.rows['a']['right'] is None
    assert result.rows['b']['right'] == 36
