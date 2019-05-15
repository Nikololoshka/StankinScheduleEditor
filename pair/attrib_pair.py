# coding: utf-8

# imports
from xml.etree import ElementTree as Xml


class AttribPair:
    @staticmethod
    def from_xml_pair(file: Xml.Element):
        pass

    def load(self, el: Xml.Element) -> None:
        pass

    def save(self) -> Xml.Element:
        pass

    def is_valid(self) -> bool:
        pass
