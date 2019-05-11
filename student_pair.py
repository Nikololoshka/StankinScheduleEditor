# coding: utf-8

# imports
import xml.etree.ElementTree as Xml
from date_pair import DatePair
from time_pair import TimePair


class StudentPair:
    """ Class describing the student pair """
    def __init__(self):
        self.pair = {
            "title": None,
            "lecturer": None,
            "type": None,
            "subgroup": None,
            "classroom": None,
            "time": None,
            "dates": None
        }

    def get_number(self):
        return self.pair["time"].get_number()

    def update(self, key, value):
        self.pair[key] = value

    def get_value(self, key):
        """ Returned value pair by key. If the key is not found will return 'None' """
        return self.pair.get(key)

    def load(self, xml_file: Xml.Element):
        self.pair = {
            "title": xml_file.findtext("title"),
            "lecturer": xml_file.findtext("lecturer"),
            "type": xml_file.findtext("type"),
            "subgroup": xml_file.findtext("subgroup"),
            "classroom": xml_file.findtext("classroom"),
            "time": TimePair.from_xml_element(xml_file.find("time")),
            "dates": DatePair.from_xml_element(xml_file.find("dates"))
        }
        return self

    def save(self):
        """ Create XML file of the student pair """
        element = Xml.Element("pair")
        lst = ["title", "lecturer", "type", "subgroup", "classroom"]
        for x in lst:
            sub_element = Xml.SubElement(element, x)
            sub_element.text = self.pair[x]

        element.append(self.pair["time"].to_xml_element())
        element.append(self.pair["dates"].to_xml_element())

        return element

    def __str__(self):
        lst = ["title", "lecturer", "type", "subgroup", "classroom"]
        s = ""
        for x in lst:
            if self.pair[x] != "None":
                s += self.pair[x] + ". "

        s += "[" + str(self.pair["dates"]) + "]"

        return s


if __name__ == '__main__':
    tree = Xml.ElementTree(file="./temp/example.xml")
    root = tree.getroot()

    if not Xml.iselement(root):
        print("No valid root of tree")
        exit(-1)

    print("root - tag: '{}', attrib: {}".format(root.tag, root.attrib))

    for day_of_week in root:
        for pair in day_of_week:
            sp = StudentPair().load(pair)
            print(sp)
