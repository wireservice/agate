#!/usr/bin/env python

import csv

import agate
import proof

def load_data(data):
    text_type = agate.Text()
    number_type = agate.Number()
    boolean_type = agate.Boolean()

    columns = (
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

    with open('examples/realdata/exonerations-20150828.csv') as f:
        # Create a csv reader
        reader = csv.reader(f)

        # Skip header
        next(f)

        # Create the table
        data['exonerations'] = agate.Table(reader, columns)

def confessions(data):
    num_false_confessions = data['exonerations'].columns['false_confession'].aggregate(agate.Count(True))

    print('False confessions: %i' % num_false_confessions)

@proof.never_cache
def median_age(data):
    with_age = data['exonerations'].where(lambda row: row['age'] is not None)

    median_age = with_age.columns['age'].aggregate(agate.Median())

    print('Median age at time of arrest: %i' % median_age)

    with_age.bins('age', 8).print_bars('bin', 'count', width=80)

def years_in_prison(data):
    data['with_years_in_prison'] = data['exonerations'].compute([
        (agate.Change('convicted', 'exonerated'), 'years_in_prison')
    ])

def youth(data):
    sorted_by_age = data['exonerations'].order_by('age')
    youngest_ten = sorted_by_age.limit(10)

    youngest_ten.print_table(max_columns=7)

def states(data):
    state_totals = data['with_years_in_prison'].group_by('state')

    medians = state_totals.aggregate([
        ('years_in_prison', agate.Median(), 'median_years_in_prison')
    ])

    sorted_medians = medians.order_by('median_years_in_prison', reverse=True)

    sorted_medians.print_table(max_rows=5)

def race_and_age(data):
    # Filters rows without age data
    only_with_age = data['with_years_in_prison'].where(
        lambda r: r['age'] is not None
    )

    # Group by race
    race_groups = only_with_age.group_by('race')

    # Sub-group by age cohorts (20s, 30s, etc.)
    race_and_age_groups = race_groups.group_by(
        lambda r: '%i0s' % (r['age'] // 10),
        key_name='age_group'
    )

    # Aggregate medians for each group
    medians = race_and_age_groups.aggregate([
        ('years_in_prison', agate.Length(), 'count'),
        ('years_in_prison', agate.Median(), 'median_years_in_prison')
    ])

    # Sort the results
    sorted_groups = medians.order_by('median_years_in_prison', reverse=True)

    # Print out the results
    sorted_groups.print_table(max_rows=10)

analysis = proof.Analysis(load_data)
analysis.then(confessions)
analysis.then(median_age)
analysis.then(youth)

years_analysis = analysis.then(years_in_prison)
years_analysis.then(states)
years_analysis.then(race_and_age)

analysis.run()
