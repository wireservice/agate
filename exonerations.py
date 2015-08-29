#!/usr/bin/env python

import csv

import agate

def load_data(data):
    text_type = agate.TextType()
    number_type = agate.NumberType()
    boolean_type = agate.BooleanType()

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

def median_age(data):
    with_age = data['exonerations'].where(lambda row: row['age'] is not None)

    median_age = with_age.columns['age'].aggregate(agate.Median())

    print('Median age at time of arrest: %i' % median_age)

def years_in_prison(data):
    data['with_years_in_prison'] = data['exonerations'].compute([
        ('years_in_prison', agate.Change('convicted', 'exonerated'))
    ])

def youth(data):
    sorted_by_age = data['exonerations'].order_by('age')
    youngest_ten = sorted_by_age.limit(10)

    print(youngest_ten.format(max_columns=7))

def states(data):
    state_totals = data['with_years_in_prison'].group_by('state')

    medians = state_totals.aggregate([
        ('years_in_prison', agate.Median(), 'median_years_in_prison')
    ])

    sorted_medians = medians.order_by('median_years_in_prison', reverse=True)

    print(sorted_medians.format(max_rows=5))


analysis = agate.Analysis(load_data)
analysis.then(confessions)
analysis.then(median_age)
analysis.then(youth)

years_analysis = analysis.then(years_in_prison)
years_analysis.then(states)

analysis.run()
