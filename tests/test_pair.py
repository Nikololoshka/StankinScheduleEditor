# coding: utf-8

# imports
from unittest import TestCase
import itertools
from project.pair import DatePair, TimePair, DateItem, DateRange, \
                         FrequencyDate, InvalidDatePair


class TestPair(TestCase):
    def test_date_pair(self):
        json_date = [
            {
                "frequency": "once",
                "date": "2019.02.09"
            },
            {
                "frequency": "throughout",
                "date": "2019.02.16-2019.03.16"
            },
            {
                "frequency": "every",
                "date": "2019.03.23-2019.04.27"
            },
            {
                "frequency": "once",
                "date": "2019.05.18"
            },
            {
                "frequency": "once",
                "date": "2019.05.25"
            }
        ]

        date = DatePair()
        date.load(json_date)

        self.assertIn(DateItem("2019.03.30"), date, "Date contains test failed")

        self.assertRaises(InvalidDatePair,
                          date.add_date,
                          DateRange("2019.02.19", "2019.04.24", FrequencyDate.Every))

        self.assertRaises(InvalidDatePair,
                          date.add_date,
                          DateItem("2019.06.02"))

        correct_str = "09.02, 16.02-16.03 t.w., 23.03-27.04 e.w., 18.05, 25.05"
        for lst in itertools.permutations(json_date):
            temp_date = DatePair()
            temp_date.load(lst)

            self.assertEqual(correct_str, str(temp_date), "Date load test failed")

    def test_time_pair(self):
        json_time = {
            "start": "12:20",
            "end": "14:00"
        }

        t = TimePair()
        t.load(json_time)
        self.assertEqual(str(t.save()),
                         str(json_time),
                         "Time save/Load test failed")

