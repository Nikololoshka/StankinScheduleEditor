# coding: utf-8

# imports
from xml.etree import ElementTree
from xml.dom import minidom


def prettify(elem):
    """ Return a pretty-printed XML string for the Element. """
    rough_string = ElementTree.tostring(elem, encoding='utf-8')
    parse = minidom.parseString(rough_string)
    return parse.toprettyxml()


def get_lecturers() -> set:
    """ Returns a list of lecturers """
    with open("./res/lecturers.txt", "r") as file:
        return set(line for line in file)


def get_time_start() -> tuple:
    return "8:30", "10:20", "12:20", "14:10",  \
            "16:00", "18:00", "19:40", "21:20"


def get_time_end() -> tuple:
    return "10:10", "12:00", "14:00", "15:50", \
            "17:40", "19:30", "21:10", "22:50"


def get_time_start_end(number) -> str:
    return "{} - {}".format(get_time_start()[number], get_time_end()[number])

