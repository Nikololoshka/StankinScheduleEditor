# coding: utf-8

# imports
from project.pair import StudentPair, DateItem, DaysOfWeek, SubgroupPairAttrib
from project.util import SortedList
from datetime import timedelta, date
import json


class AlongTwoPairsException(Exception):
    """ Class that describes errors associated with the schedule """
    pass


class ScheduleElement:
    """
    Class describing the element of the day schedule.
    """
    def __init__(self):
        self._buffer = SortedList(ScheduleElement.compare_pairs)
        self._pair_lines = []

    def add_pair(self, new_pair: StudentPair) -> None:
        """
        Adds a pair to a schedule item.

        :param new_pair: Added pair
        """
        self.check_possible_added(new_pair)
        self._buffer.append(new_pair)
        self.reallocate()

    def reallocate(self) -> None:
        """
        Redistributes pairs in an element.
        """
        self._pair_lines.clear()
        for add_pair in self._buffer:
            insert = False
            for line in self._pair_lines:
                pairs = line.get(add_pair["time"].get_number())
                if pairs is not None and pairs[0]["time"].duration() == \
                        add_pair["time"].duration() and self.is_merge(add_pair, pairs):
                    pairs.append(add_pair)
                    insert = True
                    break
                else:
                    free = True
                    for pairs in line.values():
                        if add_pair["time"].intersect(pairs[0]["time"]):
                            free = False
                            break

                    if free:
                        line[add_pair["time"].get_number()] = [add_pair]
                        insert = True
                        break

            if not insert:
                self._pair_lines.append({add_pair["time"].get_number(): [add_pair]})

    @staticmethod
    def is_merge(added_pair: StudentPair, pairs: list) -> bool:
        for pair in pairs:
            if pair["subgroup"].get_subgroup() == added_pair["subgroup"].get_subgroup():
                return True

        return False

    def remove_pair(self, remove_pair: StudentPair) -> None:
        """
        Removes a pair from an element.

        :param remove_pair: Removed pair
        """
        self._buffer.remove(remove_pair)
        self.reallocate()

    def pairs_by_date(self, current_date: date):
        pairs = []

        current_date = DateItem(current_date.strftime("%Y.%m.%d"))
        for pair in self._buffer:
            if current_date in pair["dates"]:
                pairs.append(pair)

        return pairs

    def get_pairs(self, number: int, duration: int, line: int = -1) -> list:
        """
        Returns a list of pairs by their start number and duration.

        :param number: Pair start number
        :param duration: Pair duration
        :return: A list of pairs
        """
        if line != -1 and len(self._pair_lines) != 0:
            pairs = self._pair_lines[line].get(number)
            if pairs is not None and pairs[0]["time"].duration() == duration:
                return pairs

        for line in self._pair_lines:
            pairs = line.get(number)
            if pairs is not None and pairs[0]["time"].duration() == duration:
                return pairs

        return []

    def save(self) -> dict:
        """
        Returns an dict pair generator to save them.
        """
        for pair in self._buffer:
            yield pair.save()

    def rows(self) -> int:
        """
        Number of lines.
        """
        return len(self._pair_lines)

    def check_possible_added(self, added_pair: StudentPair) -> None:
        """
        Checks the ability to add a pair to an element.

        :param added_pair: Added a pair
        """
        for pair in self._buffer:
            if added_pair["time"].intersect(pair["time"]):
                if added_pair["dates"] in pair["dates"]:
                    if not added_pair["subgroup"].is_separate() or \
                            not pair["subgroup"].is_separate():
                        raise AlongTwoPairsException("There can't be two pairs at the same time!\n"
                                                     "{} and {}".format(str(pair),
                                                                        str(added_pair)))

    @staticmethod
    def compare_pairs(pair_1: StudentPair, pair_2: StudentPair) -> bool:
        """
        Comparator for sorting pairs.

        :param pair_1: First pair
        :param pair_2: Second pair
        """
        if pair_1["time"].duration() == pair_2["time"].duration():
            return pair_1["dates"] < pair_2["dates"]

        return pair_1["time"].duration() < pair_2["time"].duration()

    def __iter__(self) -> dict:
        if len(self._pair_lines) == 0:
            yield dict()

        for line in reversed(self._pair_lines):
            yield line


