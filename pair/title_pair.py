# coding: utf-8

# imports
from xml.etree import ElementTree as Xml
from pair.attrib_pair import AttribPair


class TitlePair(AttribPair):
    def __init__(self, s: str = ""):
        self._title: str = s

    @staticmethod
    def from_xml_pair(file: Xml.Element):
        title = TitlePair()
        title.load(file.find("title"))
        return title

    def set_title(self, s: str):
        self._title = s

    def load(self, el: Xml.Element) -> None:
        self._title = el.text

    def save(self) -> Xml.Element:
        element = Xml.Element("title")
        element.text = self._title
        return element

    def is_valid(self) -> bool:
        return self._title != ""

    def __str__(self):
        return self._title
