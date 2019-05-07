# coding: utf-8

# imports
import xml.etree.ElementTree as Xml
from datetime import datetime, timedelta
from enum import Enum

# debug import
import itertools


class FrequencyPair(Enum):
    """ Enum describing the frequency of student classes """
    ONCE = 1
    EVERY = 2
    THROUGHOUT = 3


class InvalidDatePair(Exception):
    def __init__(self, msg):
        self._msg = msg

    def __str__(self):
        return "InvalidDatePair: {}".format(self._msg)


class DateItem:
    """ Class that describes the element of dates """
    def __init__(self, str_date):
        self.date = str_date

    @staticmethod
    def compact_date(date_str):
        """
        Returns a compact representation of the date. I.e. "%d.%m"
        Example: 2019.02.24 -> 24.02
        """
        return datetime.strptime(date_str, "%Y.%m.%d").strftime("%d.%m")

    def is_less(self, other):
        """
        Compares dates. If the original date is less than the comparable one,
        then it returns true, otherwise it is false.
        """
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

    def __contains__(self, item):
        if item == self.date:
            return True

        return False

    def __str__(self):
        return DateItem.compact_date(self.date)


class DateRange:
    """ Class that describes the date range """
    def __init__(self, date_from, date_to, frequency):
        self.date_from = date_from
        self.date_to = date_to
        self.frequency = frequency

    def is_less(self, other):
        """
        Compares dates. If the original date is less than the comparable one,
        then it returns true, otherwise it is false.
        """
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

    def __contains__(self, item):
        if self.frequency == FrequencyPair.EVERY:
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
        return "{} - {} {}".format(DateItem.compact_date(self.date_from),
                                   DateItem.compact_date(self.date_to),
                                   "к.н." if self.frequency == FrequencyPair.EVERY else "ч.н.")


class DatePair:
    """ Class describing the date of student pairs """
    def __init__(self, xml_file: Xml.Element):
        self._dates = list()

        for date_tag in xml_file:
            try:
                frequency = FrequencyPair[date_tag.attrib["frequency"].upper()]

                if frequency == FrequencyPair.ONCE:
                    date_parse = DateItem(date_tag.text)
                else:
                    date_parse = DateRange(*date_tag.text.split("-"), frequency)

                i = 0
                while i < len(self._dates):
                    if not self._dates[i].is_less(date_parse):
                        break
                    i += 1

                self._dates.insert(i, date_parse)

            except KeyError:
                raise InvalidDatePair("Could not read the \"date\", because the frequency \"{}\" is not correct"
                                      .format(date_tag.attrib["frequency"]))

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

    def __repr__(self):
        return str(self)


if __name__ == '__main__':
    try:
        raise InvalidDatePair("The date range must have the same day of the week.")
    except InvalidDatePair as ex:
        print(ex)

    dates_lst = [
        "<date frequency=\"once\">2019.02.09</date>",
        "<date frequency =\"throughout\">2019.02.16-2019.03.16</date>",
        "<date frequency=\"every\">2019.03.23-2019.04.27</date>",
        "<date frequency=\"once\">2019.05.18</date>",
        "<date frequency=\"once\">2019.05.25</date>"
    ]

    el = Xml.fromstring("<dates>" + "".join(dates_lst) + "</dates>")
    date = DatePair(el)

    print("True:", "2019.03.30" in date)

    correct_str = "09.02, 16.02 - 16.03 ч.н., 23.03 - 27.04 к.н., 18.05, 25.05"

    count = 0
    for lst in itertools.permutations(dates_lst):
        el = Xml.fromstring("<dates>" + "".join(lst) + "</dates>")
        date = DatePair(el)

        if str(date) == correct_str:
            # print("cool\t", d,)
            count += 1
        else:
            print("bad\t", date)

    print("Done: {} / 120 is correct".format(count))
