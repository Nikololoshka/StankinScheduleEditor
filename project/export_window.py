# coding: utf-8

# imports
from PyQt5.QtWidgets import QDialog, QWidget, QFormLayout, QLineEdit, QLabel, QCheckBox, \
                            QGroupBox, QDateEdit, QHBoxLayout, QVBoxLayout, QPushButton, \
                            QSizePolicy, QMessageBox, QComboBox, QProgressDialog, \
                            QFileDialog, QColorDialog, qApp
from PyQt5.QtCore import Qt, QStandardPaths, QDate, QFileInfo, QUrl
from PyQt5.QtGui import QColor, QPixmap, QIcon, QDesktopServices
from fpdf import FPDF   # PyFPDF2
from fpdf.ttfonts import TTFontFile

from project.schedule import Schedule
from datetime import timedelta
from project.pair import DaysOfWeek, StudentPairAttrib, SubgroupPairAttrib, DateItem
from project import defaults

import os
import re
import platform

FPDF.FPDF_CACHE_MODE = 1  # no cache


class ExportWindow(QDialog):
    def __init__(self, schedule: Schedule, parent: QWidget = None):
        super().__init__(parent)
        self._schedule_ref = schedule
        self._date_start_cache = None
        self._file = None

        # window settings
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setWindowTitle(self.tr("Export window"))
        self.setMinimumWidth(800)

        # title, add_date edit
        self.layout_title_date = QHBoxLayout()

        self.label_title = QLabel(self.tr("Title"))
        self.layout_title_date.addWidget(self.label_title)

        self.line_edit_title = QLineEdit()
        self.layout_title_date.addWidget(self.line_edit_title)

        self.check_box_add_date = QCheckBox(self.tr("Add date"))
        self.layout_title_date.addWidget(self.check_box_add_date)

        self.line_edit_title.setPlaceholderText(self.tr("My Group. A subgroup - green color, "
                                                        "B subgroup - yellow color. "))
        self.check_box_add_date.setChecked(True)

        # preview
        self.group_box_preview = QGroupBox(self.tr("Preview"))
        self.layout_preview = QHBoxLayout(self.group_box_preview)

        self.label_preview = QLabel(self.tr("Not work :("))
        self.layout_preview.addWidget(self.label_preview)

        self.group_box_preview.setSizePolicy(QSizePolicy.Expanding,
                                             QSizePolicy.Expanding)

        # font edit
        self.group_box_font = QGroupBox(self.tr("Font settings"))
        self.form_layout_font = QFormLayout(self.group_box_font)

        self.label_font = QLabel(self.tr("Font"))
        self.form_layout_font.setWidget(0, QFormLayout.LabelRole, self.label_font)
        self.combo_box_font = QComboBox()
        self.form_layout_font.setWidget(0, QFormLayout.FieldRole, self.combo_box_font)

        self.label_encoding = QLabel(self.tr("Encoding"))
        self.form_layout_font.setWidget(1, QFormLayout.LabelRole, self.label_encoding)
        self.combo_box_encoding = QComboBox()
        self.form_layout_font.setWidget(1, QFormLayout.FieldRole, self.combo_box_encoding)

        for font_name, font_path in self.get_fonts():
            self.combo_box_font.addItem(font_name, font_path)

        self.combo_box_font.setCurrentText(qApp.font().family())
        self.combo_box_font.setEditable(True)

        self.combo_box_encoding.addItem("UTF-8")
        self.combo_box_encoding.addItem("Latin-1")
        self.combo_box_encoding.addItem("Windows-1252")

        # date edit
        self.group_box_date = QGroupBox(self.tr("Date settings"))
        self.form_layout_date = QFormLayout(self.group_box_date)

        self.label_date_start = QLabel(self.tr("Start"))
        self.form_layout_date.setWidget(0, QFormLayout.LabelRole, self.label_date_start)
        self.date_edit_start = QDateEdit()
        self.form_layout_date.setWidget(0, QFormLayout.FieldRole, self.date_edit_start)

        self.label_date_end = QLabel(self.tr("End"))
        self.form_layout_date.setWidget(1, QFormLayout.LabelRole, self.label_date_end)
        self.date_edit_end = QDateEdit()
        self.form_layout_date.setWidget(1, QFormLayout.FieldRole, self.date_edit_end)

        self.date_edit_start.setCalendarPopup(True)
        self.date_edit_end.setCalendarPopup(True)

        if QDate.currentDate().day() < QDate.currentDate().dayOfYear() / 2:
            date = QDate(QDate.currentDate().year(), 2, 1)
        else:
            date = QDate(QDate.currentDate().year(), 9, 1)

        self._date_start_cache = date.addDays(8 - date.dayOfWeek())
        self.date_edit_start.setDate(self._date_start_cache)
        self.date_edit_end.setMinimumDate(self._date_start_cache.addDays(7))
        self.date_edit_end.setDate(self._date_start_cache.addDays(16 * 7))

        # subgroup edit
        self.group_box_subgroup = QGroupBox(self.tr("Subgroup settings"))
        self.form_layout_subgroup = QFormLayout(self.group_box_subgroup)

        self.label_color_a = QLabel(self.tr("Color A"))
        self.form_layout_subgroup.setWidget(0, QFormLayout.LabelRole, self.label_color_a)
        self.combo_box_color_a = QComboBox()
        self.form_layout_subgroup.setWidget(0, QFormLayout.FieldRole, self.combo_box_color_a)

        self.label_color_b = QLabel(self.tr("Color B"))
        self.form_layout_subgroup.setWidget(1, QFormLayout.LabelRole, self.label_color_b)
        self.combo_box_color_b = QComboBox()
        self.form_layout_subgroup.setWidget(1, QFormLayout.FieldRole, self.combo_box_color_b)

        self.label_pattern_a_b = QLabel(self.tr("Pattern A and B"))
        self.form_layout_subgroup.setWidget(2, QFormLayout.LabelRole, self.label_pattern_a_b)
        self.combo_box_pattern_a_b = QComboBox()
        self.form_layout_subgroup.setWidget(2, QFormLayout.FieldRole, self.combo_box_pattern_a_b)

        self.add_standard_colors(self.combo_box_color_a)
        self.add_standard_colors(self.combo_box_color_b)
        self.combo_box_color_a.setCurrentIndex(9)   # lime
        self.combo_box_color_b.setCurrentIndex(15)  # yellow

        self.combo_box_pattern_a_b.addItem("None")
        self.combo_box_pattern_a_b.setEnabled(False)

        # navigate buttons
        self.layout_navigate = QHBoxLayout()

        self.layout_navigate.addStretch(1)

        self.push_button_export = QPushButton(self.tr("Export"))
        self.layout_navigate.addWidget(self.push_button_export)

        self.push_button_cancel = QPushButton(self.tr("Cancel"))
        self.layout_navigate.addWidget(self.push_button_cancel)

        # layout setup
        self.layout_right_setting = QVBoxLayout()
        self.layout_right_setting.addWidget(self.group_box_font)
        self.layout_right_setting.addWidget(self.group_box_date)
        self.layout_right_setting.addWidget(self.group_box_subgroup)
        self.layout_right_setting.addStretch(1)

        self.layout_center = QHBoxLayout()
        self.layout_center.addWidget(self.group_box_preview, 3)
        self.layout_center.addLayout(self.layout_right_setting, 1)

        self.layout_main = QVBoxLayout()
        self.layout_main.addLayout(self.layout_title_date)
        self.layout_main.addLayout(self.layout_center)
        self.layout_main.addLayout(self.layout_navigate)

        self.setLayout(self.layout_main)

        # connection
        self.date_edit_start.dateChanged.connect(self.date_edit_start_changed)
        self.combo_box_color_a.activated.connect(self.combo_box_color_a_clicked)
        self.combo_box_color_b.activated.connect(self.combo_box_color_b_clicked)
        self.push_button_export.clicked.connect(self.export_to_pdf)
        self.push_button_cancel.clicked.connect(self.close)

    def add_standard_colors(self, combo_box: QComboBox) -> None:
        color_items = [
            (self.tr("Custom color"), QColor()),
            (self.tr("Aqua"), QColor(0, 255, 255)),
            (self.tr("Grey"), QColor(128, 128, 128)),
            (self.tr("Navy"), QColor(0, 0, 192)),
            (self.tr("Silver"), QColor(192, 192, 192)),
            (self.tr("Black"), QColor(0, 0, 0)),
            (self.tr("Green"), QColor(0, 128, 0)),
            (self.tr("Olive"), QColor(192, 192, 0)),
            (self.tr("Blue"), QColor(0, 0, 255)),
            (self.tr("Lime"), QColor(0, 255, 0)),
            (self.tr("Purple"), QColor(128, 0, 128)),
            (self.tr("White"), QColor(255, 255, 255)),
            (self.tr("Fuchsia"), QColor(255, 0, 255)),
            (self.tr("Maroon"), QColor(128, 0, 0)),
            (self.tr("Red"), QColor(255, 0, 0)),
            (self.tr("Yellow"), QColor(255, 255, 0))
        ]

        for name, data in color_items:
            combo_box.addItem(self.create_color_icon(data), name, data)

    def export_to_pdf(self) -> None:

        if not self.encoding_test():
            return

        if self._file is None:
            path = QFileDialog.getSaveFileName(self,
                                               self.tr("Export to pdf"),
                                               ".",
                                               "PDF file (*.pdf)")[0]
            if path == "":
                return

            if not path.endswith(".pdf"):
                path += ".pdf"

            self._file = QFileInfo(path)

        weeks = self.date_edit_start.date().daysTo(self.date_edit_end.date()) / 7
        count = 0

        progress = QProgressDialog(self.tr("Export to pdf"),
                                   self.tr("Abort export"), 0, weeks, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(1000)

        pdf = FPDF(orientation="L")

        font_name = self.combo_box_font.currentText()
        font_path = self.combo_box_font.currentData()
        start = self.date_edit_start.date().toPyDate()
        end = self.date_edit_end.date().toPyDate()
        delta = timedelta(days=1)

        encoding = self.combo_box_encoding.currentText()
        if encoding == "UTF-8":
            pdf.add_font(font_name, "", font_path, uni=True)
        else:
            pdf.add_font(font_name, "", font_path)
            pdf.set_doc_option("core_fonts_encoding", encoding)

        pdf.set_font(font_name)

        while True:
            pdf.add_page()
            data = [[{"text": "", "subgroup": None} for j in range(8)] for i in range(6)]

            for i in range(6):
                now = DateItem(start.strftime("%Y.%m.%d"))
                for j in range(8):
                    pairs = self._schedule_ref.pairs_by_index(i, j)
                    for pair in pairs:
                        if now in pair.get_value(StudentPairAttrib.Date):
                            data[i][j]["text"] += str(pair) + "\n"
                            data[i][j]["subgroup"] = pair.get_value(StudentPairAttrib.Subgroup)

                start += delta

            x, y = float(pdf.get_x()), float(pdf.get_y())

            pdf.set_auto_page_break(True, margin=y)

            w = float(pdf.w) - 2 * float(pdf.get_x())
            h = float(pdf.h) - 2 * float(pdf.get_y()) - 6

            title = 10

            title_text = self.line_edit_title.text()
            if self.check_box_add_date.isChecked():
                title_text += " {}-{}".format((start + timedelta(days=-6)).strftime("%d.%m.%Y"),
                                              start.strftime("%d.%m.%Y"))

            pdf.set_font_size(14)
            pdf.cell(w, title, txt=title_text, align="C", border=0)
            h -= title

            first_column, first_row = 4, 4

            step_column = (w - first_row) / 8
            step_row = (h - first_column) / 6

            for i in range(7):
                for j in range(9):
                    if i == 0 and j == 0:
                        pdf.set_xy(x, y + title)
                        pdf.cell(first_column, first_row, border=1)
                    elif i == 0:
                        pdf.set_xy(x + first_row + step_column * (j - 1), y + title)
                        pdf.set_font_size(8)
                        pdf.cell(step_column, first_row, txt=defaults.get_time_start_end(j - 1), align="C", border=1)
                    elif j == 0:
                        pdf.set_xy(x, y + title + first_column + step_row * (i - 1) + step_row)
                        pdf.rotate(90)
                        pdf.set_font_size(8)
                        pdf.cell(step_row, first_row, txt=str(DaysOfWeek.value_of(i - 1)), align="C", border=1)
                        pdf.rotate(0)
                    else:
                        pdf.set_xy(x + first_row + step_column * (j - 1),
                                   y + title + first_column + step_row * (i - 1))

                        if data[i - 1][j - 1]["subgroup"] is not None:
                            if data[i - 1][j - 1]["subgroup"].get_subgroup() == SubgroupPairAttrib.A:
                                color: QColor = self.combo_box_color_a.currentData()
                                pdf.set_fill_color(color.red(), color.green(), color.blue())
                                pdf.cell(step_column, step_row, border=1, fill=1)
                            elif data[i - 1][j - 1]["subgroup"].get_subgroup() == SubgroupPairAttrib.B:
                                color: QColor = self.combo_box_color_b.currentData()
                                pdf.set_fill_color(color.red(), color.green(), color.blue())
                                pdf.cell(step_column, step_row, border=1, fill=1)
                            else:
                                pdf.cell(step_column, step_row, border=1)
                        else:
                            pdf.cell(step_column, step_row, border=1)

                        if data[i - 1][j - 1]["subgroup"] is not None:
                            size = 7
                            offset = 1
                            while size >= 1:
                                pdf.set_font_size(size)
                                lst = pdf.multi_cell(step_column, step_row,
                                                     txt=data[i - 1][j - 1]["text"], align="L", split_only=True)
                                hf = size / 2.8
                                if len(lst) * hf <= step_row - offset * 2:
                                    for k, t in enumerate(lst):
                                        pdf.set_xy(x + first_row + step_column * (j - 1),
                                                   y + title + first_column + step_row * (i - 1) + k * hf + offset)

                                        pdf.cell(step_column, hf, txt=t, align="L")
                                    break
                                size -= 1

            count += 1
            progress.setValue(count)
            if progress.wasCanceled():
                break

            start += delta
            if end <= start:
                break

        pdf.output(self._file.absoluteFilePath())
        progress.setValue(weeks)

        finish_msg_box = QMessageBox(QMessageBox.Information,  self.tr("Export to pdf"),
                                     self.tr("Gone!"))
        open_folder_button = finish_msg_box.addButton(self.tr("Open folder"),
                                                      QMessageBox.ActionRole)
        finish_msg_box.addButton(QMessageBox.Ok)
        finish_msg_box.exec_()

        if finish_msg_box.clickedButton() == open_folder_button:
            QDesktopServices.openUrl(QUrl(self._file.absolutePath()))

    def encoding_test(self) -> bool:
        font_name = self.combo_box_font.currentText()
        font_path = self.combo_box_font.currentData()

        done = False

        try:
            test_pdf = FPDF(orientation="L")
            test_pdf.add_page()

            encoding = self.combo_box_encoding.currentText()
            if encoding == "UTF-8":
                test_pdf.add_font(font_name, "", font_path, uni=True)
            else:
                test_pdf.add_font(font_name, "", font_path)
                test_pdf.set_doc_option("core_fonts_encoding", encoding)

            test_pdf.set_font(font_name)
            test_pdf.cell(100, 100, self.line_edit_title.text())

            done = True
        except Exception as ex:
            QMessageBox.critical(self, self.tr("Encoding error!"), str(ex))

        return done

    def combo_box_color_a_clicked(self) -> None:
        if self.combo_box_color_a.currentIndex() == 0:
            self.custom_color_selected(self.combo_box_color_a)

    def combo_box_color_b_clicked(self) -> None:
        if self.combo_box_color_b.currentIndex() == 0:
            self.custom_color_selected(self.combo_box_color_b)

    def custom_color_selected(self, combo_box: QComboBox) -> None:
        color = QColorDialog.getColor(combo_box.currentData(), self)
        if color.isValid():
            combo_box.setItemIcon(0, self.create_color_icon(color))
            combo_box.setItemData(0, color)

    def date_edit_start_changed(self, date: QDate):
        end_date = self.date_edit_end.date().addDays(self._date_start_cache.daysTo(date))
        self.date_edit_end.setMinimumDate(date.addDays(7))
        self.date_edit_end.setDate(end_date)
        self._date_start_cache = QDate(date)

    @staticmethod
    def create_color_icon(color: QColor) -> QIcon:
        pix_map = QPixmap(32, 32)
        pix_map.fill(color)
        icon = QIcon(pix_map)
        return icon

    def get_fonts(self) -> list:
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

        max_progress = len(paths)
        progress_load_font = QProgressDialog(self.tr("Font loading"),
                                             self.tr("Cancel loading"),
                                             0, max_progress, self.parentWidget())
        # progress_load_font.setWindowModality(Qt.WindowModal)
        progress_load_font.setMinimumDuration(1000)

        for i, path in enumerate(paths):
            progress_load_font.setValue(i)
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

        progress_load_font.setValue(max_progress)
        fonts = sorted(fonts.items())
        return fonts
