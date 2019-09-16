# coding: utf-8

# imports
from PyQt5.QtCore import QFileInfo

from project.pair import StudentPair, TimePair, DateItem, DateRange, \
                         TypePairAttrib, SubgroupPairAttrib, FrequencyDate, InvalidDatePair
from project.exports.export_logic import export_weeks_to_pdf, export_full_to_pdf
from project.imports.tesseract_wrapper import TesseractWrapper
from .confuse_window import ConfuseWindow
from project.schedule import Schedule

import pdf2image
import numpy as np
import cv2 as cv

import re
import time
import difflib
import traceback
from datetime import datetime
from multiprocessing import Queue, Manager


class ImportManager:
    def __init__(self, size=2):
        # shared data
        self.weekly = False
        self.full = False
        self.debug_image = False
        self.dpi = 500
        self.tesseract_path = "tesseract"
        self.poppler_path = None
        self.font_name = ""
        self.font_path = ""
        self.encoding = ""
        self.start = None
        self.end = None
        self.color_a = None
        self.color_b = None

        self.titles_list = []
        self.lecturers_list = []
        self.classrooms_list = []

        self.classrooms_translate = {}

        with open("res/titles.txt", "r", encoding="utf-8") as file:
            for line in file:
                self.titles_list.append(line.strip())

        with open("res/lecturers.txt", "r", encoding="utf-8") as file:
            for line in file:
                self.lecturers_list.append(line.strip())

        with open("res/classrooms.txt", "r", encoding="utf-8") as file:
            for line in file:
                self.classrooms_list.append(line.strip())

        with open("res/classrooms-translate.txt", "r", encoding="utf-8") as file:
            for line in file:
                lst = line.split("->")
                self.classrooms_translate[lst[0].strip()] = lst[1].strip()

        mp = Manager()

        self.queue = Queue()
        self.progress_value_list = mp.list([0] * size)
        self.progress_text_list = mp.list([""] * size)
        self.confuse_info = mp.list([""] * size)
        self.confuse_file_path = mp.list([""] * size)
        self.confuse_list = mp.list([""] * size)
        self.confuse_answer_list = mp.list([ConfuseWindow.Nothing] * size)
        self.flags = mp.dict({"stop": False})


class ConfuseSituationException(Exception):
    def __init__(self, filename="", cell="", context="",
                 maybe_answer="", confuse_type="", confuse=""):
        self.filename = filename
        self.cell = cell
        self.context = context
        self.maybe_answer = maybe_answer
        self.confuse_type = confuse_type
        self.confuse = confuse

    def __str__(self):
        return f"Filename: {self.filename} \n" \
               f"Cell: {self.cell} \n\n" \
               f"Type: {self.confuse_type} \n\n"    \
               f"Context: {self.context}   \n\n"    \
               f"Maybe answer: {self.maybe_answer} \n\n" \
               f"Confuse: {self.confuse}"


class PairParser:
    # ([а-яА-Яa-zA-Z0-9\s\,\-\(\)\/\:]+?\.)\s?([а-яА-Я\_]+\s([а-яА-я]\.?){1,2})?\s?([а-яА-я\s]+?\.)\s?(\([абАБ]\)\.)?\s?([^\[\]]+?\.)\s?(\[((\,)|(\s?(\d{2}\.\d{2})\-(\d{2}\.\d{2})\s*?([чк]\.[н]\.)|(\s?(\d{2}\.\d{2}))))+\])
    Pattern_title = r"([а-яА-Яa-zA-Z0-9\s\,\-\(\)\/\:]+?\.)"# 0
    Pattern_lecturer = r"([а-яА-Я\_]+\s([а-яА-я]\.?){1,2})?"  # 1
    Pattern_type = r"([а-яА-я\s]+?\.)"                      # 3
    Pattern_subgroup = r"(\([абАБ]\)\.)?"                   # 4
    Pattern_classroom = r"([^\[\]]+?\.)"                    # 5
    Pattern_date = r"(\[((\,)|(\s?(\d{2}\.\d{2})\-(\d{2}\.\d{2})\s*?([чкЧК]\.[нН]\.{1,2})|(\s?(\d{2}\.\d{2}))))+\])"                             # 6

    Pattern = r"\s?".join([Pattern_title,
                           Pattern_lecturer,
                           Pattern_type,
                           Pattern_subgroup,
                           Pattern_classroom,
                           Pattern_date])


