#!/usr/bin/env python

import csv

import agate

tester = agate.TypeTester(force={
    'fips': agate.TextType()
})

table = agate.Table.from_csv('examples/realdata/ks_1033_data.csv', tester)

# Filter to counties containing Kansas City
kansas_city = table.where(lambda r: r['county'] in ('JACKSON', 'CLAY', 'CASS', 'PLATTE'))

# Sum total_cost of four counties
print('Total for Kansas City area: %i' % kansas_city.columns['total_cost'].aggregate(agate.Sum()))

# Group by county
counties = table.group_by('county')

# Aggregate totals for all counties
totals = counties.aggregate([
    ('total_cost', agate.Sum(), 'total_cost_sum')
])

totals = totals.order_by('total_cost_sum', reverse=True).rows[:5]

print('Five most spendy counties:')

for i, row in enumerate(totals):
    text = '# {}: {}, ${:,}'.format(i + 1, row['county'], row['total_cost_sum'])
    print(text)

# Get the five most recent purchases
recent_five = table.order_by('ship_date', reverse=True).rows[:5]

print('Five most recent purchases:')

for row in recent_five:
    text = '{}: {} {}, ${:,}'.format(row['ship_date'], row['quantity'], row['item_name'], row['total_cost'])
    print(text)

# Calculate the standard of deviation for the total_costs
stdev = table.columns['total_cost'].aggregate(agate.StDev())

print('Standard deviation of total_cost: %.2f' % stdev)

# How many roborts were purchased?
robots = table.where(lambda r: 'ROBOT' in (r['item_name'] or [])).columns['quantity'].aggregate(agate.Sum())

print('Number of robots purchased: %i' % robots)
