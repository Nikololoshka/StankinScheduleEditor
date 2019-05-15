# coding: utf-8

# imports
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from schedule import Schedule
from pair import StudentPair, StudentPairAttrib, TypePairAttrib, \
                 SubgroupPairAttrib, TimePair
import defaults


class PairCreatorWindow(QDialog):

    pairChanged = pyqtSignal()

    def __init__(self, scheduler_ref: Schedule, index: QModelIndex, edit_pair: StudentPair, parent: QWidget = None):
        super().__init__(parent)

        self.scheduler_ref: Schedule = scheduler_ref
        self.index: QModelIndex = index
        self.edit_pair: StudentPair = edit_pair

        # window settings
        self.setWindowTitle("Creator")
        self.setMinimumSize(640, 350)
        self.resize(800, 400)

        # general settings window
        self.form_layout_general = QFormLayout()

        # title
        self.label_title = QLabel("Title", self)
        self.form_layout_general.setWidget(0, QFormLayout.LabelRole, self.label_title)
        self.line_edit_title = QLineEdit(str(self.edit_pair.get_value(StudentPairAttrib.Title)), self)
        self.form_layout_general.setWidget(0, QFormLayout.FieldRole, self.line_edit_title)

        # lecturer
        self.label_lecturer = QLabel("Lecturer", self)
        self.form_layout_general.setWidget(1, QFormLayout.LabelRole, self.label_lecturer)
        self.line_edit_lecturer = QLineEdit(str(self.edit_pair.get_value(StudentPairAttrib.Lecturer)), self)
        self.form_layout_general.setWidget(1, QFormLayout.FieldRole, self.line_edit_lecturer)

        self.completer = QCompleter(defaults.get_lecturers(), self)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchContains)
        self.line_edit_lecturer.setCompleter(self.completer)

        # type
        self.label_type = QLabel("Type", self)
        self.form_layout_general.setWidget(2, QFormLayout.LabelRole, self.label_type)
        self.combo_box_type = QComboBox(self)
        self.form_layout_general.setWidget(2, QFormLayout.FieldRole, self.combo_box_type)

        for name, attrib in TypePairAttrib.items():
            self.combo_box_type.addItem(name, attrib)

        self.combo_box_type.setCurrentText(str(self.edit_pair.get_value(StudentPairAttrib.Type)))

        # classes
        self.label_classes = QLabel("Classes", self)
        self.form_layout_general.setWidget(3, QFormLayout.LabelRole, self.label_classes)
        self.line_edit_classes = QLineEdit(str(self.edit_pair.get_value(StudentPairAttrib.Classroom)), self)
        self.form_layout_general.setWidget(3, QFormLayout.FieldRole, self.line_edit_classes)

        # subgroup
        self.label_subgroup = QLabel("Subgroup", self)
        self.form_layout_general.setWidget(4, QFormLayout.LabelRole, self.label_subgroup)
        self.combo_box_subgroup = QComboBox(self)
        self.form_layout_general.setWidget(4, QFormLayout.FieldRole, self.combo_box_subgroup)

        for name, attrib in SubgroupPairAttrib.items():
            self.combo_box_subgroup.addItem(name, attrib)

        self.combo_box_subgroup.setCurrentText(str(self.edit_pair.get_value(StudentPairAttrib.Subgroup)))

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

        time: TimePair = self.edit_pair.get_value(StudentPairAttrib.Time)
        if time is not None:
            number = time.get_number()
            self.combo_box_start.setCurrentIndex(number)
            self.combo_box_end.setCurrentIndex(number)
            self.time = time

        # date setting
        self.group_box_date = QGroupBox("Date", self)
        self.horizontal_layout_right = QHBoxLayout(self.group_box_date)

        self.list_widget_date = QListWidget(self.group_box_date)
        self.horizontal_layout_right.addWidget(self.list_widget_date)

        self.vertical_layout_right = QVBoxLayout()
        self.horizontal_layout_right.addLayout(self.vertical_layout_right)

        self.push_button_add_date = QPushButton("Add", self)
        self.vertical_layout_right.addWidget(self.push_button_add_date)

        self.push_button_edit_date = QPushButton("Edit", self)
        self.vertical_layout_right.addWidget(self.push_button_edit_date)

        self.push_button_remove_date = QPushButton("Remove", self)
        self.vertical_layout_right.addWidget(self.push_button_remove_date)

        self.vertical_layout_right.addStretch(1)

        for date in str(self.edit_pair.get_value(StudentPairAttrib.Date)).split(","):
            self.list_widget_date.addItem(date.strip())

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

    def save(self) -> bool:
        title = self.line_edit_title.text()
        if title == "":
            QMessageBox.information(self, "Information", "Title field is empty")
            return False

        lecturer = self.line_edit_lecturer.text()
        if lecturer == "":
            QMessageBox.information(self, "Information", "Lecturer field is empty")
            return False

        classes = self.line_edit_classes.text()
        if classes == "":
            QMessageBox.information(self, "Information", "Classes field is empty")
            return False

        pair_type = self.combo_box_type.currentData(Qt.UserRole)
        subgroup = self.combo_box_subgroup.currentData(Qt.UserRole)

        start_time = self.combo_box_start.currentText()
        end_time = self.combo_box_end.currentText()

        self.edit_pair.get_value(StudentPairAttrib.Title).set_title(title)
        self.edit_pair.get_value(StudentPairAttrib.Lecturer).set_lecturer(lecturer)
        self.edit_pair.get_value(StudentPairAttrib.Type).set_type(pair_type)
        self.edit_pair.get_value(StudentPairAttrib.Classroom).set_classroom(classes)
        self.edit_pair.get_value(StudentPairAttrib.Subgroup).set_subgroup(subgroup)
        self.edit_pair.get_value(StudentPairAttrib.Time).set_time(start_time, end_time)

        return True

    def push_button_ok_clicked(self):
        if self.save():
            self.close()

    def combo_box_start_changed(self, index):
        self.combo_box_end.setCurrentIndex(index)