def import_from_pdf(process_id, manager: ImportManager) -> None:
    tesseract = TesseractWrapper(tesseract_path=manager.tesseract_path)
    while not manager.queue.empty():
        try:
            file_path = manager.queue.get(True, 1)
            file = QFileInfo(file_path)

            # convert from pdf to PIL image
            img_pdf = pdf2image.convert_from_path(file.absoluteFilePath(),
                                                  dpi=manager.dpi,
                                                  poppler_path=manager.poppler_path)
            img_pdf = img_pdf[0].convert('RGB')

            # convert to NumPy array
            img = np.array(img_pdf)
            img = img[:, :, ::-1].copy()

            # set mask
            grey = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
            thresh = cv.threshold(grey, 127, 255, 0)[1]

            if manager.flags["stop"]:
                break

            # found contours
            contours = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)[0]

            height, width = img.shape[:2]
            # max and min area of rect
            max_area = height * width / 20
            min_area = max_area / 40

            cells = []
            time_cells = dict()

            contours_number = len(contours)
            number = 0

            for k, contour in enumerate(contours, 1):
                rect = cv.minAreaRect(contour)
                area = int(rect[1][0] * rect[1][1])
                if min_area < area < max_area:
                    if manager.flags["stop"]:
                        break

                    x, y, w, h = cv.boundingRect(contour)
                    crop_img = img[int(y):int(y + h), int(x):int(x + w)]

                    txt = tesseract.to_string(crop_img)

                    found = False
                    for i in range(8):
                        if TimePair.time_starts()[i] in txt and TimePair.time_ends()[i]:
                            time_cells[i] = (x, x + w)
                            found = True
                            break

                    if not found:
                        cells.append((x, x + w, " ".join(txt.split())))

                    # draw debug rect with number
                    if manager.debug_image:
                        box = cv.boxPoints(rect)
                        box = np.int0(box)
                        blue_color = (255, 0, 0)
                        center = (int(rect[0][0]), int(rect[0][1]))

                        cv.drawContours(img, [box], 0, blue_color, 2)
                        cv.putText(img, str(number), (center[0] - 100, center[1] - 40),
                                   cv.FONT_HERSHEY_SIMPLEX, 3, blue_color, 12)

                    number += 1
                    process = int(k / contours_number * 70)
                    manager.progress_value_list[process_id] = process
                    manager.progress_text_list[process_id] = "{} {}%".format(file.baseName(),
                                                                             process)
            if manager.debug_image:
                cv.imwrite(file_path[0:-4] + "-debug.jpg", img)

            if manager.flags["stop"]:
                break

            schedule = Schedule()
            cells_number = len(cells)

            for k, cell in enumerate(cells):
                if manager.flags["stop"]:
                    break

                start_x, end_x, text = cell
                first_start_time, first_end_time = time_cells[0]

                if not abs(end_x - first_start_time) < abs(start_x - first_start_time):
                    text = "\n".join(re.findall(r".*?\]", text))
                    while True:
                        try:
                            pairs = parse_pair(manager, text)
                            break
                        except InvalidDatePair as ex:
                            text = confuse_loop(process_id, manager,
                                                ConfuseSituationException(file.absoluteFilePath(),
                                                                          text,
                                                                          confuse=str(ex)))
                        except ConfuseSituationException as ex:
                            ex.filename = file.absoluteFilePath()[0:-4] + "-debug.jpg"
                            ex.cell = k
                            ex.context = text
                            if ex.maybe_answer == "":
                                ex.maybe_answer = text

                            text = confuse_loop(process_id, manager, ex)

                    if len(pairs) != 0:
                        diff_start = abs(start_x - first_start_time)
                        diff_end = abs(end_x - first_end_time)
                        start, end = 0, 0

                        for number, (start_time, end_time) in time_cells.items():
                            diff = abs(start_x - start_time)
                            if diff < diff_start:
                                diff_start = diff
                                start = number

                            diff = abs(end_x - end_time)
                            if diff < diff_end:
                                diff_end = diff
                                end = number

                        for pair in pairs:
                            pair["time"].set_time(TimePair.time_starts()[start],
                                                  TimePair.time_ends()[end])
                            schedule.add_pair(pair)

                    process = int(70 + k / cells_number * 30)
                    manager.progress_value_list[process_id] = process
                    manager.progress_text_list[process_id] = "{} {}%".format(file.baseName(),
                                                                             process)

            schedule.save(file.absoluteFilePath()[0:-4] + ".json")
            print(file.absoluteFilePath()[0:-4] + ".json")

            if manager.flags["stop"]:
                break

            if manager.weekly:
                export_weeks_to_pdf(schedule,
                                    file.baseName(),
                                    True,
                                    file.absoluteFilePath()[0:-4] + "-weekly.pdf",
                                    manager.font_name,
                                    manager.font_path,
                                    manager.encoding,
                                    manager.start,
                                    manager.end,
                                    manager.color_a,
                                    manager.color_b)

            if manager.full:
                export_full_to_pdf(schedule,
                                   file.baseName(),
                                   file.absoluteFilePath()[0:-4] + "-full.pdf",
                                   manager.font_name,
                                   manager.font_path,
                                   manager.encoding)

        except Exception as ex:
            print("Exception, process:", process_id, "is:", ex)
            traceback.print_exc()

    manager.progress_value_list[process_id] = 100
    manager.progress_text_list[process_id] = "Work complete"


