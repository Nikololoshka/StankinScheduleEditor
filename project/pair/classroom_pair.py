# coding: utf-8

# imports
from xml.etree import ElementTree as Xml
from project.pair.attrib_pair import AttribPair


class ClassroomPair(AttribPair):
    """ Class describing the classroom pair """
    def __init__(self, s: str = ""):
        super().__init__()
        self._classroom: str = s

    @staticmethod
    def from_xml_pair(file: Xml.Element):
        classroom = ClassroomPair()
        classroom.load(file.find("classroom"))
        return classroom

    def set_classroom(self, s: str) -> None:
        """ Sets the value of classroom """
        self._classroom = s

    def load(self, el: Xml.Element) -> None:
        self._classroom = el.text

    def save(self) -> Xml.Element:
        element = Xml.Element("classroom")
        element.text = self._classroom
        return element

    def copy(self):
        new_classroom = ClassroomPair(self._classroom)
        return new_classroom

    def is_valid(self) -> bool:
        return self._classroom != ""

    def __str__(self):
        return self._classroom
