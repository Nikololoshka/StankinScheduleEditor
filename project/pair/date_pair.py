# coding: utf-8

# imports
from PyQt5.QtCore import QObject
import xml.etree.ElementTree as Xml
from project.pair.attrib_pair import AttribPair
from datetime import datetime, timedelta
from enum import Enum


class DaysOfWeek(Enum):
    """
    Enum describing student days of the week.
    """
    Monday = "monday"
    Tuesday = "tuesday"
    Wednesday = "wednesday"
    Thursday = "thursday"
    Friday = "friday"
    Saturday = "saturday"

    def index_of(self) -> int:
        """
        Returns the day of the week in order.
        """
        for i, day in enumerate(DaysOfWeek.__members__.values()):
            if self == day:
                return i

        return -1

    @staticmethod
    def value_of(index: int):
        """
        Returns the day of the week by its number.
        :param index: Index of day
        """
        for i, day in enumerate(DaysOfWeek.__members__.values()):
            if i == index:
                return day

        raise InvalidDatePair("Wrong day of the week")

    @staticmethod
    def to_list() -> list:
        """
        Returns a list of the names of the days of the week.
        """
        return [str(name) for name in DaysOfWeek.__members__.values()]

    def __str__(self) -> str:
        translator = DaysOfWeekTranslator()
        return translator.translate(self)


class DaysOfWeekTranslator(QObject):
    """
    A helper class to translate the enumeration of the days of the week.
    """

    def translate(self, day: DaysOfWeek) -> str:
        """
        Returns the translation of the day of the week.
        :param day: Day of week
        """
        return {
            DaysOfWeek.Monday: self.tr("Monday"),
            DaysOfWeek.Tuesday: self.tr("Tuesday"),
            DaysOfWeek.Wednesday: self.tr("Wednesday"),
            DaysOfWeek.Thursday: self.tr("Thursday"),
            DaysOfWeek.Friday: self.tr("Friday"),
            DaysOfWeek.Saturday: self.tr("Saturday")
        }[day]


class FrequencyDate(Enum):
    """
    Enum describing the frequency of student classes.
    """
    Once = "once"
    Every = "every"
    Throughout = "throughout"

    @staticmethod
    def value_of(s: str):
        """
        Returns the frequency of a pair by its string representation.
        """
        return FrequencyDate.__members__[s.title()]

    def __str__(self):
        translator = FrequencyDateTranslator()
        return translator.translate(self)


class FrequencyDateTranslator(QObject):
    """
    A helper class to translate the enumeration of the frequency of student classes.
    """

    def translate(self, frequency: FrequencyDate) -> str:
        """
        Returns the translation of the frequency of student classes.
        """
        return {
            FrequencyDate.Once: self.tr(""),
            FrequencyDate.Every: self.tr("e.w."),
            FrequencyDate.Throughout: self.tr("t.w.")
        }[frequency]


class InvalidDatePair(Exception):
    """
    Class that describes errors associated with the date.
    """

    def __init__(self, msg):
        self._msg = msg

    def __str__(self):
        return self._msg


class DateItem:
    """
    Class that describes the element of dates.
    """

    def __init__(self, str_date):
        self.date: str = str_date

    @staticmethod
    def compact_date(date_str) -> str:
        """
        Returns a compact representation of the date. I.e. "%d.%m"
        Example: 2019.02.24 -> 24.02

        :param date_str: Input string of date
        """
        return datetime.strptime(date_str, "%Y.%m.%d").strftime("%d.%m")

    def save(self) -> dict:
        """
        Save DateItem to XML file
        """
        return {"frequency": FrequencyDate.Once.value,
                "date": self.date}

    def get_week_day(self) -> str:
        """
        Returns the day of the week date
         """
        index_day = datetime.strptime(self.date, "%Y.%m.%d").weekday()
        return DaysOfWeek.value_of(index_day)

    def copy(self):
        """
        Returns a copy of the date.
        """
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
    """
    Class that describes the date range.
    """

    def __init__(self, date_from, date_to, frequency):
        self.date_from: str = date_from
        self.date_to: str = date_to
        self.frequency: FrequencyDate = frequency

    def save(self) -> dict:
        """
        Save DateItem to XML file.
        """
        return {"frequency": self.frequency.value,
                "date": "{}-{}".format(self.date_from, self.date_to)}

    def get_week_day(self) -> str:
        """
        Returns the day of the week date.
        """
        index_day = datetime.strptime(self.date_from, "%Y.%m.%d").weekday()
        return DaysOfWeek.value_of(index_day)

    def copy(self):
        """
        Returns a copy of the date.
        """
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
            for date in self:
                if item == DateItem(date):
                    return True

            return False

        if isinstance(item, DateRange):
            for first_date in self:
                for second_date in item:
                    if first_date == second_date:
                        return True

            return False

        raise InvalidDatePair("Impossible to compare: {} with {}"
                              .format(self.__class__.__name__, item.__class__.__name__))

    def __iter__(self):
        if self.frequency == FrequencyDate.Every:
            delta = timedelta(days=7)
        elif self.frequency == FrequencyDate.Throughout:
            delta = timedelta(days=14)
        else:
            raise InvalidDatePair("Incorrect \"frequency\" values for the date")

        start = datetime.strptime(self.date_from, "%Y.%m.%d")
        end = datetime.strptime(self.date_to, "%Y.%m.%d")

        while start <= end:
            yield start.strftime("%Y.%m.%d")
            start += delta

    def __str__(self):
        return "{}-{} {}".format(DateItem.compact_date(self.date_from),
                                 DateItem.compact_date(self.date_to),
                                 str(self.frequency))


class DatePair(AttribPair):
    """
    Class describing the dates of student pairs.
    """

    def __init__(self):
        super().__init__()
        self._dates = list()
        self._week_day = None

    @staticmethod
    def from_json_pair(file):
        d = DatePair()
        d.load(file["dates"])
        return d

    def load(self, json_element) -> None:
        for json_date in json_element:
            try:
                frequency = FrequencyDate.value_of(json_date["frequency"])

                if frequency == FrequencyDate.Once:
                    date_parse = DateItem(json_date["date"])
                else:
                    date_parse = DateRange(*json_date["date"].split("-"), frequency)

                self.add_date(date_parse)

            except KeyError:
                raise InvalidDatePair("Could not read the \"date\", because the frequency \"{}\" is not correct"
                                      .format(json_date["frequency"]))

    def save(self) -> list:
        element = []
        for date in self._dates:
            element.append(date.save())

        return element

    def is_valid(self) -> bool:
        return len(self._dates) != 0

    def get_week_day(self) -> DaysOfWeek:
        """
        Returns the day of the week date.
        """
        return self._week_day

    def add_date(self, date_item) -> None:
        """
        Adds a date to the list of dates.

        :param date_item: Added date
        """
        if self._week_day is None:
            self._week_day = date_item.get_week_day()
        else:
            if self._week_day != date_item.get_week_day():
                raise InvalidDatePair("Dates have a different day of the week")

        if date_item in self:
            raise InvalidDatePair("Date crosses existing dates. ["
                                  + str(date_item) + "] , [" + str(self) + "]")

        i = 0
        while i < len(self._dates):
            if not self._dates[i] < date_item:
                break
            i += 1

        self._dates.insert(i, date_item)

    def remove_date(self, date_item) -> None:
        """
        Removes a date from the date list.

        :param date_item: Removed date
        """
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
