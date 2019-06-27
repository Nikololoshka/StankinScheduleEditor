# coding: utf-8

# imports
from PyQt5.QtCore import QObject
from xml.etree import ElementTree as Xml


class AttribPair(QObject):
    """
    Class describing attribute of the pair.
    """
    def __init__(self):
        super().__init__()

    @staticmethod
    def from_xml_pair(file: Xml.Element):
        """
        Loads an attribute from the XML representation of the StudentPair.

        :param file: XML element
        """
        pass

    def load(self, el: Xml.Element) -> None:
        """
        Loads an attribute from XML element.

        :param el: XML element
        """
        pass

    def save(self) -> Xml.Element:
        """
        Saves the attribute to XML element.
        """
        pass

    def copy(self):
        """
        Returns a copy of the current object.
        """
        pass

    def is_valid(self) -> bool:
        """
        Checks if the attribute is valid.
        Returns True/False.
        """
        pass
