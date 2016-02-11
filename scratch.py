import six
import agate

number_type = agate.Number()
text_type = agate.Text()

column_names = ['label', 'before', 'after']
column_types = [text_type, number_type, number_type]

total = 100

rows = (
    ('one', 25, 25),
    ('two', 25, 50),
    ('three', 50, 25)
)

table2 = agate.Table(rows, column_names, column_types)
table2 = table2.compute([
    ('percent', agate.Percent('before')),
    ('percent_change', agate.PercentChange('before', 'after'))
])
table2.print_table()
