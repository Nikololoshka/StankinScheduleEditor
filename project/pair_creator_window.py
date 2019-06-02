# coding: utf-8

# imports
from PyQt5.QtWidgets import QDialog, QWidget, QFormLayout, QLineEdit, QLabel, QCompleter, \
                            QGroupBox, QListWidget, QHBoxLayout, QVBoxLayout, QPushButton, \
                            QMessageBox, QListWidgetItem, QComboBox
from PyQt5.QtCore import QModelIndex, Qt
from project.schedule import Schedule
from project.pair import StudentPair, StudentPairAttrib, TypePairAttrib, \
                         SubgroupPairAttrib, TimePair, InvalidDatePair
from project.date_creator_window import DateCreatorWindow
from project import defaults
import copy


class PairCreatorWindow(QDialog):
    """ Dialog window for creating a student pair """
    def __init__(self, scheduler_ref: Schedule, index: QModelIndex, parent: QWidget = None):
        super().__init__(parent)

        self._scheduler_ref: Schedule = scheduler_ref
        self._index: QModelIndex = index
        self._edit_pair = StudentPair()

        # window settings
        self.setWindowTitle("Creator")
        self.setMinimumSize(640, 350)
        self.resize(800, 400)

        # general settings window
        self.group_box_general = QGroupBox(self.tr("General"), self)
        self.form_layout_general = QFormLayout(self.group_box_general)

        # title
        self.label_title = QLabel(self.tr("Title"), self)
        self.form_layout_general.setWidget(0, QFormLayout.LabelRole, self.label_title)
        self.line_edit_title = QLineEdit("", self)
        self.form_layout_general.setWidget(0, QFormLayout.FieldRole, self.line_edit_title)

        # lecturer
        self.label_lecturer = QLabel(self.tr("Lecturer"), self)
        self.form_layout_general.setWidget(1, QFormLayout.LabelRole, self.label_lecturer)
        self.line_edit_lecturer = QLineEdit("", self)
        self.form_layout_general.setWidget(1, QFormLayout.FieldRole, self.line_edit_lecturer)

        self.completer = QCompleter(defaults.get_lecturers(), self)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchContains)
        self.line_edit_lecturer.setCompleter(self.completer)

        # type
        self.label_type = QLabel(self.tr("Type"), self)
        self.form_layout_general.setWidget(2, QFormLayout.LabelRole, self.label_type)
        self.combo_box_type = QComboBox(self)
        self.form_layout_general.setWidget(2, QFormLayout.FieldRole, self.combo_box_type)

        for name, attrib in TypePairAttrib.items():
            self.combo_box_type.addItem(name, attrib)

        # classes
        self.label_classes = QLabel(self.tr("Classes"), self)
        self.form_layout_general.setWidget(3, QFormLayout.LabelRole, self.label_classes)
        self.line_edit_classes = QLineEdit("", self)
        self.form_layout_general.setWidget(3, QFormLayout.FieldRole, self.line_edit_classes)

        # subgroup
        self.label_subgroup = QLabel(self.tr("Subgroup"), self)
        self.form_layout_general.setWidget(4, QFormLayout.LabelRole, self.label_subgroup)
        self.combo_box_subgroup = QComboBox(self)
        self.form_layout_general.setWidget(4, QFormLayout.FieldRole, self.combo_box_subgroup)

        for name, attrib in SubgroupPairAttrib.items():
            self.combo_box_subgroup.addItem(name, attrib)

        # time setting
        self.group_box_time = QGroupBox(self.tr("Time"), self)
        self.form_layout_time = QFormLayout(self.group_box_time)

        self.label_start = QLabel(self.tr("Start"), self.group_box_time)
        self.form_layout_time.setWidget(0, QFormLayout.LabelRole, self.label_start)
        self.combo_box_start = QComboBox(self.group_box_time)
        self.form_layout_time.setWidget(0, QFormLayout.FieldRole, self.combo_box_start)

        self.label_end = QLabel(self.tr("End"), self.group_box_time)
        self.form_layout_time.setWidget(1, QFormLayout.LabelRole, self.label_end)
        self.combo_box_end = QComboBox(self.group_box_time)
        self.form_layout_time.setWidget(1, QFormLayout.FieldRole, self.combo_box_end)

        self.combo_box_start.addItems(defaults.get_time_start())
        self.combo_box_end.addItems(defaults.get_time_end())
        self.combo_box_end.setEnabled(False)

        # date setting
        self.group_box_date = QGroupBox(self.tr("Date"), self)
        self.horizontal_layout_right = QHBoxLayout(self.group_box_date)

        self.list_widget_date = QListWidget(self.group_box_date)
        self.horizontal_layout_right.addWidget(self.list_widget_date)

        self.vertical_layout_right = QVBoxLayout()
        self.horizontal_layout_right.addLayout(self.vertical_layout_right)

        self.push_button_add_date = QPushButton(self.tr("Add"), self)
        self.vertical_layout_right.addWidget(self.push_button_add_date)

        self.push_button_edit_date = QPushButton(self.tr("Edit"), self)
        self.vertical_layout_right.addWidget(self.push_button_edit_date)

        self.push_button_remove_date = QPushButton(self.tr("Remove"), self)
        self.vertical_layout_right.addWidget(self.push_button_remove_date)

        self.vertical_layout_right.addStretch(1)

        # navigate
        self.horizontal_layout_down = QHBoxLayout()

        self.horizontal_layout_down.addStretch(1)

        self.push_button_ok = QPushButton(self.tr("OK"), self)
        self.horizontal_layout_down.addWidget(self.push_button_ok)

        self.push_button_cancel = QPushButton(self.tr("Cancel"), self)
        self.horizontal_layout_down.addWidget(self.push_button_cancel)

        # layout settings
        self.vertical_layout_left = QVBoxLayout()
        self.vertical_layout_left.addWidget(self.group_box_general)
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
        self.list_widget_date.itemDoubleClicked.connect(self.push_button_edit_date_clicked)
        self.push_button_add_date.clicked.connect(self.push_button_add_date_clicked)
        self.push_button_edit_date.clicked.connect(self.push_button_edit_date_clicked)
        self.push_button_remove_date.clicked.connect(self.push_button_remove_date_clicked)
        self.push_button_ok.clicked.connect(self.push_button_ok_clicked)
        self.push_button_cancel.clicked.connect(self.push_button_cancel_clicked)

    def save(self) -> bool:
        """
        Saves the created / edited a student pair.
        Returns True/False depending on whether the save was successful or not.
        """
        title = self.line_edit_title.text().strip()
        if title == "":
            QMessageBox.information(self,
                                    self.tr("Information"),
                                    self.tr("Title field is empty"))
            return False

        lecturer = self.line_edit_lecturer.text().strip()
        if lecturer == "":
            QMessageBox.information(self,
                                    self.tr("Information"),
                                    self.tr("Lecturer field is empty"))
            return False

        classes = self.line_edit_classes.text().strip()
        if classes == "":
            QMessageBox.information(self,
                                    self.tr("Information"),
                                    self.tr("Classes field is empty"))
            return False

        pair_type = self.combo_box_type.currentData(Qt.UserRole)
        subgroup = self.combo_box_subgroup.currentData(Qt.UserRole)

        start_time = self.combo_box_start.currentText()
        end_time = self.combo_box_end.currentText()

        if self.list_widget_date.count() == 0:
            QMessageBox.information(self,
                                    self.tr("Information"),
                                    self.tr("No dates"))
            return False

        self._edit_pair.get_value(StudentPairAttrib.Title).set_title(title)
        self._edit_pair.get_value(StudentPairAttrib.Lecturer).set_lecturer(lecturer)
        self._edit_pair.get_value(StudentPairAttrib.Type).set_type(pair_type)
        self._edit_pair.get_value(StudentPairAttrib.Classroom).set_classroom(classes)
        self._edit_pair.get_value(StudentPairAttrib.Subgroup).set_subgroup(subgroup)
        self._edit_pair.get_value(StudentPairAttrib.Time).set_time(start_time, end_time)

        return True

    def set_pair(self, pair: StudentPair):
        self._edit_pair = pair
        self.line_edit_title.setText(str(self._edit_pair.get_value(StudentPairAttrib.Title)))
        self.line_edit_lecturer.setText(str(self._edit_pair.get_value(StudentPairAttrib.Lecturer)))
        self.combo_box_type.setCurrentText(str(self._edit_pair.get_value(StudentPairAttrib.Type)))
        self.line_edit_classes.setText(str(self._edit_pair.get_value(StudentPairAttrib.Classroom)))
        self.combo_box_subgroup.setCurrentText(str(self._edit_pair.get_value(StudentPairAttrib.Subgroup)))

        time: TimePair = self._edit_pair.get_value(StudentPairAttrib.Time)
        if time is not None:
            number = time.get_number()
            self.combo_box_start.setCurrentIndex(number)
            self.combo_box_end.setCurrentIndex(number)

        self.update_list_widget_date()

    def get_pair(self):
        return self._edit_pair

    def push_button_add_date_clicked(self):
        """ Slot for add date button """
        date_creator = DateCreatorWindow(self)
        while True:
            date_creator.exec_()
            create_date = date_creator.get_date()
            if create_date is not None:
                try:
                    self._edit_pair.get_value(StudentPairAttrib.Date).add_date(create_date)
                    self.update_list_widget_date()
                    break
                except InvalidDatePair as ex:
                    QMessageBox.critical(self, self.tr("Invalid date pair"), str(ex))
            else:
                break

    def push_button_edit_date_clicked(self):
        """ Slot for edit date button """
        item = self.list_widget_date.currentItem()
        if item is None:
            QMessageBox.information(self,
                                    self.tr("Information"),
                                    self.tr("No date selected"))
            return

        original_date = item.data(Qt.UserRole)
        self._edit_pair.get_value(StudentPairAttrib.Date).remove_date(item.data(Qt.UserRole))

        date_editor = DateCreatorWindow(self)
        date_editor.set_date(copy.deepcopy(original_date))

        while True:
            date_editor.exec_()
            edit_date = date_editor.get_date()
            if edit_date is not None:
                try:
                    self._edit_pair.get_value(StudentPairAttrib.Date).add_date(edit_date)
                    self.update_list_widget_date()
                    break
                except InvalidDatePair as ex:
                    QMessageBox.critical(self, self.tr("Invalid date pair"), str(ex))
            else:
                self._edit_pair.get_value(StudentPairAttrib.Date).add_date(original_date)
                break

    def push_button_remove_date_clicked(self):
        """ Slot for remove date button """
        item = self.list_widget_date.currentItem()
        if item is None:
            QMessageBox.information(self,
                                    self.tr("Information"),
                                    self.tr("No date selected"))
            return

        self._edit_pair.get_value(StudentPairAttrib.Date).remove_date(item.data(Qt.UserRole))
        self.update_list_widget_date()

    def update_list_widget_date(self):
        """ Updates the list of dates in the window """
        dates = self._edit_pair.get_value(StudentPairAttrib.Date).get_dates()
        self.list_widget_date.clear()
        for date in dates:
            item = QListWidgetItem(str(date))
            item.setData(Qt.UserRole, date)
            self.list_widget_date.addItem(item)

    def push_button_ok_clicked(self):
        """ Slot for ok button """
        if self.save():
            self.close()

    def push_button_cancel_clicked(self):
        self._edit_pair = None
        self.close()

    def combo_box_start_changed(self, index):
        """ Slot for time change combo_box_end """
        self.combo_box_end.setCurrentIndex(index)
