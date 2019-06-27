# coding: utf-8

# imports
from unittest import TestCase
from xml.etree import ElementTree as Xml
from project.schedule import Schedule, AlongTwoPairsException
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
            <time duration="1">
                <start>12:20</start>
                <end>14:00</end>
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
            <time duration="1">
                <start>12:20</start>
                <end>14:00</end>
            </time>
            <dates>
                <date frequency="every">2019.02.11-2019.05.20</date>
            </dates>
        </pair>
        """)

        schedule.add_pair(StudentPair.from_xml(xml_pair_1))
        self.assertRaises(AlongTwoPairsException,
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
            <time duration="1">
                <start>12:20</start>
                <end>14:00</end>
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
            <time duration="1">
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

    def test_impossible_intersect(self):
        schedule = Schedule()

        xml_pair_1 = Xml.fromstring("""
        <pair>
            <title>Test1</title>
            <lecturer>Lec1</lecturer>
            <type>Seminar</type>
            <subgroup>A</subgroup>
            <classroom>238</classroom>
            <time>
                <start>12:20</start>
                <end>15:50</end>
            </time>
            <dates>
                <date frequency="every">2019.02.04-2019.05.20</date>
            </dates>
        </pair>
        """)

        xml_pair_2 = Xml.fromstring("""
        <pair>
            <title>Test2</title>
            <lecturer>Lec2</lecturer>
            <type>Seminar</type>
            <subgroup>B</subgroup>
            <classroom>238</classroom>
            <time>
                <start>12:20</start>
                <end>15:50</end>
            </time>
            <dates>
                <date frequency="every">2019.02.11-2019.05.20</date>
            </dates>
        </pair>
        """)

        xml_pair_3 = Xml.fromstring("""
        <pair>
            <title>Test3</title>
            <lecturer>Lec3</lecturer>
            <type>Seminar</type>
            <subgroup>Common</subgroup>
            <classroom>238</classroom>
            <time>
                <start>10:20</start>
                <end>14:00</end>
            </time>
            <dates>
                <date frequency="every">2019.02.11-2019.05.20</date>
            </dates>
        </pair>
        """)

        schedule.add_pair(StudentPair.from_xml(xml_pair_1))
        schedule.add_pair(StudentPair.from_xml(xml_pair_2))
        self.assertRaises(AlongTwoPairsException,
                          schedule.add_pair,
                          StudentPair.from_xml(xml_pair_3))

    def test_load_and_add(self):
        schedule = Schedule()
        schedule.load("../examples/example_2.xml")

        xml_pair = Xml.fromstring("""
        <pair>
            <title>Test</title>
            <lecturer>Lec</lecturer>
            <type>Seminar</type>
            <subgroup>Common</subgroup>
            <classroom>238</classroom>
            <time>
                <start>8:30</start>
                <end>12:00</end>
            </time>
            <dates>
                <date frequency="every">2019.02.11-2019.05.20</date>
            </dates>
        </pair>
        """)
        schedule.add_pair(StudentPair.from_xml(xml_pair))
