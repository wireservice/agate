#!/usr/bin/env python

import agate

table = agate.Table.from_csv('examples/realdata/Datagov_FY10_EDU_recp_by_State.csv')

table.limit(10).bar_chart('State Name', 'TOTAL', 'docs/images/bar_chart.svg')
table.limit(10).column_chart('State Name', 'TOTAL', 'docs/images/column_chart.svg')

table = agate.Table.from_csv('examples/realdata/exonerations-20150828.csv')

by_year_exonerated = table.group_by('exonerated')
counts = by_year_exonerated.aggregate([
    ('count', agate.Count())
])

counts.order_by('exonerated').line_chart('exonerated', 'count', 'docs/images/line_chart.svg')
table.scatterplot('exonerated', 'age', 'docs/images/dots_chart.svg')

top_crimes = table.group_by('crime').having([
    ('count', agate.Count())
], lambda t: t['count'] > 100)

by_year = top_crimes.group_by('exonerated')

counts = by_year.aggregate([
    ('count', agate.Count())
])

by_crime = counts.group_by('crime')

by_crime.order_by('exonerated').line_chart('exonerated', 'count', 'docs/images/lattice.svg')
