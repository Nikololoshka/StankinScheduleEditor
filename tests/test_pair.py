# coding: utf-8

# imports
from unittest import TestCase
from xml.etree import ElementTree as Xml
import itertools
from project.pair import StudentPair, DatePair, TimePair
# from project import defaults


class TestPair(TestCase):
    def test_student_pair(self):
        tree = Xml.ElementTree(file="./examples/example_1.xml")
        root = tree.getroot()

        if not Xml.iselement(root):
            print("No valid root of tree")
            exit(-1)

        # print("root - tag: '{}', attrib: {}".format(root.tag, root.attrib))

        for day_of_week in root:
            for pairs in day_of_week:
                StudentPair.from_xml(pairs)
                # print(sp)
                # print(defaults.prettify(sp.save()))

        self.assertTrue(True, "Student pair test failed")

    def test_classroom_pair(self):
        pass

    def test_date_pair(self):
        dates_lst = [
            "<date frequency=\"once\">2019.02.09</date>",
            "<date frequency=\"throughout\">2019.02.16-2019.03.16</date>",
            "<date frequency=\"every\">2019.03.23-2019.04.27</date>",
            "<date frequency=\"once\">2019.05.18</date>",
            "<date frequency=\"once\">2019.05.25</date>"
        ]

        elem = Xml.fromstring("<dates>" + "".join(dates_lst) + "</dates>")
        d = DatePair()
        d.load(elem)

        self.assertEqual(Xml.tostring(d.save()).decode("utf-8"),
                         "<dates>" + "".join(dates_lst) + "</dates>",
                         "Date load/save test failed")

        self.assertIn("2019.03.30", d, "Date contains test failed")

        correct_str = "09.02, 16.02-16.03 ч.н., 23.03-27.04 к.н., 18.05, 25.05"

        for lst in itertools.permutations(dates_lst):
            elem = Xml.fromstring("<dates>" + "".join(lst) + "</dates>")
            d = DatePair()
            d.load(elem)

            self.assertEqual(correct_str, str(d), "Date load test failed")

    def test_lecturer_pair(self):
        pass

    def test_subgroup_pair(self):
        pass

    def test_time_pair(self):
        example = "<time count=\"1\">" \
                  "<start>12:20</start>" \
                  "<end>14:00</end>" \
                  "</time>"

        elem = Xml.fromstring(example)

        t = TimePair()
        t.load(elem)
        self.assertEqual(Xml.tostring(t.save()).decode("utf-8"), example,
                         "Time save/Load test failed")

    def test_title_pair(self):
        pass

    def test_type_pair(self):
        pass
