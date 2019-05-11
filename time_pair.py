# coding: utf-8

# imports
from xml.etree import ElementTree as Xml
import defaults


class TimePair:
    def __init__(self, start, end, count=None):
        self._start = start
        self._end = end

        if count is not None:
            self._count = count
        else:
            start = defaults.get_time_start().index(self._start)
            end = defaults.get_time_end().index(self._end)
            self._count = start - end + 1

    @staticmethod
    def from_xml_element(xml_file: Xml.Element):
        return TimePair(xml_file.findtext("start"),
                        xml_file.findtext("end"),
                        xml_file.attrib.get("count"))

    def get_number(self) -> int:
        return defaults.get_time_start().index(self._start)

    def to_xml_element(self) -> Xml.Element:
        element = Xml.Element("time", {"count": self._count})
        sub_element = Xml.SubElement(element, "start")
        sub_element.text = self._start
        sub_element = Xml.SubElement(element, "end")
        sub_element.text = self._end
        return element

    def __str__(self):
        return "{} - {}".format(self._start, self._end)

    def __repr__(self):
        return str(self)


if __name__ == '__main__':
    example = "<time count=\"1\"> \
                    <start>12:20</start> \
                    <end>14:00</end> \
               </time>"

    el = Xml.fromstring(example)

    t = TimePair.from_xml_element(el)
    print(t)
