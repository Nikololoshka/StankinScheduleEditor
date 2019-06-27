# coding: utf-8

# imports
from xml.etree import ElementTree
from xml.dom import minidom


def prettify(elem) -> str:
    """
    Return a pretty-printed XML string for the Element.

    :param elem: Input XML element.
    """
    rough_string = ElementTree.tostring(elem, encoding='utf-8')
    parse = minidom.parseString(rough_string)
    return parse.toprettyxml()


def get_lecturers() -> set:
    """
    Returns a list of lecturers
    """
    with open("./res/lecturers.txt", "r", encoding="utf-8") as file:
        return set(line for line in file)


class SortedList(list):
    """
    Class describing the sorted list with the ability to install the comparator.
    """
    def __init__(self, cmp_function):
        super().__init__()
        self._cmp = cmp_function

    def append(self, x):
        i = 0
        while i < len(self):
            if not self._cmp(self[i], x):
                break
            i += 1

        self.insert(i, x)
