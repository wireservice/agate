#!/usr/bin/env python

import csv

import agate

text_type = agate.TextType()
number_type = agate.NumberType()
boolean_type = agate.BooleanType()

COLUMNS = (
    ('last_name', text_type),
    ('first_name', text_type),
    ('age', number_type),
    ('race', text_type),
    ('state', text_type),
    ('tags', text_type),
    ('crime', text_type),
    ('sentence', text_type),
    ('convicted', number_type),
    ('exonerated', number_type),
    ('dna', boolean_type),
    ('dna_essential', text_type),
    ('mistaken_witness', boolean_type),
    ('false_confession', boolean_type),
    ('perjury', boolean_type),
    ('false_evidence', boolean_type),
    ('official_misconduct', boolean_type),
    ('inadequate_defense', boolean_type),
)

def load_data(state):
    print 'load_data'
    with open('examples/realdata/exonerations-20150828.csv') as f:
        # Create a csv reader
        reader = csv.reader(f)

        # Skip header
        next(f)

        # Create the table
        state['exonerations'] = agate.Table(reader, COLUMNS)

def confessions(state):
    print 'confessions'
    num_false_confessions = state['exonerations'].columns['false_confession'].aggregate(agate.Count(True))

    print('False confessions: %i' % num_false_confessions)

    num_without_age = state['exonerations'].columns['age'].aggregate(agate.Count(None))
    print(num_without_age)

# with_age = exonerations.where(lambda row: row['age'] is not None)
#
# old = len(exonerations.rows)
# new = len(with_age.rows)
# print(old - new)
#
# median_age = with_age.columns['age'].aggregate(agate.Median())
# print(median_age)
#
# with_years_in_prison = exonerations.compute([
#     ('years_in_prison', agate.Change('convicted', 'exonerated'))
# ])
#
# median_years = with_years_in_prison.columns['years_in_prison'].aggregate(agate.Median())
#
# print(median_years)

# full_names = exonerations.compute([
#     ('full_name', agate.Formula(text_type, lambda row: '%(first_name)s %(last_name)s' % row))
# ])
#
# sorted_by_age = exonerations.order_by('age')
# youngest_ten = sorted_by_age.rows[:10]
#
# for row in youngest_ten:
#     print('%(first_name)s %(last_name)s (%(age)i) %(crime)s' % row)
#
# by_state = exonerations.group_by('state')
# totals = by_state.aggregate()
#
# sorted_totals = totals.order_by('count', reverse=True)
#
# for row in sorted_totals.rows[:5]:
#     print('%(group)s: %(count)i' % row)
#
# with_years_in_prison = exonerations.compute([
#     ('years_in_prison', agate.Change('convicted', 'exonerated'))
# ])
#
# state_totals = with_years_in_prison.group_by('state')
#
# medians = state_totals.aggregate([
#     ('years_in_prison', agate.Median(), 'median_years_in_prison')
# ])
#
# sorted_medians = medians.order_by('median_years_in_prison', reverse=True)
#
# for row in sorted_medians.rows[:5]:
#     print('%(group)s: %(median_years_in_prison)i' % row)


analysis = agate.Analysis(load_data)
analysis.then(confessions)

analysis.run()
