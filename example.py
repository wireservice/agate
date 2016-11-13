#!/usr/bin/env python

import agate

tester = agate.TypeTester(force={
    'fips': agate.Text()
})

table = agate.Table.from_csv('examples/realdata/ks_1033_data.csv', column_types=tester)

# Question 1: What was the total cost to Kansas City area counties?

# Filter to counties containing Kansas City
kansas_city = table.where(lambda r: r['county'] in ('JACKSON', 'CLAY', 'CASS', 'PLATTE'))

# Sum total_cost of four counties
print('Total for Kansas City area: %i' % kansas_city.aggregate(agate.Sum('total_cost')))

# Question 2: Which counties spent the most?

# Group by counties
counties = table.group_by('county')

# Aggregate totals for all counties
totals = counties.aggregate([
    ('total_cost_sum', agate.Sum('total_cost'))
])

totals = totals.order_by('total_cost_sum', reverse=True)
totals.limit(20).print_bars('county', 'total_cost_sum', width=80)

print('Five most spendy counties:')

totals.print_table(5)

# Question 3: What are the most recent purchases?

recent = table.order_by('ship_date', reverse=True)

print('Five most recent purchases:')

recent.print_table(5, 5)

# Question 4: What is the standard of deviation of the cost of all purchases?

stdev = table.aggregate(agate.StDev('total_cost'))

print('Standard deviation of total_cost: %.2f' % stdev)

# Question 5: How many robots were purchased?

robots = table.where(lambda r: 'ROBOT' in (r['item_name'] or [])).aggregate(agate.Sum('quantity'))

print('Number of robots purchased: %i' % robots)
