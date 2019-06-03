# coding: utf-8

# imports
from PyQt5.QtWidgets import QDialog, QWidget, QFormLayout, QLineEdit, QLabel, QCheckBox, \
                            QGroupBox, QDateEdit, QHBoxLayout, QVBoxLayout, QPushButton, \
                            QSizePolicy, QFontComboBox, QComboBox
from PyQt5.QtCore import Qt
from fpdf import FPDF   # PyFPDF2
from project.schedule import Schedule
from datetime import datetime, timedelta
from project.pair import DaysOfWeek, StudentPairAttrib, SubgroupPairAttrib
from project import defaults

# yellow color: 255, 255, 129
# green color: 129, 255, 129


class ExportWindow(QDialog):
    def __init__(self, schedule: Schedule, parent: QWidget = None):
        super().__init__(parent)
        self.schedule_ref = schedule

        # window settings
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setWindowTitle("Export window")
        self.setMinimumWidth(650)

        # title, add_date edit
        self.layout_title_date = QHBoxLayout()

        self.label_title = QLabel("Title")
        self.layout_title_date.addWidget(self.label_title)

        self.line_edit_title = QLineEdit()
        self.layout_title_date.addWidget(self.line_edit_title)

        self.check_box_add_date = QCheckBox("Add date")
        self.layout_title_date.addWidget(self.check_box_add_date)

        # preview
        self.group_box_preview = QGroupBox("Preview")
        self.layout_preview = QHBoxLayout(self.group_box_preview)

        self.label_preview = QLabel("Not work :(")
        self.layout_preview.addWidget(self.label_preview)

        self.group_box_preview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # font edit
        self.group_box_font = QGroupBox("Font settings")
        self.form_layout_font = QFormLayout(self.group_box_font)

        self.label_font = QLabel("Font")
        self.form_layout_font.setWidget(0, QFormLayout.LabelRole, self.label_font)
        self.combo_box_font = QFontComboBox()
        self.form_layout_font.setWidget(0, QFormLayout.FieldRole, self.combo_box_font)

        self.label_encoding = QLabel("Encoding")
        self.form_layout_font.setWidget(1, QFormLayout.LabelRole, self.label_encoding)
        self.combo_box_encoding = QComboBox()
        self.form_layout_font.setWidget(1, QFormLayout.FieldRole, self.combo_box_encoding)

        self.combo_box_font.setMaximumWidth(120)
        self.combo_box_font.setFontFilters(QFontComboBox.ProportionalFonts)

        self.combo_box_encoding.addItem("UTF-8")
        self.combo_box_encoding.addItem("Latin-1")
        self.combo_box_encoding.addItem("Windows-1252")

        # date edit
        self.group_box_date = QGroupBox("Date settings")
        self.form_layout_date = QFormLayout(self.group_box_date)

        self.label_date_start = QLabel("Start")
        self.form_layout_date.setWidget(0, QFormLayout.LabelRole, self.label_date_start)
        self.date_edit_start = QDateEdit()
        self.form_layout_date.setWidget(0, QFormLayout.FieldRole, self.date_edit_start)

        self.label_date_end = QLabel("End")
        self.form_layout_date.setWidget(1, QFormLayout.LabelRole, self.label_date_end)
        self.date_edit_end = QDateEdit()
        self.form_layout_date.setWidget(1, QFormLayout.FieldRole, self.date_edit_end)

        self.date_edit_start.setCalendarPopup(True)
        self.date_edit_end.setCalendarPopup(True)

        # subgroup edit
        self.group_box_subgroup = QGroupBox("Subgroup settings")
        self.form_layout_subgroup = QFormLayout(self.group_box_subgroup)

        self.label_color_a = QLabel("Color A")
        self.form_layout_subgroup.setWidget(0, QFormLayout.LabelRole, self.label_color_a)
        self.combo_box_color_a = QComboBox()
        self.form_layout_subgroup.setWidget(0, QFormLayout.FieldRole, self.combo_box_color_a)

        self.label_color_b = QLabel("Color B")
        self.form_layout_subgroup.setWidget(1, QFormLayout.LabelRole, self.label_color_b)
        self.combo_box_color_b = QComboBox()
        self.form_layout_subgroup.setWidget(1, QFormLayout.FieldRole, self.combo_box_color_b)

        self.label_pattern_a_b = QLabel("Pattern A and B")
        self.form_layout_subgroup.setWidget(2, QFormLayout.LabelRole, self.label_pattern_a_b)
        self.combo_box_pattern_a_b = QComboBox()
        self.form_layout_subgroup.setWidget(2, QFormLayout.FieldRole, self.combo_box_pattern_a_b)

        # navigate buttons
        self.layout_navigate = QHBoxLayout()

        self.layout_navigate.addStretch(1)

        self.push_button_export = QPushButton("Export")
        self.layout_navigate.addWidget(self.push_button_export)

        self.push_button_cancel = QPushButton("Cancel")
        self.layout_navigate.addWidget(self.push_button_cancel)

        # layout setup
        self.layout_right_setting = QVBoxLayout()
        self.layout_right_setting.addWidget(self.group_box_font)
        self.layout_right_setting.addWidget(self.group_box_date)
        self.layout_right_setting.addWidget(self.group_box_subgroup)
        self.layout_right_setting.addStretch(1)

        self.layout_center = QHBoxLayout()
        self.layout_center.addWidget(self.group_box_preview)
        self.layout_center.addLayout(self.layout_right_setting)

        self.layout_main = QVBoxLayout()
        self.layout_main.addLayout(self.layout_title_date)
        self.layout_main.addLayout(self.layout_center)
        self.layout_main.addLayout(self.layout_navigate)

        self.setLayout(self.layout_main)


def export_to_pdf(schedule: Schedule, start_week, end_week):
    pdf = FPDF(orientation="L")
    pdf.add_font('DejaVu', '', './project/pdf_export/DejaVuSansCondensed.ttf', uni=True)
    pdf.set_font('DejaVu', '')

    start = datetime.strptime(start_week, "%Y.%m.%d")
    end = datetime.strptime(end_week, "%Y.%m.%d")
    delta = timedelta(days=1)

    while True:
        pdf.add_page()
        data = [[{"text": "", "subgroup": None} for j in range(8)] for i in range(6)]

        for i in range(6):
            now = start.strftime("%Y.%m.%d")
            for j in range(8):
                pairs = schedule.pairs_by_index(i, j)
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

        pdf.set_font_size(14)
        pdf.cell(w, title, txt="ИДБ-17-09. Зеленый цвет - А подгруппа, желтый цвет - Б подгруппа. "
                               "{}-{}".format((start + timedelta(days=-6)).strftime("%d.%m.%Y"),
                                              start.strftime("%d.%m.%Y")),
                 align="C", border=0)
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
                            pdf.set_fill_color(129, 255, 129)
                            pdf.cell(step_column, step_row, border=1, fill=1)
                        elif data[i - 1][j - 1]["subgroup"].get_subgroup() == SubgroupPairAttrib.B:
                            pdf.set_fill_color(255, 255, 129)
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

        start += delta

        if end <= start:
            print(start.strftime("%Y.%m.%d"))
            break

        print("work...")

    pdf.output("simple.pdf")
    print("Gone!")
