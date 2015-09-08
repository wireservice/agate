#!/usr/bin/env python

import agate

tester = agate.TypeTester(force={
    'fips': agate.Text()
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

totals = totals.order_by('total_cost_sum', reverse=True)

print('Five most spendy counties:')

totals.pretty_print(5)

# Get the most recent purchases
recent = table.order_by('ship_date', reverse=True)

print('Five most recent purchases:')

recent.pretty_print(5, 5)

# Calculate the standard of deviation for the total_costs
stdev = table.columns['total_cost'].aggregate(agate.StDev())

print('Standard deviation of total_cost: %.2f' % stdev)

# How many roborts were purchased?
robots = table.where(lambda r: 'ROBOT' in (r['item_name'] or [])).columns['quantity'].aggregate(agate.Sum())

print('Number of robots purchased: %i' % robots)