class Schedule:
    """
    Class describing the schedule of pairs
    """
    def __init__(self):
        self._change: bool = False
        self._columns = 8
        self._rows = 6
        self._indexes = []
        for i in range(6):
            self._indexes.append(1)
        self._schedule_list = {
            day: ScheduleElement() for day in DaysOfWeek
        }

    @staticmethod
    def from_xml(path: str):
        """
        Load Schedule from XML file.

        :param path: The path to load the schedule
        :return: Schedule
        """
        sch = Schedule()
        sch.load(path)
        return sch

    def load(self, path: str) -> None:
        """
        Load Schedule from JSON file

        :param path: The path to load the schedule
        """
        with open(path, "r", encoding="utf-8") as file:
            all_pairs = json.load(file)
            for pair in all_pairs:
                added_pair = StudentPair.from_json(pair)
                self.add_pair(added_pair, True)

    def save(self, path: str) -> None:
        """
        Save Schedule to JSON file
        :param path: The path to save the schedule
        """
        with open(path, "w", encoding="utf-8") as file:
            all_pairs = []
            for schedule_element in self._schedule_list.values():
                for pair in schedule_element.save():
                    all_pairs.append(pair)

            json.dump(all_pairs, file, ensure_ascii=False, indent=4)

    def create_week_schedule(self, start_date: date, end_date: date):
        """
        Creates a new schedule with the specified date ranges for the week.

        :param start_date: Start date
        :param end_date: End date
        """
        schedule = Schedule()

        delta = timedelta(days=1)
        while start_date < end_date:
            for schedule_element in self._schedule_list.values():
                pairs = schedule_element.pairs_by_date(start_date)
                for pair in pairs:
                    schedule.add_pair(pair)
                start_date += delta

        return schedule

    def clear(self) -> None:
        """
        Method of cleaning schedules.
        """
        self._change: bool = False
        self._columns = 8
        self._rows = 6
        self._indexes.clear()
        for i in range(6):
            self._indexes.append(1)
        self._schedule_list = {
            day: ScheduleElement() for day in DaysOfWeek
        }

    def is_change(self) -> bool:
        """
        Returns True/False depending on whether there are changes in the schedule
        """
        return self._change

    def normalize_index(self, row: int, column: int, column_number: int) -> tuple:
        """
        Translates the indexes of a pair from the table to the indexes for the schedule.

        :param row: Row index
        :param column: Column index
        :param column_number: Number of columns
        :return: New index tuple: (Day, Number, Duration)
        """
        day, number, duration = row, column, column_number
        for day_number, index in enumerate(self._indexes):
            day -= index
            if day < 0:
                day = day_number
                break

        return day, number, duration

    def pairs_by_index(self, day: int, number: int, duration: int, line: int = -1) -> list:
        """
        Returns a list of pairs in the table by indexes.

        :param day: Number of day
        :param number: Pair start number
        :param duration: Duration
        :return: A list of pairs
        """
        return self._schedule_list[DaysOfWeek.value_of(day)].get_pairs(number, duration, line)

    def add_pair(self, pair: StudentPair, back_mode: bool = False) -> None:
        """
        Adds a student pair to the schedule.

        :param pair: Added pair
        :param back_mode: True - if it returns a pair, on which there were no changes
        """
        week_day = pair["dates"].get_week_day()
        pairs_day = self._schedule_list[week_day]

        pairs_day.add_pair(pair)

        self._indexes[week_day.index_of()] = pairs_day.rows()
        self._rows = sum(self._indexes)

        if not back_mode:
            self._change = True

    def remove_pair(self, pair: StudentPair, back_mode: bool = False) -> None:
        """
        Remove a student pair from schedule.

        :param pair: Removed pair
        :param back_mode: True - if the pair is deleted for editing
        """
        week_day = pair["dates"].get_week_day()
        pairs_day = self._schedule_list[week_day]

        pairs_day.remove_pair(pair)

        self._indexes[week_day.index_of()] = pairs_day.rows()
        self._rows = sum(self._indexes)

        if not back_mode:
            self._change = True

    def columns(self) -> int:
        """
        Number of columns.
        """
        return self._columns

    def rows(self) -> int:
        """
        Number of rows.
        :return:
        """
        return self._rows

    def indexes(self) -> list:
        """
        List of indexes with the distribution of the number of rows per day.
        """
        return self._indexes

    def __iter__(self) -> ScheduleElement:
        for day in self._schedule_list.values():
            yield day
