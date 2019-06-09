# coding: utf-8

# imports
import xml.etree.ElementTree as Xml
from project.pair import StudentPair, StudentPairAttrib, DaysOfWeek
from project import defaults


class ScheduleException(Exception):
    """ Class that describes errors associated with the schedule """

    def __init__(self, msg):
        self._msg = msg

    def __str__(self):
        return self._msg


class Schedule:
    """ Class describing the schedule of pairs """

    def __init__(self):
        self.change: bool = False
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

    def save(self, path) -> None:
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

    def clear(self) -> None:
        self.schedule_list = {
            day: {
                number: [] for number in range(8)
            } for day in DaysOfWeek
        }

    def is_change(self) -> bool:
        """ Returns True/False depending on whether there are changes in the schedule """
        return self.change

    def pairs_by_index(self, i, j) -> list:
        """ Returns a list of pairs in the table """
        return self.schedule_list[DaysOfWeek.value_of(i)][j]

    def add_pair(self, pair: StudentPair, back: bool = False) -> None:
        """ Adds a student pair to the schedule """
        time = pair.get_value(StudentPairAttrib.Time).get_number()
        week_day = pair.get_value(StudentPairAttrib.Date).get_week_day()

        pairs = self.schedule_list[week_day][time]

        for p in pairs:
            if pair.get_value(StudentPairAttrib.Date) in \
                    p.get_value(StudentPairAttrib.Date):
                if not pair.get_value(StudentPairAttrib.Subgroup).is_separate() and \
                        not p.get_value(StudentPairAttrib.Subgroup).is_separate():
                    raise ScheduleException("There can't be two pairs at the same time!\n"
                                            "{} and {}".format(str(pair), str(p)))

        i = 0
        while i < len(pairs):
            if not pairs[i].get_value(StudentPairAttrib.Date) < \
                   pair.get_value(StudentPairAttrib.Date):
                break
            i += 1

        self.schedule_list[week_day][time].insert(i, pair)

        if not back:
            self.change = True

    def remove_pair(self, i, j, pair: StudentPair):
        """ Remove a student pair from schedule  """
        pairs = self.pairs_by_index(i, j)
        pairs.remove(pair)
        self.change = True
