# coding: utf-8

# imports
from unittest import TestCase
from xml.etree import ElementTree as Xml
from project.schedule import Schedule, ScheduleException
from project.pair import StudentPair


class TestSchedule(TestCase):
    def test_impossible_pairs(self):
        schedule = Schedule()

        xml_pair_1 = Xml.fromstring("""
        <pair>
            <title>Иностранный язык</title>
            <lecturer>Стихова Ольга Владимировна</lecturer>
            <type>Seminar</type>
            <subgroup>Common</subgroup>
            <classroom>238</classroom>
            <time count="1">
                <start>12:20</start>
                <end>14:10</end>
            </time>
            <dates>
                <date frequency="every">2019.02.04-2019.05.20</date>
            </dates>
        </pair>
        """)

        xml_pair_2 = Xml.fromstring("""
        <pair>
            <title>Прикладная физическая культура</title>
            <lecturer>Волков Владимир Андреевич</lecturer>
            <type>Seminar</type>
            <subgroup>Common</subgroup>
            <classroom>С/3 СТАНКИН</classroom>
            <time count="1">
                <start>12:20</start>
                <end>14:00</end>
            </time>
            <dates>
                <date frequency="every">2019.02.11-2019.05.20</date>
            </dates>
        </pair>
        """)

        schedule.add_pair(StudentPair.from_xml(xml_pair_1))
        self.assertRaises(ScheduleException,
                          schedule.add_pair,
                          StudentPair.from_xml(xml_pair_2))

    def test_possible_pairs(self):
        schedule = Schedule()
        xml_pair_1 = Xml.fromstring("""
        <pair>
            <title>Иностранный язык</title>
            <lecturer>Стихова Ольга Владимировна</lecturer>
            <type>Seminar</type>
            <subgroup>A</subgroup>
            <classroom>238</classroom>
            <time count="1">
                <start>12:20</start>
                <end>14:10</end>
            </time>
            <dates>
                <date frequency="every">2019.02.04-2019.05.20</date>
            </dates>
        </pair>
        """)

        xml_pair_2 = Xml.fromstring("""
        <pair>
            <title>Прикладная физическая культура</title>
            <lecturer>Волков Владимир Андреевич</lecturer>
            <type>Seminar</type>
            <subgroup>B</subgroup>
            <classroom>С/3 СТАНКИН</classroom>
            <time count="1">
                <start>12:20</start>
                <end>14:00</end>
            </time>
            <dates>
                <date frequency="every">2019.02.11-2019.05.20</date>
            </dates>
        </pair>
        """)

        schedule.add_pair(StudentPair.from_xml(xml_pair_1))
        schedule.add_pair(StudentPair.from_xml(xml_pair_2))
