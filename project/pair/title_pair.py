# coding: utf-8

# imports
from xml.etree import ElementTree as Xml
from project.pair.attrib_pair import AttribPair


class TitlePair(AttribPair):
    """
    Class describing the title pair.
    """
    def __init__(self, s: str = ""):
        super().__init__()
        self._title: str = s

    @staticmethod
    def from_json_pair(file):
        title = TitlePair()
        title.load(file)
        return title

    def set_title(self, s: str):
        """
        Sets the value of title.

        :param s: Title
        """
        self._title = s

    def load(self, json_element) -> None:
        self._title = json_element["title"]

    def save(self) -> str:
        return self._title

    def copy(self):
        new_title = TitlePair(self._title)
        return new_title

    def is_valid(self) -> bool:
        return self._title != ""

    def __str__(self):
        return self._title
