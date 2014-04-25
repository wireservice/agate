#!/usr/bin/env python

import csv

from journalism import Table, TextColumn, IntColumn

COLUMNS = [
    ('state', TextColumn),
    ('state_abbr', TextColumn),
    ('9_11_gi_bill1', IntColumn),
    ('montogomery_gi_bill_active', IntColumn),
    ('montgomery_gi_bill_reserve', IntColumn),
    ('dependants', IntColumn),
    ('reserve', IntColumn),
    ('vietnam', IntColumn),
    ('total', IntColumn)
]

COLUMN_NAMES = [c[0] for c in COLUMNS]
COLUMN_TYPES = [c[1] for c in COLUMNS]

with open('examples/realdata/Datagov_FY10_EDU_recp_by_State.csv') as f:
    # Skip headers
    f.next()
    f.next()
    f.next()

    rows = list(csv.reader(f))

# Trim cruft off end
rows = rows[:-2]

table = Table(rows, COLUMN_TYPES, COLUMN_NAMES, cast=True)

print 'Total of all states: %i' % table.columns['total'].sum()

sort_by_total_desc = table.sort_by('total', reverse=True)
first_place = sort_by_total_desc.rows[0]

print 'Highest state: %(state)s %(total)i' % (first_place)

last_place = sort_by_total_desc.rows[-1]

print 'Lowest state: %(state)s %(total)i' %(last_place)

stdev = table.columns['total'].stdev()

print 'Standard deviation of totals: %.2f' % stdev
