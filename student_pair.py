# coding: utf-8

# imports
import xml.etree.ElementTree as Xml
from date_pair import DatePair


class StudentPair:
    """ Class describing the student pair """
    def __init__(self, xml_file: Xml.Element):
        self._pair = {
            "title": xml_file.findtext("title"),
            "lecturer": xml_file.findtext("lecturer"),
            "type": xml_file.findtext("type"),
            "subgroup": xml_file.findtext("subgroup"),
            "classroom": xml_file.findtext("classroom"),
            "dates": DatePair(xml_file.find("dates"))
        }

    def get_value(self, key):
        """ Returned value pair by key. If the key is not found will return 'None' """
        return self._pair.get(key)

    def to_xml_element(self):
        """ Create XML file of the student pair """
        element = Xml.Element("pair")

        for tag, value in self._pair.items():
            element.set(tag, value)

        return element

    def __str__(self):
        return "'StudentPair': " + str(self._pair)


if __name__ == '__main__':
    tree = Xml.ElementTree(file="./temp/example.xml")
    root = tree.getroot()

    if not Xml.iselement(root):
        print("No valid root of tree")
        exit(-1)

    print("root - tag: '{}', attrib: {}".format(root.tag, root.attrib))

    for day_of_week in root:
        print(day_of_week.tag)
        for pair in day_of_week:
            print("\t", StudentPair(pair))
