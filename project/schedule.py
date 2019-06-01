# coding: utf-8

# imports
import xml.etree.ElementTree as Xml
from project.pair import StudentPair, StudentPairAttrib, DaysOfWeek
from project import defaults


class Schedule:
    """ Class describing the schedule of pairs """
    def __init__(self):
        self.schedule_list = {
            day: {
                number: [] for number in range(8)
            } for day in DaysOfWeek
        }

    @staticmethod
    def from_xml(path):
        """ Load Schedule from XML file. Returns Schedule """
        sch = Schedule()
        sch.load(path)
        return sch

    def load(self, path) -> None:
        """ Load Schedule from XML file """
        tree = Xml.ElementTree(file=path)
        root = tree.getroot()

        for day_of_week in root:
            for xml_pair in day_of_week:
                pair = StudentPair.from_xml(xml_pair)
                self.add_pair(pair)

    def save(self, path):
        """ Save Schedule to XML file """
        with open(path, "w") as file:
            element_schedule = Xml.Element("schedule")
            for day, times in self.schedule_list.items():
                element_day = Xml.Element(day.value)
                for time, pairs in times.items():
                    for pair in pairs:
                        element_day.append(pair.save())

                element_schedule.append(element_day)

            file.write(defaults.prettify(element_schedule))

    def pairs_by_index(self, i, j) -> list:
        """ Returns a list of pairs in the table """
        return self.schedule_list[DaysOfWeek.value_of(i)][j]

    def add_pair(self, pair: StudentPair):
        """ Adds a student pair to the schedule """
        time = pair.get_value(StudentPairAttrib.Time).get_number()
        week_day = pair.get_value(StudentPairAttrib.Date).get_week_day()

        dates = self.schedule_list[week_day][time]

        i = 0
        while i < len(dates):
            if not dates[i].get_value(StudentPairAttrib.Date) < pair.get_value(StudentPairAttrib.Date):
                break
            i += 1

        self.schedule_list[week_day][time].insert(i, pair)
