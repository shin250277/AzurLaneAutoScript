"""Exercise OCR must not consume the hour's leading zero as a day digit."""
from datetime import timedelta
from unittest import TestCase

from dev_tools.test_os_task_stop_boundaries import method


class ExerciseDatedDurationTest(TestCase):
    def parse(self, value):
        return method('module/exercise/exercise.py', 'DatedDuration', 'parse_time',
                      timedelta=timedelta).__func__(value)

    def test_missing_day_separator_keeps_two_digit_hour(self):
        self.assertEqual(self.parse('808:37:44'), timedelta(days=8, hours=8, minutes=37, seconds=44))
        self.assertEqual(self.parse('1001:30:30'), timedelta(days=10, hours=1, minutes=30, seconds=30))

    def test_explicit_day_separator(self):
        for value in ('8d08:37:44', '8日08:37:44', '8일08:37:44', '8d8:37:44'):
            self.assertEqual(self.parse(value), timedelta(days=8, hours=8, minutes=37, seconds=44))

    def test_no_colons_and_invalid_input(self):
        self.assertEqual(self.parse('8083744'), timedelta(days=8, hours=8, minutes=37, seconds=44))
        self.assertEqual(self.parse(''), timedelta())
