# coding: utf-8

# imports
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from schedule import Schedule
from student_pair import StudentPair
from time_pair import TimePair
from date_pair import DatePair, DateItem, DateRange
import defaults


class PairCreatorWindow(QDialog):
    def __init__(self, scheduler_ref: Schedule, index: QModelIndex, edit_pair: StudentPair, parent: QWidget = None):
        super().__init__(parent)

        self.scheduler_ref = scheduler_ref
        self.index = index
        self.edit_pair = edit_pair
        self.change = False

        # window settings
        self.setWindowTitle("Creator")
        self.resize(640, 350)

        # general settings window
        self.form_layout_general = QFormLayout()

        # title
        self.label_title = QLabel("Title", self)
        self.form_layout_general.setWidget(0, QFormLayout.LabelRole, self.label_title)
        self.line_edit_title = QLineEdit(self.edit_pair.get_value("title"), self)
        self.form_layout_general.setWidget(0, QFormLayout.FieldRole, self.line_edit_title)

        # lecturer
        self.label_lecturer = QLabel("Lecturer", self)
        self.form_layout_general.setWidget(1, QFormLayout.LabelRole, self.label_lecturer)
        self.line_edit_lecturer = QLineEdit(self.edit_pair.get_value("lecturer"), self)
        self.form_layout_general.setWidget(1, QFormLayout.FieldRole, self.line_edit_lecturer)

        # type
        self.label_type = QLabel("Type", self)
        self.form_layout_general.setWidget(2, QFormLayout.LabelRole, self.label_type)
        self.line_edit_type = QLineEdit(self.edit_pair.get_value("type"), self)
        self.form_layout_general.setWidget(2, QFormLayout.FieldRole, self.line_edit_type)

        # classes
        self.label_classes = QLabel("Classes", self)
        self.form_layout_general.setWidget(3, QFormLayout.LabelRole, self.label_classes)
        self.line_edit_classes = QLineEdit(self.edit_pair.get_value("classroom"), self)
        self.form_layout_general.setWidget(3, QFormLayout.FieldRole, self.line_edit_classes)

        # subgroup
        self.label_subgroup = QLabel("Subgroup", self)
        self.form_layout_general.setWidget(4, QFormLayout.LabelRole, self.label_subgroup)
        self.line_edit_subgroup = QLineEdit(self.edit_pair.get_value("subgroup"), self)
        self.form_layout_general.setWidget(4, QFormLayout.FieldRole, self.line_edit_subgroup)

        # time setting
        self.group_box_time = QGroupBox("Time", self)
        self.form_layout_time = QFormLayout(self.group_box_time)

        self.label_start = QLabel("Start", self.group_box_time)
        self.form_layout_time.setWidget(0, QFormLayout.LabelRole, self.label_start)
        self.combo_box_start = QComboBox(self.group_box_time)
        self.form_layout_time.setWidget(0, QFormLayout.FieldRole, self.combo_box_start)

        self.label_end = QLabel("End", self.group_box_time)
        self.form_layout_time.setWidget(1, QFormLayout.LabelRole, self.label_end)
        self.combo_box_end = QComboBox(self.group_box_time)
        self.form_layout_time.setWidget(1, QFormLayout.FieldRole, self.combo_box_end)

        self.combo_box_start.addItems(defaults.get_time_start())
        self.combo_box_end.addItems(defaults.get_time_end())
        self.combo_box_end.setEnabled(False)

        time: TimePair = self.edit_pair.get_value("time")
        if time is not None:
            number = time.get_number()
            self.combo_box_start.setCurrentIndex(number)
            self.combo_box_end.setCurrentIndex(number)

        # date setting
        self.group_box_date = QGroupBox("Date", self)
        self.form_layout_date = QFormLayout(self.group_box_date)

        self.label_edit_date = QLabel("Input date", self.group_box_date)
        self.form_layout_date.setWidget(0, QFormLayout.LabelRole, self.label_edit_date)
        self.line_edit_date = QLineEdit(self)
        self.form_layout_date.setWidget(0, QFormLayout.FieldRole, self.line_edit_date)

        self.label_parse_date = QLabel("Parse date", self.group_box_date)
        self.form_layout_date.setWidget(1, QFormLayout.LabelRole, self.label_parse_date)
        self.label_result_date = QLabel(self)
        self.form_layout_date.setWidget(1, QFormLayout.FieldRole, self.label_result_date)

        self.line_edit_date.setEnabled(False)

        dates: DatePair = self.edit_pair.get_value("dates")
        if dates is not None:
            self.label_result_date.setText(str(dates))

        # navigate
        self.horizontal_layout_down = QHBoxLayout()

        self.horizontal_layout_down.addStretch(1)

        self.push_button_ok = QPushButton("OK", self)
        self.horizontal_layout_down.addWidget(self.push_button_ok)

        self.push_button_cancel = QPushButton("Cancel", self)
        self.horizontal_layout_down.addWidget(self.push_button_cancel)

        # layout settings
        self.vertical_layout_left = QVBoxLayout()
        self.vertical_layout_left.addLayout(self.form_layout_general)
        self.vertical_layout_left.addWidget(self.group_box_time)

        self.horizontal_layout_up = QHBoxLayout()
        self.horizontal_layout_up.addLayout(self.vertical_layout_left)
        self.horizontal_layout_up.addWidget(self.group_box_date)

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.horizontal_layout_up)
        self.main_layout.addLayout(self.horizontal_layout_down)

        self.setLayout(self.main_layout)

        # connection
        self.combo_box_start.currentIndexChanged.connect(self.combo_box_start_changed)
        self.push_button_ok.clicked.connect(self.push_button_ok_clicked)
        self.push_button_cancel.clicked.connect(self.close)

    def has_change(self) -> bool:
        return self.change

    def save(self):
        self.edit_pair.update("title", self.line_edit_title.text())
        self.edit_pair.update("lecturer", self.line_edit_lecturer.text())
        self.edit_pair.update("type", self.line_edit_type.text())
        self.edit_pair.update("subgroup", self.line_edit_subgroup.text())
        self.edit_pair.update("classroom", self.line_edit_classes.text())
        self.edit_pair.update("time", TimePair(self.combo_box_start.currentText(),
                                               self.combo_box_end.currentText()))

        self.change = True

    def push_button_ok_clicked(self):
        self.save()
        self.close()

    def combo_box_start_changed(self, index):
        self.combo_box_end.setCurrentIndex(index)