import unittest

from agate.data_types import Boolean, Date, DateTime, Number, Text, TimeDelta
from agate.type_tester import TypeTester


class TestTypeTester(unittest.TestCase):
    def setUp(self):
        self.tester = TypeTester()

    def test_empty(self):
        rows = [
            (None,),
            (None,),
            (None,),
        ]

        inferred = self.tester.run(rows, ['one'])

        # This behavior is not necessarily desirable. See https://github.com/wireservice/agate/issues/371
        self.assertIsInstance(inferred[0], Boolean)

    def test_text_type(self):
        rows = [
            ('a',),
            ('b',),
            ('',)
        ]

        inferred = self.tester.run(rows, ['one'])

        self.assertIsInstance(inferred[0], Text)

    def test_number_type(self):
        rows = [
            ('1.7',),
            ('200000000',),
            ('',)
        ]

        inferred = self.tester.run(rows, ['one'])

        self.assertIsInstance(inferred[0], Number)

    def test_number_percent(self):
        rows = [
            ('1.7%',),
            ('200000000%',),
            ('',)
        ]

        inferred = self.tester.run(rows, ['one'])

        self.assertIsInstance(inferred[0], Number)

    def test_number_currency(self):
        rows = [
            ('$1.7',),
            ('$200000000',),
            ('',)
        ]

        inferred = self.tester.run(rows, ['one'])

        self.assertIsInstance(inferred[0], Number)

    def test_number_currency_locale(self):
        rows = [
            ('£1.7',),
            ('£200000000',),
            ('',)
        ]

        inferred = self.tester.run(rows, ['one'])

        self.assertIsInstance(inferred[0], Number)

    def test_boolean_type(self):
        rows = [
            ('True',),
            ('FALSE',),
            ('',)
        ]

        inferred = self.tester.run(rows, ['one'])

        self.assertIsInstance(inferred[0], Boolean)

    def test_date_type(self):
        rows = [
            ('5/7/1984',),
            ('2/28/1997',),
            ('3/19/2020',),
            ('',)
        ]

        inferred = self.tester.run(rows, ['one'])

        self.assertIsInstance(inferred[0], Date)

    def test_date_type_iso_format(self):
        rows = [
            ('1984-05-07',),
            ('1997-02-28',),
            ('2020-03-19',),
            ('',)
        ]

        inferred = self.tester.run(rows, ['one'])

        self.assertIsInstance(inferred[0], Date)

    def test_date_time_type(self):
        rows = [
            ('5/7/84 3:44:12',),
            ('2/28/1997 3:12 AM',),
            ('3/19/20 4:40 PM',),
            ('',)
        ]

        inferred = self.tester.run(rows, ['one'])

        self.assertIsInstance(inferred[0], DateTime)

    def test_date_time_type_isoformat(self):
        rows = [
            ('1984-07-05T03:44:12',),
            ('1997-02-28T03:12:00',),
            ('2020-03-19T04:40:00',),
            ('',)
        ]

        inferred = self.tester.run(rows, ['one'])

        self.assertIsInstance(inferred[0], DateTime)

    def test_time_delta_type(self):
        rows = [
            ('1:42',),
            ('1w 27h',),
            ('',)
        ]

        inferred = self.tester.run(rows, ['one'])

        self.assertIsInstance(inferred[0], TimeDelta)

    def test_force_type(self):
        rows = [
            ('1.7',),
            ('200000000',),
            ('',)
        ]

        tester = TypeTester(force={
            'one': Text()
        })

        inferred = tester.run(rows, ['one'])

        self.assertIsInstance(inferred[0], Text)

    def test_limit(self):
        rows = [
            ('1.7',),
            ('foo',),
            ('',)
        ]

        tester = TypeTester(limit=1)
        inferred = tester.run(rows, ['one'])

        self.assertIsInstance(inferred[0], Number)

        tester = TypeTester(limit=2)
        inferred = tester.run(rows, ['one'])

        self.assertIsInstance(inferred[0], Text)

    def test_types_force_text(self):
        rows = [
            ('1.7',),
            ('200000000',),
            ('',)
        ]

        tester = TypeTester(types=[Text()])
        inferred = tester.run(rows, ['one'])

        self.assertIsInstance(inferred[0], Text)

    def test_types_no_boolean(self):
        rows = [
            ('True',),
            ('False',),
            ('False',)
        ]

        tester = TypeTester(types=[Number(), Text()])
        inferred = tester.run(rows, ['one'])

        self.assertIsInstance(inferred[0], Text)

    def test_types_number_locale(self):
        rows = [
            ('1,7',),
            ('200.000.000',),
            ('',)
        ]

        tester = TypeTester(types=[Number(locale='de_DE.UTF-8'), Text()])
        inferred = tester.run(rows, ['one'])

        self.assertIsInstance(inferred[0], Number)
        self.assertEqual(str(inferred[0].locale), 'de_DE')
