# coding: utf-8

# imports
import xml.etree.ElementTree as Xml
from pair import StudentPair, StudentPairAttrib, DaysOfWeek
import defaults


class Schedule:
    def __init__(self):
        self.schedule_list = {
            day: {
                number: [] for number in range(8)
            } for day in DaysOfWeek
        }

    @staticmethod
    def from_xml(path):
        sch = Schedule()
        sch.load(path)
        return sch

    def load(self, path):
        """ Load Schedule from XML file. Returns Schedule """
        tree = Xml.ElementTree(file=path)
        root = tree.getroot()

        for day_of_week in root:
            for xml_pair in day_of_week:
                pair = StudentPair.from_xml(xml_pair)
                self.add_pair(pair)

        return self

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
        return self.schedule_list[DaysOfWeek.value_of(i)][j]

    def add_pair(self, pair: StudentPair):
        time = pair.get_value(StudentPairAttrib.Time).get_number()
        week_day = pair.get_value(StudentPairAttrib.Date).get_week_day()

        dates = self.schedule_list[week_day][time]

        i = 0
        while i < len(dates):
            if not dates[i].get_value(StudentPairAttrib.Date) < pair.get_value(StudentPairAttrib.Date):
                break
            i += 1

        self.schedule_list[week_day][time].insert(i, pair)


if __name__ == '__main__':
    # tests
    s = Schedule.from_xml("./examples/example.xml")

    print(s)
    print(s.pairs_by_index(0, 2))
