# coding: utf-8

# imports
import xml.etree.ElementTree as Xml
import defaults
from student_pair import StudentPair


class Schedule:
    def __init__(self):
        self.schedule_list = {day: {number: [] for number in range(8)}
                              for day in defaults.get_day_of_weeks()}

    @staticmethod
    def from_xml(path):
        sch = Schedule()
        sch.load(path)
        return sch

    def load(self, path):
        tree = Xml.ElementTree(file=path)
        root = tree.getroot()

        for day_of_week in root:
            for xml_pair in day_of_week:
                pair = StudentPair(xml_pair)
                number_pair = pair.get_number()
                self.schedule_list[day_of_week.tag][number_pair].append(pair)


if __name__ == '__main__':
    s = Schedule.from_xml("./temp/example.xml")
    print(s)
