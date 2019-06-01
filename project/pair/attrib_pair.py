# coding: utf-8

# imports
from xml.etree import ElementTree as Xml


class AttribPair:
    @staticmethod
    def from_xml_pair(file: Xml.Element):
        """ Loads an attribute from the XML representation of the StudentPair """
        pass

    def load(self, el: Xml.Element) -> None:
        """ Loads an attribute from XML file """
        pass

    def save(self) -> Xml.Element:
        """ Saves the attribute to XML file """
        pass

    def is_valid(self) -> bool:
        """ Checks if the attribute is valid. Returns True/False """
        pass
