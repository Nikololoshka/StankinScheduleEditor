# coding: utf-8

# imports
from PyQt5.QtCore import QObject, QT_TR_NOOP_UTF8
import xml.etree.ElementTree as Xml
from project.pair.attrib_pair import AttribPair
from datetime import datetime, timedelta
from enum import Enum


class DaysOfWeek(Enum):
    """ Enum describing student days of the week """
    Monday = "monday"
    Tuesday = "tuesday"
    Wednesday = "wednesday"
    Thursday = "thursday"
    Friday = "friday"
    Saturday = "saturday"

    def index_of(self) -> int:
        """ Returns the day of the week in order """
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

        raise InvalidDatePair("Wrong day of the week")

    @staticmethod
    def to_list():
        """ Returns a list of the names of the days of the week """
        return [str(name) for name in DaysOfWeek.__members__.values()]

    def __str__(self) -> str:
        return {
            DaysOfWeek.Monday: QT_TR_NOOP_UTF8("Понедельник"),
            DaysOfWeek.Tuesday: QT_TR_NOOP_UTF8("Вторник"),
            DaysOfWeek.Wednesday: QT_TR_NOOP_UTF8("Среда"),
            DaysOfWeek.Thursday: QT_TR_NOOP_UTF8("Четверг"),
            DaysOfWeek.Friday: QT_TR_NOOP_UTF8("Пятница"),
            DaysOfWeek.Saturday: QT_TR_NOOP_UTF8("Суббота")
        }[self]


class FrequencyDate(Enum):
    """ Enum describing the frequency of student classes """
    Once = "once"
    Every = "every"
    Throughout = "throughout"

    @staticmethod
    def value_of(s: str):
        """ Returns the frequency of a pair by its string representation """
        return FrequencyDate.__members__[s.title()]

    def __str__(self):
        return {
            FrequencyDate.Once: QT_TR_NOOP_UTF8(""),
            FrequencyDate.Every: QT_TR_NOOP_UTF8("к.н."),
            FrequencyDate.Throughout: QT_TR_NOOP_UTF8("ч.н.")
        }[self]


class InvalidDatePair(Exception):
    """ Class that describes errors associated with the date """
    def __init__(self, msg):
        self._msg = msg

    def __str__(self):
        return self._msg


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

    def copy(self):
        new_date = DateItem(self.date)
        return new_date

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
        if isinstance(item, DateItem):
            if item == self:
                return True

            return False

        if isinstance(item, DateRange):
            return self in item

        raise InvalidDatePair("Impossible to compare: {} with {}"
                              .format(self.__class__.__name__, item.__class__.__name__))

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

    def copy(self):
        new_date = DateRange(self.date_from,
                             self.date_to,
                             self.frequency)
        return new_date

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
        """ Return key in self. """
        if isinstance(item, DateItem):
            if self.frequency == FrequencyDate.Every:
                delta = timedelta(days=7)
            elif self.frequency == FrequencyDate.Throughout:
                delta = timedelta(days=14)
            else:
                raise InvalidDatePair("Incorrect \"frequency\" values for the date")

            start = datetime.strptime(self.date_from, "%Y.%m.%d")
            end = datetime.strptime(self.date_to, "%Y.%m.%d")

            while True:
                if item == DateItem(start.strftime("%Y.%m.%d")):
                    return True

                start += delta

                if start > end:
                    break

            return False

        if isinstance(item, DateRange):
            if item.date_from > self.date_from and item.date_from > self.date_to or \
                    item.date_to < self.date_from and item.date_to < self.date_to:
                return False

            return True

        raise InvalidDatePair("Impossible to compare: {} with {}"
                              .format(self.__class__.__name__, item.__class__.__name__))

    def __str__(self):
        return "{}-{} {}".format(DateItem.compact_date(self.date_from),
                                 DateItem.compact_date(self.date_to),
                                 str(self.frequency))


class DatePair(AttribPair):
    """ Class describing the dates of student pairs """
    def __init__(self):
        super().__init__()
        self._dates = list()
        self._week_day = None

    @staticmethod
    def from_xml_pair(file: Xml.Element):
        d = DatePair()
        d.load(file.find("dates"))
        return d

    def load(self, el: Xml.Element) -> None:
        for date_tag in el:
            try:
                frequency = FrequencyDate.value_of(date_tag.attrib["frequency"])

                if frequency == FrequencyDate.Once:
                    date_parse = DateItem(date_tag.text)
                else:
                    date_parse = DateRange(*date_tag.text.split("-"), frequency)

                self.add_date(date_parse)

            except KeyError:
                raise InvalidDatePair("Could not read the \"date\", because the frequency \"{}\" is not correct"
                                      .format(date_tag.attrib["frequency"]))

    def save(self) -> Xml.Element:
        element = Xml.Element("dates")
        for x in self._dates:
            element.append(x.save())

        return element

    def is_valid(self) -> bool:
        return len(self._dates) != 0

    def get_week_day(self) -> DaysOfWeek:
        """ Returns the day of the week date """
        return self._week_day

    def add_date(self, date_item) -> None:
        """ Adds a date to the list of dates """
        if self._week_day is None:
            self._week_day = date_item.get_week_day()
        else:
            if self._week_day != date_item.get_week_day():
                raise InvalidDatePair(self.tr("Dates have a different day of the week"))

        if date_item in self:
            raise InvalidDatePair(self.tr("Date crosses existing dates"))

        i = 0
        while i < len(self._dates):
            if not self._dates[i] < date_item:
                break
            i += 1

        self._dates.insert(i, date_item)

    def remove_date(self, date_item) -> None:
        """ Removes a date from the date list """
        self._dates.remove(date_item)
        if len(self._dates) == 0:
            self._week_day = None

    def copy(self):
        new_dates = DatePair()
        for date in self:
            new_dates.add_date(date.copy())

        return new_dates

    def __iter__(self) -> (DateItem, DateRange):
        for date in self._dates:
            yield date

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
        """ Return item in self. """
        for x in self._dates:
            if x in item:
                return True

        return False

    def __str__(self):
        s = ""
        for i in range(len(self._dates)):
            s += str(self._dates[i])
            if i != len(self._dates) - 1:
                s += ", "

        return s
