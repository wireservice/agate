#!/usr/bin/env python

import proof

import agate


def load_data(data):
    data['exonerations'] = agate.Table.from_csv('examples/realdata/exonerations-20150828.csv')

    print(data['exonerations'])


def confessions(data):
    num_false_confessions = data['exonerations'].aggregate(agate.Count('false_confession', True))

    print('False confessions: %i' % num_false_confessions)


@proof.never_cache
def median_age(data):
    median_age = data['exonerations'].aggregate(agate.Median('age'))

    print('Median age at time of arrest: %i' % median_age)

    data['exonerations'].bins('age', 10, 0, 100).print_bars('age', width=80)
    data['exonerations'].pivot('age').order_by('age').print_bars('age', width=80)

    data['exonerations'].bins('age').print_bars('age', width=80)


def years_in_prison(data):
    data['with_years_in_prison'] = data['exonerations'].compute([
        ('years_in_prison', agate.Change('convicted', 'exonerated'))
    ])


def youth(data):
    sorted_by_age = data['exonerations'].order_by('age')
    youngest_ten = sorted_by_age.limit(10)

    youngest_ten.print_table(max_columns=7)


def states(data):
    by_state = data['with_years_in_prison'].group_by('state')
    state_totals = by_state.aggregate([
        ('count', agate.Count())
    ])

    sorted_totals = state_totals.order_by('count', reverse=True)

    sorted_totals.print_table(max_rows=5)

    medians = by_state.aggregate([
        ('count', agate.Count()),
        ('median_years_in_prison', agate.Median('years_in_prison'))
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
        ('count', agate.Count()),
        ('median_years_in_prison', agate.Median('years_in_prison'))
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
