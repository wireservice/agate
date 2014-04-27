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

# Create the table
table = Table(rows, COLUMN_TYPES, COLUMN_NAMES, cast=True)

# Remove Phillipines and Puerto Rico
states = table.where(lambda r: r['state_abbr'] not in ['PR', 'PH'])

# Sum total of all states
print 'Total of all states: %i' % states.columns['total'].sum()

# Sort state total, descending
sort_by_total_desc = states.sort_by('total', reverse=True)

# Grab just the top 5 states
top_five = sort_by_total_desc.rows[0:5]

for i, row in enumerate(top_five):
    print '# %i: %s %i' % (i, row['state'], row['total'])

with open('sorted.csv', 'w') as f:
    writer = csv.writer(f)

    writer.writerow(sort_by_total_desc.get_column_names())
    writer.writerows(sort_by_total_desc.get_data())

# Grab just the bottom state
last_place = sort_by_total_desc.rows[-1]

print 'Lowest state: %(state)s %(total)i' %(last_place)

# Calculate the standard of deviation for the state totals
stdev = states.columns['total'].stdev()

print 'Standard deviation of totals: %.2f' % stdev