def parse_pair(manager, text):
    text_pairs = re.findall(r".*?\]", text)
    pairs = []
    for text_pair in text_pairs:
        match = re.fullmatch(PairParser.Pattern, text_pair)
        if match is not None:
            pair = StudentPair()

            pair["title"].set_title(parse_title(match.group(1), manager, text))
            pair["lecturer"].set_lecturer(parse_lecturer(match.group(2), manager, text))
            pair["type"].set_type(parse_type(match.group(4)))
            pair["subgroup"].set_subgroup(parse_subgroup(match.group(5)))
            pair["classroom"].set_classroom(parse_classroom(match.group(6), manager, text))
            for date in parse_date(match.group(7)):
                pair["dates"].add_date(date)

            pairs.append(pair)
        else:
            ex = ConfuseSituationException()
            ex.confuse_type = "Pair parse"
            ex.confuse = "not found"
            raise ex

    return pairs


def parse_title(title_str, manager: ImportManager, text):
    title_str = title_str[0:-1].strip()

    score = -1
    maybe = "not find"
    for element in manager.titles_list:
        seq = difflib.SequenceMatcher(None, title_str, element)
        if seq.ratio() > score:
            score = seq.ratio()
            maybe = element

    if score < 0.95:
        print(title_str)
        ex = ConfuseSituationException()
        ex.confuse = title_str
        ex.confuse_type = "Invalid title"
        ex.maybe_answer = text.replace(title_str, maybe)
        raise ex

    return maybe


def parse_lecturer(lecturer_str, manager: ImportManager, text):
    if lecturer_str is not None:
        lecturer_str = lecturer_str[0:-1].strip()

        score = -1
        maybe = "not find"
        for element in manager.lecturers_list:
            seq = difflib.SequenceMatcher(None, lecturer_str, element)
            if seq.ratio() > score:
                score = seq.ratio()
                maybe = element

        if score < 0.95:
            ex = ConfuseSituationException()
            ex.confuse = lecturer_str
            ex.confuse_type = "Invalid lecturer"
            ex.maybe_answer = text.replace(lecturer_str, maybe)
            raise ex

        return maybe
    else:
        return ""


