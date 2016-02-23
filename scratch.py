import agate


column_names = ['name', 'race', 'gender']
column_types = [agate.Text(), agate.Text(), agate.Text()]
rows = (
    ('joe', 'white', 'male'),
    ('jane', 'white', 'female'),
    ('josh', 'black', 'male'),
    ('jim', 'latino', 'male'),
    ('julia', 'white', 'female'),
    ('joan', 'asian', 'female'),
)
people = agate.Table(rows, column_names, column_types)

by_race = people.group_by("race").aggregate([
    ('total', agate.Length()),
])

gender_by_race = {}
for row in by_race.rows:
    race = row[0]
    gender_by_race[race] = {
        'male': len(people.where(lambda r: r['race'] == race and r['gender'] == 'male').rows),
        'female': len(people.where(lambda r: r['race'] == race and r['gender'] == 'male').rows)
    }

totals = by_race.compute([
    ('male', agate.Formula(agate.Number(), lambda r: gender_by_race[r['race']]['male'])),
    ('female', agate.Formula(agate.Number(), lambda r: gender_by_race[r['race']]['female'])),
])
totals.print_table()
