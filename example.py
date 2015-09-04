#!/usr/bin/env python

import csv

from agate import Table, DateType, NumberType, TextType, Sum, StDev

text_type = TextType()
number_type = NumberType()
date_type = DateType()

COLUMNS = (
    ('state', text_type),
    ('county', text_type),
    ('fips', text_type),
    ('nsn', text_type),
    ('item_name', text_type),
    ('quantity', number_type),
    ('ui', text_type),
    ('acquisition_cost', number_type),
    ('total_cost', number_type),
    ('ship_date', date_type),
    ('federal_supply_category', text_type),
    ('federal_supply_category_name', text_type),
    ('federal_supply_class', text_type),
    ('federal_supply_class_name', text_type),
)

with open('examples/realdata/ks_1033_data.csv') as f:
    # Create a csv reader
    reader = csv.reader(f)

    # Skip header
    next(f)

    # Create the table
    table = Table(reader, COLUMNS)

# Filter to counties containing Kansas City
kansas_city = table.where(lambda r: r['county'] in ('JACKSON', 'CLAY', 'CASS', 'PLATTE'))

# Sum total_cost of four counties
print('Total for Kansas City area: %i' % kansas_city.columns['total_cost'].aggregate(Sum()))

# Group by county
counties = table.group_by('county')

# Aggregate totals for all counties
totals = counties.aggregate([
    ('total_cost', Sum(), 'total_cost_sum')
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
stdev = table.columns['total_cost'].aggregate(StDev())

print('Standard deviation of total_cost: %.2f' % stdev)

# How many roborts were purchased?
robots = table.where(lambda r: 'ROBOT' in (r['item_name'] or [])).columns['quantity'].aggregate(Sum())

print('Number of robots purchased: %i' % robots)
