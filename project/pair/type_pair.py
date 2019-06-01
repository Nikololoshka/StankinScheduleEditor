# coding: utf-8

# imports
from xml.etree import ElementTree as Xml
from enum import Enum
from project.pair.attrib_pair import AttribPair


class TypePairAttrib(Enum):
    """ Enum describing the possible types of a student pair """
    Missing = 0
    Lecture = 1
    Seminar = 2
    Laboratory = 3

    @staticmethod
    def value_of(s: str):
        """ Returns a type by its string representation """
        return TypePairAttrib.__members__[s.title()]

    @staticmethod
    def items():
        """ Returns a tuple of tuples of the form: (type name, type) """
        return (str(TypePairAttrib.Missing), TypePairAttrib.Missing), \
               (str(TypePairAttrib.Lecture), TypePairAttrib.Lecture), \
               (str(TypePairAttrib.Seminar), TypePairAttrib.Seminar), \
               (str(TypePairAttrib.Laboratory), TypePairAttrib.Laboratory)

    def __str__(self):
        return {
            TypePairAttrib.Missing: "---",
            TypePairAttrib.Lecture: "Лекция",
            TypePairAttrib.Seminar: "Семинар",
            TypePairAttrib.Laboratory: "Лабораторная работа"
        }[self]


class TypePair(AttribPair):
    """  Class describing the type of a student pair """
    def __init__(self, t: TypePairAttrib = TypePairAttrib.Missing):
        self._type: TypePairAttrib = t

    @staticmethod
    def from_xml_pair(file: Xml.Element):
        t = TypePair()
        t.load(file.find("type"))
        return t

    def set_type(self, t: TypePairAttrib):
        """ Sets the value of type """
        self._type = t

    def load(self, el: Xml.Element) -> None:
        self._type = TypePairAttrib.value_of(el.text)

    def save(self) -> Xml.Element:
        element = Xml.Element("type")
        element.text = self._type.name
        return element

    def is_valid(self) -> bool:
        return self._type is not TypePairAttrib.Missing

    def __str__(self):
        return str(self._type)
