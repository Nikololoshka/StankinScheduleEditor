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

import json


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
            "dates": DatePair()
        }

    @staticmethod
    def from_json(file: dict):
        """
        Load Pair from JSON element. Returned StudentPair.
        """
        pair = StudentPair()
        pair.load(file)
        return pair

    def load(self, el: dict):
        """
        Load StudentPair from XML element.
        """
        self._attributes = {
            "title": TitlePair.from_json_pair(el),
            "lecturer": LecturerPair.from_json_pair(el),
            "type": TypePair.from_json_pair(el),
            "subgroup": SubgroupPair.from_json_pair(el),
            "classroom": ClassroomPair.from_json_pair(el),
            "time": TimePair.from_json_pair(el),
            "dates": DatePair.from_json_pair(el)
        }

    def save(self) -> dict:
        """
        Save StudentPair to dict for JSON.
        """
        element = {}
        for key, attrib in self._attributes.items():
            element[key] = attrib.save()

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
                if attrib_name == "dates":
                    s += "[" + str(attrib) + "]"
                else:
                    s += str(attrib) + ". "

        return s
