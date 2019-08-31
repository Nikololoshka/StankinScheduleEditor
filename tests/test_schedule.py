# coding: utf-8

# imports
from unittest import TestCase
from project.schedule import Schedule, AlongTwoPairsException
from project.pair import StudentPair

import json


class TestSchedule(TestCase):
    def test_impossible_pairs(self):
        schedule = Schedule()

        with open("res/test_pair_1.json", "r", encoding="utf-8") as file:
            json_pair_1 = json.load(file)

        with open("res/test_pair_2.json", "r", encoding="utf-8") as file:
            json_pair_2 = json.load(file)

        schedule.add_pair(StudentPair.from_json(json_pair_1))

        self.assertRaises(AlongTwoPairsException,
                          schedule.add_pair,
                          StudentPair.from_json(json_pair_2))

    def test_possible_pairs(self):
        schedule = Schedule()

        with open("res/test_pair_2.json", "r", encoding="utf-8") as file:
            json_pair_2 = json.load(file)

        with open("res/test_pair_3.json", "r", encoding="utf-8") as file:
            json_pair_3 = json.load(file)

        schedule.add_pair(StudentPair.from_json(json_pair_2))
        schedule.add_pair(StudentPair.from_json(json_pair_3))

    def test_impossible_intersect(self):
        schedule = Schedule()

        with open("res/test_pair_4.json", "r", encoding="utf-8") as file:
            json_pair_4 = json.load(file)

        with open("res/test_pair_5.json", "r", encoding="utf-8") as file:
            json_pair_5 = json.load(file)

        with open("res/test_pair_6.json", "r", encoding="utf-8") as file:
            json_pair_6 = json.load(file)

        schedule.add_pair(StudentPair.from_json(json_pair_4))
        schedule.add_pair(StudentPair.from_json(json_pair_5))

        self.assertRaises(AlongTwoPairsException,
                          schedule.add_pair,
                          StudentPair.from_json(json_pair_6))
