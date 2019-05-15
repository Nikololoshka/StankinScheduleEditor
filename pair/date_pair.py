# coding: utf-8

# imports
import xml.etree.ElementTree as Xml
from pair.attrib_pair import AttribPair
from datetime import datetime, timedelta
from enum import Enum

# debug import
import itertools


class DaysOfWeek(Enum):
    """ Enum describing student days of the week """
    Monday = "monday"
    Tuesday = "tuesday"
    Wednesday = "wednesday"
    Thursday = "thursday"
    Friday = "friday"
    Saturday = "saturday"

    def index_of(self) -> int:
        for i, day in enumerate(DaysOfWeek.__members__.values()):
            if self == day:
                return i

        return -1

    @staticmethod
    def value_of(index: int):
        """ Returns the day of the week by its number """
        for i, day in enumerate(DaysOfWeek.__members__.values()):
            if i == index:
                return day

        return None

    @staticmethod
    def to_list():
        return [str(name) for name in DaysOfWeek.__members__.values()]

    def __str__(self) -> str:
        return {
            DaysOfWeek.Monday: "Понедельник",
            DaysOfWeek.Tuesday: "Вторник",
            DaysOfWeek.Wednesday: "Среда",
            DaysOfWeek.Thursday: "Четверг",
            DaysOfWeek.Friday: "Пятница",
            DaysOfWeek.Saturday: "Суббота"
        }[self]


class FrequencyDate(Enum):
    """ Enum describing the frequency of student classes """
    Once = "once"
    Every = "every"
    Throughout = "throughout"

    @staticmethod
    def value_of(s: str):
        return FrequencyDate.__members__[s.title()]

    def __str__(self):
        return {
            FrequencyDate.Once: "",
            FrequencyDate.Every: "к.н.",
            FrequencyDate.Throughout: "ч.н."
        }[self]


class InvalidDatePair(Exception):
    """ Class that describes errors associated with the date """
    def __init__(self, msg):
        self._msg = msg

    def __str__(self):
        return "InvalidDatePair: {}".format(self._msg)


class DateItem:
    """ Class that describes the element of dates """
    def __init__(self, str_date):
        self.date: str = str_date

    @staticmethod
    def compact_date(date_str) -> str:
        """
        Returns a compact representation of the date. I.e. "%d.%m"
        Example: 2019.02.24 -> 24.02
        """
        return datetime.strptime(date_str, "%Y.%m.%d").strftime("%d.%m")

    def save(self) -> Xml.Element:
        """ Save DateItem to XML file """
        element = Xml.Element("date", {"frequency": FrequencyDate.Once.value})
        element.text = self.date
        return element

    def get_week_day(self) -> str:
        """ Returns the day of the week date """
        index_day = datetime.strptime(self.date, "%Y.%m.%d").weekday()
        return DaysOfWeek.value_of(index_day)

    def __eq__(self, other):
        """ Return self == other. """
        if isinstance(other, DateItem):
            if self.date == other.date:
                return True

            return False

        if isinstance(other, DateRange):
            return False

        raise InvalidDatePair("Impossible to compare: {} with {}"
                              .format(self.__class__.__name__, other.__class__.__name__))

    def __ne__(self, other):
        """ Return self != other. """
        return not self == other

    def __lt__(self, other):
        """ Return self < other. """
        if isinstance(other, DateRange):
            if self.date < other.date_from and self.date < other.date_to:
                return True

            return False

        if isinstance(other, DateItem):
            if self.date < other.date:
                return True

            return False

        raise InvalidDatePair("Impossible to compare: {} with {}"
                              .format(self.__class__.__name__, other.__class__.__name__))

    def __le__(self, other):
        """ Return self <= other. """
        return self < other or self == other

    def __gt__(self, other):
        """ Return self > other. """
        return not self <= other

    def __ge__(self, other):
        """ Return self >= other. """
        return not self < other

    def __contains__(self, item):
        if item == self.date:
            return True

        return False

    def __str__(self) -> str:
        return DateItem.compact_date(self.date)


class DateRange:
    """ Class that describes the date range """
    def __init__(self, date_from, date_to, frequency):
        self.date_from: str = date_from
        self.date_to: str = date_to
        self.frequency: FrequencyDate = frequency

    def save(self) -> Xml.Element:
        """ Save DateItem to XML file """
        element = Xml.Element("date", {"frequency": self.frequency.value})
        element.text = "{}-{}".format(self.date_from, self.date_to)
        return element

    def get_week_day(self) -> str:
        """ Returns the day of the week date """
        index_day = datetime.strptime(self.date_from, "%Y.%m.%d").weekday()
        return DaysOfWeek.value_of(index_day)

    def __eq__(self, other):
        """ Return self == other. """
        if isinstance(other, DateRange):
            if self.date_from == other.date_from and self.date_from == other.date_to:
                return True

            return False

        if isinstance(other, DateItem):
            return False

        raise InvalidDatePair("Impossible to compare: {} with {}"
                              .format(self.__class__.__name__, other.__class__.__name__))

    def __ne__(self, other):
        """ Return self != other. """
        return not self == other

    def __lt__(self, other):
        """ Return self < other. """
        if isinstance(other, DateRange):
            if self.date_from < other.date_from and self.date_to < other.date_to:
                return True

            return False

        if isinstance(other, DateItem):
            if self.date_from < other.date and self.date_to < other.date:
                return True

            return False

        raise InvalidDatePair("Impossible to compare: {} with {}"
                              .format(self.__class__.__name__, other.__class__.__name__))

    def __le__(self, other):
        """ Return self <= other. """
        return self < other or self == other

    def __gt__(self, other):
        """ Return self > other. """
        return not self <= other

    def __ge__(self, other):
        """ Return self >= other. """
        return not self < other

    def __contains__(self, item):
        if self.frequency == FrequencyDate.Every:
            delta = timedelta(days=7)
        else:
            delta = timedelta(days=14)

        start = datetime.strptime(self.date_from, "%Y.%m.%d")
        end = datetime.strptime(self.date_to, "%Y.%m.%d")

        while True:
            if item == start.strftime("%Y.%m.%d"):
                return True

            start += delta

            if start > end:
                break

        return False

    def __str__(self):
        return "{}-{} {}".format(DateItem.compact_date(self.date_from),
                                 DateItem.compact_date(self.date_to),
                                 str(self.frequency))


