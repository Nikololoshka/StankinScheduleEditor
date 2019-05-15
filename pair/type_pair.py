# coding: utf-8

# imports
from xml.etree import ElementTree as Xml
from enum import Enum
from pair.attrib_pair import AttribPair


class TypePairAttrib(Enum):
    Missing = 0
    Lecture = 1
    Seminar = 2

    @staticmethod
    def value_of(s: str):
        return TypePairAttrib.__members__[s.title()]

    @staticmethod
    def items():
        return (str(TypePairAttrib.Missing), TypePairAttrib.Missing), \
               (str(TypePairAttrib.Lecture), TypePairAttrib.Lecture), \
               (str(TypePairAttrib.Seminar), TypePairAttrib.Seminar)

    def __str__(self):
        return {
            TypePairAttrib.Missing: "---",
            TypePairAttrib.Lecture: "Лекция",
            TypePairAttrib.Seminar: "Семинар"
        }[self]


class TypePair(AttribPair):
    def __init__(self, t: TypePairAttrib = TypePairAttrib.Missing):
        self._type: TypePairAttrib = t

    @staticmethod
    def from_xml_pair(file: Xml.Element):
        t = TypePair()
        t.load(file.find("type"))
        return t

    def set_type(self, t: TypePairAttrib):
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

