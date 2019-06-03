# coding: utf-8

# imports
from PyQt5.QtCore import QT_TR_NOOP_UTF8
from xml.etree import ElementTree as Xml
from enum import Enum
from project.pair.attrib_pair import AttribPair


class SubgroupPairAttrib(Enum):
    """ Enum describing the possible values of a subgroup """
    Common = 0
    A = 1
    B = 2

    @staticmethod
    def value_of(s: str):
        """ Returns a subgroup by its string representation """
        return SubgroupPairAttrib.__members__[s.title()]

    @staticmethod
    def items():
        """ Returns a tuple of tuples of the form: (subgroup name, subgroup) """
        return (str(SubgroupPairAttrib.Common), SubgroupPairAttrib.Common), \
               (str(SubgroupPairAttrib.A), SubgroupPairAttrib.A), \
               (str(SubgroupPairAttrib.B), SubgroupPairAttrib.B)

    def __str__(self):
        return {
            SubgroupPairAttrib.Common: "---",
            SubgroupPairAttrib.A: QT_TR_NOOP_UTF8("(А)"),
            SubgroupPairAttrib.B: QT_TR_NOOP_UTF8("(Б)")
        }[self]


class SubgroupPair(AttribPair):
    """ Class describing the subgroup of a student pair """
    def __init__(self, subgroup: SubgroupPairAttrib = SubgroupPairAttrib.Common):
        super().__init__()
        self._subgroup: SubgroupPairAttrib = subgroup

    @staticmethod
    def from_xml_pair(file: Xml.Element):
        subgroup = SubgroupPair()
        subgroup.load(file.find("subgroup"))
        return subgroup

    def set_subgroup(self, subgroup: SubgroupPairAttrib):
        """ Sets the value of subgroup """
        self._subgroup = subgroup

    def get_subgroup(self):
        """ Returns the value of subgroup """
        return self._subgroup

    def is_separate(self):
        """ Returns True/False depending on whether the student pair is separate by subgroup """
        if self._subgroup == SubgroupPairAttrib.A or \
                self._subgroup == SubgroupPairAttrib.B:
            return True

        return False

    def load(self, el: Xml.Element) -> None:
        self._subgroup = SubgroupPairAttrib.value_of(el.text)

    def save(self) -> Xml.Element:
        element = Xml.Element("subgroup")
        element.text = self._subgroup.name
        return element

    def copy(self):
        new_subgroup = SubgroupPair(self._subgroup)
        return new_subgroup

    def is_valid(self) -> bool:
        return self._subgroup is not SubgroupPairAttrib.Common

    def __str__(self):
        return str(self._subgroup)