class DatePair(AttribPair):
    """ Class describing the date of student pairs """
    def __init__(self):
        self._dates = list()
        self._week_day = None

    @staticmethod
    def from_xml_pair(file: Xml.Element):
        d = DatePair()
        d.load(file.find("dates"))
        return d

    def load(self, el: Xml.Element) -> None:
        """ Load DatePair from XML file """
        for date_tag in el:
            try:
                frequency = FrequencyDate.value_of(date_tag.attrib["frequency"])

                if frequency == FrequencyDate.Once:
                    date_parse = DateItem(date_tag.text)
                else:
                    date_parse = DateRange(*date_tag.text.split("-"), frequency)

                if self._week_day is None:
                    self._week_day = date_parse.get_week_day()
                else:
                    if self._week_day != date_parse.get_week_day():
                        raise InvalidDatePair("Dates have a different day of the week")

                i = 0
                while i < len(self._dates):
                    if not self._dates[i] < date_parse:
                        break
                    i += 1

                self._dates.insert(i, date_parse)

            except KeyError:
                raise InvalidDatePair("Could not read the \"date\", because the frequency \"{}\" is not correct"
                                      .format(date_tag.attrib["frequency"]))

    def save(self) -> Xml.Element:
        """ Save DatePair to XML file """
        element = Xml.Element("dates")
        for x in self._dates:
            element.append(x.save())

        return element

    def is_valid(self) -> bool:
        return len(self._dates) != 0

    def get_week_day(self) -> DaysOfWeek:
        """ Returns the day of the week date """
        return self._week_day

    def __eq__(self, other):
        """ Return self == other. """
        if isinstance(other, DatePair):
            for date1 in self._dates:
                for date2 in other._dates:
                    if date1 != date2:
                        return False

            return True

        raise InvalidDatePair("Impossible to compare: {} with {}"
                              .format(self.__class__.__name__, other.__class__.__name__))

    def __ne__(self, other):
        """ Return self != other. """
        return not self == other

    def __lt__(self, other):
        """ Return self < other. """
        if isinstance(other, DatePair):
            for date1 in self._dates:
                for date2 in other._dates:
                    if date1 >= date2:
                        return False

            return True

        raise InvalidDatePair("Impossible to compare: {} with {}"
                              .format(self.__class__.__name__, other.__class__.__name__))

    def __le__(self, other):
        """ Return self <= other. """
        return self < other or self == other

    def __gt__(self, other):
        """ Return self > other. """
        return not self <= other

    def __ge__(self, other):
        """ Return self >= other. """
        return not self < other

    def __contains__(self, item):
        for x in self._dates:
            if item in x:
                return True

        return False

    def __str__(self):
        s = ""
        for i in range(len(self._dates)):
            s += str(self._dates[i])
            if i != len(self._dates) - 1:
                s += ", "

        return s


if __name__ == '__main__':
    # tests
    try:
        raise InvalidDatePair("The date range must have the same day of the week.")
    except InvalidDatePair as ex:
        print("Exception check:", ex)

    dates_lst = [
        "<date frequency=\"once\">2019.02.09</date>",
        "<date frequency=\"throughout\">2019.02.16-2019.03.16</date>",
        "<date frequency=\"every\">2019.03.23-2019.04.27</date>",
        "<date frequency=\"once\">2019.05.18</date>",
        "<date frequency=\"once\">2019.05.25</date>"
    ]

    elem = Xml.fromstring("<dates>" + "".join(dates_lst) + "</dates>")
    date = DatePair()
    date.load(elem)

    print("Save/Load check:", Xml.tostring(date.save()).decode("utf-8") == "<dates>" + "".join(dates_lst) + "</dates>")
    print("Contains method check:", "2019.03.30" in date)

    correct_str = "09.02, 16.02-16.03 ч.н., 23.03-27.04 к.н., 18.05, 25.05"

    count = 0
    for lst in itertools.permutations(dates_lst):
        elem = Xml.fromstring("<dates>" + "".join(lst) + "</dates>")
        date = DatePair()
        date.load(elem)

        if str(date) == correct_str:
            # print("cool\t", d,)
            count += 1
        else:
            print("bad\t", date)

    print("Combination check: {} / 120 is correct".format(count))
