# coding: utf-8

# imports
from PyQt5.QtCore import QObject


class AttribPair(QObject):
    """
    Class describing attribute of the pair.
    """
    def __init__(self):
        super().__init__()

    @staticmethod
    def from_json_pair(file: dict):
        """
        Loads an attribute from the JSON representation of the StudentPair.
        """
        pass

    def load(self, el: dict) -> None:
        """
        Loads an attribute from JSON element.
        """
        pass

    def save(self) -> (str, list, dict):
        """
        Saves the attribute.
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
