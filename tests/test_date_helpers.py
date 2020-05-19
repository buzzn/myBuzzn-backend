from datetime import datetime, date, timedelta
from util.date_helpers import calc_support_year_start, calc_term_boundaries,\
    calc_end, calc_support_year_start_datetime, calc_support_week_start,\
    calc_two_days_back
from tests.buzzn_test_case import BuzznTestCase


class DateHelpersTestCase(BuzznTestCase):
    """ Unit tests for date helper methods."""

    def test_calc_term_boundaries(self):
        """ Unit tests for function calc_term_boundaries().
        Expect begin_ongoing_term to equal the s_term_boundaries of the current support
        year at 00:00:00 UTC.
        Expect end_ongoing_term to equal today at 00:00:00 UTC.
        Expect begin_previous_term to equal the start of the previous support
        year at 00:00:00 UTC.
        Expect end_previous_term to equal the end of the previous support year
        at 00:00:00 UTC.
        """

        result = calc_term_boundaries()
        today = datetime.today()

        # Check result types
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 4)
        for timestamp in result:
            self.assertIsInstance(timestamp, int)

        # Check result values
        self.assertEqual(result[0], calc_support_year_start())
        begin_ongoing_term = datetime.fromtimestamp(result[0]/1000)

        end_ongoing_term = datetime.fromtimestamp(result[1]/1000)
        self.assertEqual(end_ongoing_term.year, today.year)
        self.assertEqual(end_ongoing_term.month, today.month)
        self.assertEqual(end_ongoing_term.day, today.day)
        for value in end_ongoing_term.hour, end_ongoing_term.minute, end_ongoing_term.second:
            self.assertEqual(value, 0)

        begin_previous_term = datetime.fromtimestamp(result[2]/1000)
        self.assertEqual(begin_previous_term.year, begin_ongoing_term.year - 1)
        self.assertEqual(begin_previous_term.month, 3)
        self.assertEqual(begin_previous_term.day, 12)
        for value in begin_previous_term.hour, begin_previous_term.minute,\
                begin_previous_term.second:
            self.assertEqual(value, 0)

        end_previous_term = datetime.fromtimestamp(result[3]/1000)
        self.assertEqual(end_previous_term.year, begin_ongoing_term.year)
        self.assertEqual(end_previous_term.month, 3)
        self.assertEqual(end_previous_term.day, 11)
        for value in end_previous_term.hour, end_previous_term.minute, end_previous_term.second:
            self.assertEqual(value, 0)

    def test_calc_end(self):
        """ Unit tests for function calc_end(). """

        result = calc_end()

        # Check return type
        self.assertIsInstance(result, int)

    def test_calc_support_year_start(self):
        """ Unit tests for function calc_support_year_start().
        Expect Mar-12 last year if today is between Jan-01 and Mar-11.
        Expect Mar-12 this year if today is after Mar-11.
        """

        result = calc_support_year_start()

        # Check result type
        self.assertIsInstance(result, int)

        # Check result values
        d = datetime.fromtimestamp(
            float(result/1000))
        self.assertEqual(d.day, 12)
        self.assertEqual(d.month, 3)
        if (datetime.utcnow().month < d.month) or (datetime.utcnow().month == d.month
                                                   and datetime.utcnow().day < d.day):
            self.assertEqual(d.year, datetime.utcnow().year - 1)
        else:
            self.assertEqual(d.year, datetime.utcnow().year)

    def test_calc_support_year_start_datetime(self):
        """ Unit tests for function calc_support_year_start_datetime().
        Expect Mar-12 last year as datetime.datetime.date object if today is
        between Jan-01 and Mar-11.
        Expect Mar-12 this year as datetime.datetime.date object if today is
        after Mar-11.
        """

        result = calc_support_year_start_datetime()

        # Check result type
        self.assertIsInstance(result, date)

        # Check result values
        self.assertEqual(result.day, 12)
        self.assertEqual(result.month, 3)

        if datetime.utcnow().month < result.month:
            self.assertEqual(result.year, datetime.utcnow().year - 1)
        elif datetime.utcnow().month == result.month and datetime.utcnow().day < result.day:
            self.assertEqual(result.year, datetime.utcnow().year - 1)
        else:
            self.assertEqual(result.year, datetime.utcnow().year)

    def test_calc_support_week_start(self):
        """ Unit tests for function calc_support_week_start().
        Expect one week back if today is before Mar-12 or after Mar-18.
        Expect start of support year, i.e. Mar-12 this year, if today is
        between Mar-11 and Mar-19.
        """

        result = calc_support_week_start()

        # Check result type
        self.assertIsInstance(result, int)

        # Check result values
        d = datetime.fromtimestamp(
            float(result/1000))
        if (datetime.utcnow().month == 3) and (11 < datetime.utcnow().day < 19):
            self.assertEqual(d.year, datetime.utcnow().year)
            self.assertEqual(d.month, 3)
            self.assertEqual(d.day, 12)
        else:
            self.assertEqual(d.date(), (datetime.utcnow() -
                                        timedelta(days=7)).date())

    def test_calc_two_days_back(self):
        """ Unit tests for function calc_two_days_back(). """

        result = calc_two_days_back()

        # Check return type
        self.assertIsInstance(result, int)
