# coding: utf-8

# imports
from PyQt5.QtCore import QObject
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
        translator = SubgroupPairAttribTranslator()
        return translator.translate(self)


class SubgroupPairAttribTranslator(QObject):
    """ A helper class to translate the enumeration of the subgroup value """
    def translate(self, subgroup: SubgroupPairAttrib) -> str:
        """ Returns the translation of the subgroup value """
        return {
            SubgroupPairAttrib.Common: "---",
            SubgroupPairAttrib.A: self.tr("(A)"),
            SubgroupPairAttrib.B: self.tr("(B)")
        }[subgroup]


class SubgroupPair(AttribPair):
    """
    Class describing the subgroup of a student pair.
    """
    def __init__(self, subgroup: SubgroupPairAttrib = SubgroupPairAttrib.Common):
        super().__init__()
        self._subgroup: SubgroupPairAttrib = subgroup

    @staticmethod
    def from_json_pair(file):
        subgroup = SubgroupPair()
        subgroup.load(file)
        return subgroup

    def set_subgroup(self, subgroup: SubgroupPairAttrib):
        """
        Sets the value of subgroup.

        :param subgroup: Subgroup value
        """
        self._subgroup = subgroup

    def get_subgroup(self):
        """
        Returns the value of subgroup.
        """
        return self._subgroup

    def is_separate(self):
        """
        Returns True/False depending on whether the student pair is separate by subgroup.
        """
        if self._subgroup == SubgroupPairAttrib.A or \
                self._subgroup == SubgroupPairAttrib.B:
            return True

        return False

    def load(self, json_element) -> None:
        self._subgroup = SubgroupPairAttrib.value_of(json_element["subgroup"])

    def save(self) -> str:
        return self._subgroup.name

    def copy(self):
        new_subgroup = SubgroupPair(self._subgroup)
        return new_subgroup

    def is_valid(self) -> bool:
        return self._subgroup is not SubgroupPairAttrib.Common

    def __str__(self):
        return str(self._subgroup)
