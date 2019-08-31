# coding: utf-8

# imports
from PyQt5.QtCore import QObject
from xml.etree import ElementTree as Xml
from enum import Enum
from project.pair.attrib_pair import AttribPair


class TypePairAttrib(Enum):
    """
    Enum describing the possible types of a student pair.
    """
    Missing = 0
    Lecture = 1
    Seminar = 2
    Laboratory = 3

    @staticmethod
    def value_of(s: str):
        """
        Returns a type by its string representation.
        """
        return TypePairAttrib.__members__[s.title()]

    @staticmethod
    def items():
        """
        Returns a tuple of tuples of the form: (type name, type).
        """
        return (str(TypePairAttrib.Missing), TypePairAttrib.Missing), \
               (str(TypePairAttrib.Lecture), TypePairAttrib.Lecture), \
               (str(TypePairAttrib.Seminar), TypePairAttrib.Seminar), \
               (str(TypePairAttrib.Laboratory), TypePairAttrib.Laboratory)

    def __str__(self):
        translator = TypePairAttribTranslator()
        return translator.translate(self)


class TypePairAttribTranslator(QObject):
    """
    A helper class to translate the enumeration of a pair type value.
    """
    def translate(self, type: TypePairAttrib) -> str:
        """
        Returns the translation of a pair type value.
        """
        return {
            TypePairAttrib.Missing: "---",
            TypePairAttrib.Lecture: self.tr("Lecture"),
            TypePairAttrib.Seminar: self.tr("Seminar"),
            TypePairAttrib.Laboratory: self.tr("Laboratory work")
        }[type]


class TypePair(AttribPair):
    """
    Class describing the type of a student pair.
    """
    def __init__(self, t: TypePairAttrib = TypePairAttrib.Missing):
        super().__init__()
        self._type: TypePairAttrib = t

    @staticmethod
    def from_json_pair(file):
        t = TypePair()
        t.load(file)
        return t

    def set_type(self, t: TypePairAttrib):
        """
        Sets the value of type.

        :param t: Type
        """
        self._type = t

    def load(self, json_element) -> None:
        self._type = TypePairAttrib.value_of(json_element["type"])

    def save(self) -> str:
        return self._type.name

    def copy(self):
        new_type = TypePair(self._type)
        return new_type

    def is_valid(self) -> bool:
        return self._type is not TypePairAttrib.Missing

    def __str__(self):
        return str(self._type)
