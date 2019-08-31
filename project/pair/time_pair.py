# coding: utf-8

# imports
from xml.etree import ElementTree as Xml
from project.pair.attrib_pair import AttribPair


class TimePair(AttribPair):
    """
    Class describing the time of a student pair.
    """
    def __init__(self):
        super().__init__()
        self._start: str = ""
        self._start_number = 0
        self._end: str = ""
        self._end_number = 0
        self._duration: int = 0

    def set_time(self, start: str, end: str, duration: int = None):
        """
        Sets the start time, end time, and number of pairs in this time period.
        """
        self.set_start(start)
        self.set_end(end)
        self.set_count(duration)

    def set_start(self, start):
        """
        Sets the start time.
        """
        self._start = start
        self._start_number = self.time_starts().index(self._start)

    def set_end(self, end):
        """
        Sets the end time.
        """
        self._end = end
        self._end_number = self.time_ends().index(self._end)

    def set_count(self, duration: int = 0):
        """
        Sets the number of pairs in this time period.
        """
        if duration is None:
            start = self.time_starts().index(self._start)
            end = self.time_ends().index(self._end)
            self._duration = end - start + 1
        else:
            self._duration = int(duration)

    def get_number(self) -> int:
        """
        Returns the number of the pair in order.
        """
        return self._start_number

    @staticmethod
    def from_json_pair(file):
        time = TimePair()
        time.load(file["time"])
        return time

    def load(self, json_element) -> None:
        self.set_time(json_element["start"], json_element["end"])

    def save(self) -> dict:
        return {"start": self._start, "end": self._end}

    def copy(self):
        new_time = TimePair()
        new_time.set_time(self._start, self._end, self._duration)
        return new_time

    def intersect(self, other) -> bool:
        """
        True - if times intersect, otherwise False.

        :param other: Other TimePair
        """
        if isinstance(other, TimePair):
            if (self._start_number >= other._start_number) and (self._end_number <= other._end_number) or \
                    (self._start_number <= other._start_number) and (self._end_number >= other._start_number) or \
                    (self._start_number <= other._end_number) and (self._end_number >= other._end_number):
                return True
            else:
                return False

    @staticmethod
    def time_starts() -> tuple:
        """
        Returns the tuple of the start time of the pairs.
        """
        return "8:30", "10:20", "12:20", "14:10", \
               "16:00", "18:00", "19:40", "21:20"

    @staticmethod
    def time_ends() -> tuple:
        """
        Returns the time tuple of the end of the pairs.
        """
        return "10:10", "12:00", "14:00", "15:50", \
               "17:40", "19:30", "21:10", "22:50"

    @staticmethod
    def time_start_end(number) -> str:
        """
        Returns the time of the pair in the format: "start - end".

        :param number: Pair number
        """
        return "{} - {}".format(TimePair.time_starts()[number],
                                TimePair.time_ends()[number])

    def duration(self):
        return self._duration

    def is_valid(self) -> bool:
        return self._start != "" and self._end != ""

    def __str__(self) -> str:
        return "{} - {}".format(self._start, self._end)
