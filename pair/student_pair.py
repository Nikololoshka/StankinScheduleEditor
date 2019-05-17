# coding: utf-8

# imports
from xml.etree import ElementTree as Xml
from enum import Enum
from pair.title_pair import TitlePair
from pair.lecturer_pair import LecturerPair
from pair.type_pair import TypePair
from pair.subgroup_pair import SubgroupPair
from pair.classroom_pair import ClassroomPair
from pair.time_pair import TimePair
from pair.date_pair import DatePair

# debug import
import defaults


class StudentPairAttrib(Enum):
    Title = "title"
    Lecturer = "lecturer"
    Type = "type"
    Subgroup = "subgroup"
    Classroom = "classroom"
    Time = "time"
    Date = "dates"


class StudentPair:
    """ Class describing the student pair """
    def __init__(self):
        self._attributes = {
            StudentPairAttrib.Title: TitlePair(),
            StudentPairAttrib.Lecturer: LecturerPair(),
            StudentPairAttrib.Type: TypePair(),
            StudentPairAttrib.Subgroup: SubgroupPair(),
            StudentPairAttrib.Classroom: ClassroomPair(),
            StudentPairAttrib.Time: TimePair(),
            StudentPairAttrib.Date: DatePair()
        }

    @staticmethod
    def from_xml(file: Xml.Element):
        pair = StudentPair()
        pair.load(file)
        return pair

    def load(self, el: Xml.Element):
        """ Load Pair from XML file. Returns Pair """
        self._attributes = {
            StudentPairAttrib.Title: TitlePair.from_xml_pair(el),
            StudentPairAttrib.Lecturer: LecturerPair.from_xml_pair(el),
            StudentPairAttrib.Type: TypePair.from_xml_pair(el),
            StudentPairAttrib.Subgroup: SubgroupPair.from_xml_pair(el),
            StudentPairAttrib.Classroom: ClassroomPair.from_xml_pair(el),
            StudentPairAttrib.Time: TimePair.from_xml_pair(el),
            StudentPairAttrib.Date: DatePair.from_xml_pair(el)
        }
        return self

    def save(self):
        """ Save Pair to XML file """
        element = Xml.Element("pair")
        for attrib in StudentPairAttrib:
            if self._attributes[attrib] is not None:
                element.append(self._attributes[attrib].save())

        return element

    def get_number(self) -> int:
        """ Returns the number of the pair in order """
        return self._attributes[StudentPairAttrib.Time].get_number()

    def get_value(self, attrib: StudentPairAttrib):
        """ Returned value pair by attrib """
        return self._attributes[attrib]

    def __str__(self):
        s = ""
        for attrib in StudentPairAttrib:
            if self._attributes[attrib].is_valid() and attrib is not StudentPairAttrib.Time:
                if attrib is StudentPairAttrib.Date:
                    s += "[" + str(self._attributes[StudentPairAttrib.Date]) + "]"
                else:
                    s += str(self._attributes[attrib]) + ". "

        return s


if __name__ == '__main__':
    # tests
    tree = Xml.ElementTree(file="../examples/example.xml")
    root = tree.getroot()

    if not Xml.iselement(root):
        print("No valid root of tree")
        exit(-1)

    print("root - tag: '{}', attrib: {}".format(root.tag, root.attrib))

    for day_of_week in root:
        for pairs in day_of_week:
            sp = StudentPair().load(pairs)
            print(sp)
            print(defaults.prettify(sp.save()))
