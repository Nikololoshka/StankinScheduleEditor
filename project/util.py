# coding: utf-8

# imports
from PyQt5.QtCore import QStandardPaths
from PyQt5.QtGui import QIcon, QPixmap, QColor

from fpdf.ttfonts import TTFontFile

import os
import re
import platform


def get_fonts() -> list:
    """
    Returns a list of tuples (font, path) of all fonts installed on the system.
    """
    paths = []

    for path in QStandardPaths.standardLocations(QStandardPaths.FontsLocation):
        if os.path.isdir(path):
            paths.append(path)

    if platform.system() == "Linux":
        unix_paths = QStandardPaths.standardLocations(QStandardPaths.AppDataLocation)
        for path in unix_paths:
            possible_path = os.path.dirname(path) + os.sep + "fonts"
            if os.path.isdir(possible_path):
                paths.append(possible_path)

    fonts = dict()

    for i, path in enumerate(paths):
        for dir_path, dir_names, file_names in os.walk(path):
            for filename in file_names:
                if filename.endswith(".ttf"):
                    try:
                        absolute_file_path = dir_path + os.sep + filename

                        ttf = TTFontFile()
                        ttf.getMetrics(absolute_file_path)
                        font_name = ttf.fullName.replace("-", " ")
                        font_name = " ".join(re.findall(r"[A-Z]?[^A-Z\s]+|[A-Z]+", font_name))

                        if font_name not in fonts:
                            fonts[font_name] = absolute_file_path

                    except RuntimeError:
                        pass

    fonts = sorted(fonts.items())
    return fonts


def create_color_icon(color: QColor) -> QIcon:
    """
    Creates an icon with the specified color.

    :param color: Icon color
    :return: QIcon object
    """
    pix_map = QPixmap(32, 32)
    pix_map.fill(color)
    icon = QIcon(pix_map)
    return icon


class SortedList(list):
    """
    Class describing the sorted list with the ability to install the comparator.
    """
    def __init__(self, cmp_function):
        super().__init__()
        self._cmp = cmp_function

    def append(self, x):
        i = 0
        while i < len(self):
            if not self._cmp(self[i], x):
                break
            i += 1

        self.insert(i, x)
