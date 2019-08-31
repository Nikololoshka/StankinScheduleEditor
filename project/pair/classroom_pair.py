# coding: utf-8

# imports
from xml.etree import ElementTree as Xml
from project.pair.attrib_pair import AttribPair


class ClassroomPair(AttribPair):
    """
    Class describing the classroom pair.
    """
    def __init__(self, s: str = ""):
        super().__init__()
        self._classroom: str = s

    @staticmethod
    def from_json_pair(file):
        classroom = ClassroomPair()
        classroom.load(file)
        return classroom

    def set_classroom(self, s: str) -> None:
        """
        Sets the value of classroom.

        :param s: Classroom
        """
        self._classroom = s

    def load(self, json_element) -> None:
        self._classroom = json_element["classroom"]

    def save(self) -> str:
        return self._classroom

    def copy(self):
        new_classroom = ClassroomPair(self._classroom)
        return new_classroom

    def is_valid(self) -> bool:
        return self._classroom != ""

    def __str__(self):
        return self._classroom
