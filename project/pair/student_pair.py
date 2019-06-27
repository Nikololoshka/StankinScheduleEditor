# coding: utf-8

# imports
from xml.etree import ElementTree as Xml
from project.pair.title_pair import TitlePair
from project.pair.lecturer_pair import LecturerPair
from project.pair.type_pair import TypePair
from project.pair.subgroup_pair import SubgroupPair
from project.pair.classroom_pair import ClassroomPair
from project.pair.time_pair import TimePair
from project.pair.date_pair import DatePair


class StudentPair:
    """ Class describing the student pair """
    def __init__(self):
        self._attributes = {
            "title": TitlePair(),
            "lecturer": LecturerPair(),
            "type": TypePair(),
            "subgroup": SubgroupPair(),
            "classroom": ClassroomPair(),
            "time": TimePair(),
            "date": DatePair()
        }

    @staticmethod
    def from_xml(file: Xml.Element):
        """
        Load Pair from XML element. Returned StudentPair.
        """
        pair = StudentPair()
        pair.load(file)
        return pair

    def load(self, el: Xml.Element):
        """
        Load StudentPair from XML element.
        """
        self._attributes = {
            "title": TitlePair.from_xml_pair(el),
            "lecturer": LecturerPair.from_xml_pair(el),
            "type": TypePair.from_xml_pair(el),
            "subgroup": SubgroupPair.from_xml_pair(el),
            "classroom": ClassroomPair.from_xml_pair(el),
            "time": TimePair.from_xml_pair(el),
            "date": DatePair.from_xml_pair(el)
        }

    def save(self) -> Xml.Element:
        """
        Save StudentPair to XML element.
        """
        element = Xml.Element("pair")
        for attrib in self._attributes.values():
            element.append(attrib.save())

        return element

    def get_number(self) -> int:
        """
        Returns the number of the pair in order.
        """
        return self._attributes["time"].get_number()

    def get_value(self, item):
        """
        Returned value pair by attrib.
        """
        return self._attributes.get(item)

    def __getitem__(self, item):
        return self._attributes[item]

    def copy(self):
        """
        Returns a copy of a pair.
        """
        new_pair = StudentPair()
        for attrib_name in self._attributes.keys():
            new_pair._attributes[attrib_name] = self._attributes[attrib_name].copy()

        return new_pair

    def __str__(self):
        s = ""
        for attrib_name, attrib in self._attributes.items():
            if attrib.is_valid() and attrib_name != "time":
                if attrib_name == "date":
                    s += "[" + str(attrib) + "]"
                else:
                    s += str(attrib) + ". "

        return s
