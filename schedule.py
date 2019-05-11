# coding: utf-8

# imports
import xml.etree.ElementTree as Xml
import defaults
from student_pair import StudentPair


class Schedule:
    def __init__(self):
        self.schedule_list = {day: {number: [] for number in range(8)}
                              for day in defaults.get_day_of_weeks()}

    def load(self, path):
        tree = Xml.ElementTree(file=path)
        root = tree.getroot()

        for day_of_week in root:
            for xml_pair in day_of_week:
                pair = StudentPair().load(xml_pair)
                number_pair = pair.get_number()
                self.schedule_list[day_of_week.tag][number_pair].append(pair)

    def save(self, path):
        with open(path, "w") as file:
            element_schedule = Xml.Element("schedule")
            for day, times in self.schedule_list.items():
                element_day = Xml.Element(day)
                for time, pairs in times.items():
                    for pair in pairs:
                        element_day.append(pair.save())
                element_schedule.append(element_day)
            file.write(defaults.prettify(element_schedule))

    def pairs_by_index(self, i, j) -> list:
        return self.schedule_list[defaults.get_day_of_weeks()[i]][j]


if __name__ == '__main__':
    s = Schedule()
    s.load("./temp/example.xml")

    print(s)
