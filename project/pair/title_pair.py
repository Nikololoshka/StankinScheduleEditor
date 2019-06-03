# coding: utf-8

# imports
from xml.etree import ElementTree as Xml
from project.pair.attrib_pair import AttribPair


class TitlePair(AttribPair):
    """ Class describing the title pair """
    def __init__(self, s: str = ""):
        super().__init__()
        self._title: str = s

    @staticmethod
    def from_xml_pair(file: Xml.Element):
        title = TitlePair()
        title.load(file.find("title"))
        return title

    def set_title(self, s: str):
        """ Sets the value of title """
        self._title = s

    def load(self, el: Xml.Element) -> None:
        self._title = el.text

    def save(self) -> Xml.Element:
        element = Xml.Element("title")
        element.text = self._title
        return element

    def copy(self):
        new_title = TitlePair(self._title)
        return new_title

    def is_valid(self) -> bool:
        return self._title != ""

    def __str__(self):
        return self._title