def parse_type(type_str):
    type_str = type_str[0:-1].strip().lower()

    if type_str == "семинар":
        return TypePairAttrib.Seminar
    elif type_str == "лекции":
        return TypePairAttrib.Lecture
    elif type_str == "лабораторные занятия":
        return TypePairAttrib.Laboratory

    ex = ConfuseSituationException()
    ex.confuse_type = "Type pair"
    ex.confuse = type_str
    raise ex


def parse_subgroup(subgroup_str):
    if subgroup_str is None:
        return SubgroupPairAttrib.Common
    elif subgroup_str[0:-1].upper() == "(А)":
        return SubgroupPairAttrib.A
    elif subgroup_str[0:-1].upper() == "(Б)":
        return SubgroupPairAttrib.B

    ex = ConfuseSituationException()
    ex.confuse_type = "Subgroup pair"
    ex.confuse = subgroup_str
    raise ex


def parse_classroom(classroom_str, manager: ImportManager, text):
    if classroom_str is not None:
        classroom_str = classroom_str[0:-1].strip()

        if classroom_str == "":
            return ""

        if classroom_str in manager.classrooms_translate:
            return manager.classrooms_translate[classroom_str]

        score = -1
        maybe = "not find"
        for element in manager.classrooms_list:
            seq = difflib.SequenceMatcher(None, classroom_str, element)
            if seq.ratio() > score:
                score = seq.ratio()
                maybe = element

        if score < 0.975:
            ex = ConfuseSituationException()
            ex.confuse = classroom_str
            ex.confuse_type = "Invalid classroom"
            ex.maybe_answer = text.replace(classroom_str, maybe)
            raise ex

        return maybe
    else:
        return ""


def parse_date(date_str):
    dates = []

    text_dates = date_str.replace("[", "").replace("]", "").strip().lower().split(",")

    for text_date in text_dates:
        # find data range
        match = re.match(r"\s?(\d{2}\.\d{2})-(\d{2}\.\d{2})\s*?([чк]\.[н]\.)", text_date)
        if match is not None:
            freq = match.group(3)

            if freq == "к.н.":
                freq = FrequencyDate.Every
            elif freq == "ч.н.":
                freq = FrequencyDate.Throughout
            else:
                ex = ConfuseSituationException()
                ex.confuse_type = "Date frequency"
                ex.confuse = match.string
                raise ex

            dates.append(DateRange(convert_date(match.group(1)),
                                   convert_date(match.group(2)),
                                   freq))
            continue

        # find data item
        match = re.match(r"\s?(\d{2}\.\d{2})", text_date)
        if match is not None:
            dates.append(DateItem(convert_date(match.group(1))))
            continue

        ex = ConfuseSituationException()
        ex.confuse_type = "Date pair"
        ex.confuse = date_str
        raise ex

    return dates


def convert_date(old_date):
    return datetime.strptime(old_date, "%d.%m") \
        .replace(datetime.today().year).strftime("%Y.%m.%d")


def confuse_loop(process_id, manager: ImportManager, ex: ConfuseSituationException):
    manager.confuse_info[process_id] = str(ex)
    manager.confuse_file_path[process_id] = ex.filename
    manager.confuse_list[process_id] = ex.maybe_answer
    manager.confuse_answer_list[process_id] = ConfuseWindow.NeededSolution

    while True:
        if manager.confuse_answer_list[process_id] == ConfuseWindow.Solved:
            manager.confuse_answer_list[process_id] = ConfuseWindow.Nothing
            return manager.confuse_list[process_id]
        else:
            time.sleep(1)
