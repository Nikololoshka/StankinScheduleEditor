# coding: utf-8

# imports
from xml.etree import ElementTree as Xml
from project.pair.attrib_pair import AttribPair
from project import defaults


class TimePair(AttribPair):
    """ Class describing the time of a student pair """
    def __init__(self):
        self._start: str = ""
        self._end: str = ""
        self._count: int = 0

    def set_time(self, start: str, end: str, count: int = None):
        """ Sets the start time, end time, and number of pairs in this time period """
        self._start = start
        self._end = end
        self.set_count(count)

    def set_start(self, start):
        """ Sets the start time """
        self._start = start

    def set_end(self, end):
        """ Sets the end time """
        self._end = end

    def set_count(self, count: int = 0):
        """ Sets the number of pairs in this time period """
        self._count = count
        if self._count is None:
            start = defaults.get_time_start().index(self._start)
            end = defaults.get_time_end().index(self._end)
            self._count = start - end + 1

    def get_number(self) -> int:
        """ Returns the number of the pair in order """
        if self._start == "":
            return 0

        return defaults.get_time_start().index(self._start)

    @staticmethod
    def from_xml_pair(file: Xml.Element):
        time = TimePair()
        time.load(file.find("time"))
        return time

    def load(self, el: Xml.Element) -> None:
        """ Load TimePair from XML file. """
        self.set_time(el.findtext("start"),
                      el.findtext("end"),
                      el.attrib.get("count"))

    def save(self) -> Xml.Element:
        """ Save TimePair to XML file """
        element = Xml.Element("time", {"count": str(self._count)})

        sub_element = Xml.SubElement(element, "start")
        sub_element.text = self._start

        sub_element = Xml.SubElement(element, "end")
        sub_element.text = self._end

        return element

    def is_valid(self) -> bool:
        return self._start != "" and self._end != ""

    def __str__(self) -> str:
        return "{} - {}".format(self._start, self._end)
