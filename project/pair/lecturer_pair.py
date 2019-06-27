# coding: utf-8

# imports
from xml.etree import ElementTree as Xml
from project.pair.attrib_pair import AttribPair
from project.settings import Settings


class LecturerPair(AttribPair):
    """
    Class describing the lecturer pair.
    """
    def __init__(self, s: str = ""):
        super().__init__()
        self._lecturer: str = s

    @staticmethod
    def from_xml_pair(file: Xml.Element):
        lecturer = LecturerPair()
        lecturer.load(file.find("lecturer"))
        return lecturer

    def set_lecturer(self, s: str):
        """
        Sets the value of lecturer.
        :param s: Lecturer
        """
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
        if Settings.ShortName:
            lst = self._lecturer.replace(".", " ").split()
            lecturer = lst[0]
            lecturer += " " + ".".join(word[0] for word in lst[1:])
            return lecturer
        else:
            return self._lecturer
