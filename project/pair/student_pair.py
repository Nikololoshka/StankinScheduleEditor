# coding: utf-8

# imports
from xml.etree import ElementTree as Xml
from enum import Enum
from project.pair.title_pair import TitlePair
from project.pair.lecturer_pair import LecturerPair
from project.pair.type_pair import TypePair
from project.pair.subgroup_pair import SubgroupPair
from project.pair.classroom_pair import ClassroomPair
from project.pair.time_pair import TimePair
from project.pair.date_pair import DatePair


class StudentPairAttrib(Enum):
    """ Enum describing attributes of StudentPair """
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
        """ Load Pair from XML file. Returned StudentPair """
        pair = StudentPair()
        pair.load(file)
        return pair

    def load(self, el: Xml.Element):
        """ Load StudentPair from XML file """
        self._attributes = {
            StudentPairAttrib.Title: TitlePair.from_xml_pair(el),
            StudentPairAttrib.Lecturer: LecturerPair.from_xml_pair(el),
            StudentPairAttrib.Type: TypePair.from_xml_pair(el),
            StudentPairAttrib.Subgroup: SubgroupPair.from_xml_pair(el),
            StudentPairAttrib.Classroom: ClassroomPair.from_xml_pair(el),
            StudentPairAttrib.Time: TimePair.from_xml_pair(el),
            StudentPairAttrib.Date: DatePair.from_xml_pair(el)
        }

    def save(self):
        """ Save StudentPair to XML file """
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

    def copy(self):
        new_pair = StudentPair()
        for attrib in StudentPairAttrib:
            new_pair._attributes[attrib] = self._attributes[attrib].copy()

        return new_pair

    def __str__(self):
        s = ""
        for attrib in StudentPairAttrib:
            if self._attributes[attrib].is_valid() and attrib is not StudentPairAttrib.Time:
                if attrib is StudentPairAttrib.Date:
                    s += "[" + str(self._attributes[StudentPairAttrib.Date]) + "]"
                else:
                    s += str(self._attributes[attrib]) + ". "

        return s
