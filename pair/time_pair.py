# coding: utf-8

# imports
from xml.etree import ElementTree as Xml
from pair.attrib_pair import AttribPair
import defaults


class TimePair(AttribPair):
    """ Class describing the time of the pair """
    def __init__(self):
        self._start: str = ""
        self._end: str = ""
        self._count: int = 0

    def set_time(self, start: str, end: str, count: int = None):
        self._start = start
        self._end = end
        self.set_count(count)

    def set_start(self, start):
        self._start = start

    def set_end(self, end):
        self._end = end

    def set_count(self, count: int = 0):
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
        element = Xml.Element("time", {"count": self._count})

        sub_element = Xml.SubElement(element, "start")
        sub_element.text = self._start

        sub_element = Xml.SubElement(element, "end")
        sub_element.text = self._end

        return element

    def is_valid(self) -> bool:
        return self._start != "" and self._end != ""

    def __str__(self) -> str:
        return "{} - {}".format(self._start, self._end)


if __name__ == '__main__':
    # tests
    example = "<time count=\"1\">" \
              "<start>12:20</start>" \
              "<end>14:00</end>" \
              "</time>"

    elem = Xml.fromstring(example)

    t = TimePair()
    t.load(elem)
    print("Save/Load check:", Xml.tostring(t.save()).decode("utf-8") == example)
    print(t)
