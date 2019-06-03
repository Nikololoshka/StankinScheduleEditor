# coding: utf-8

# imports
from xml.etree import ElementTree as Xml
from project.pair.attrib_pair import AttribPair


class LecturerPair(AttribPair):
    """ Class describing the lecturer pair """
    def __init__(self, s: str = ""):
        super().__init__()
        self._lecturer: str = s

    @staticmethod
    def from_xml_pair(file: Xml.Element):
        lecturer = LecturerPair()
        lecturer.load(file.find("lecturer"))
        return lecturer

    def set_lecturer(self, s: str):
        """ Sets the value of lecturer """
        self._lecturer = s

    def load(self, el: Xml.Element) -> None:
        self._lecturer = el.text

    def save(self) -> Xml.Element:
        element = Xml.Element("lecturer")
        element.text = self._lecturer
        return element

    def copy(self):
        new_lecturer = LecturerPair(self._lecturer)
        return new_lecturer

    def is_valid(self) -> bool:
        return self._lecturer != ""

    def __str__(self):
        return self._lecturer
