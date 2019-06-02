# coding: utf-8

# imports
from PyQt5.QtWidgets import QDialog, QWidget, QVBoxLayout, QHBoxLayout, \
                            QCheckBox, QMessageBox, QLabel, QFormLayout, \
                            QDateEdit, QComboBox, QPushButton
from PyQt5.QtCore import Qt, QDate
from project.pair import DateItem, DateRange, FrequencyDate, InvalidDatePair


class DateCreatorWindow(QDialog):
    """ Dialog window for creation / editing date """
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self._date = None
        self._date_delta = 7
        self._date_start_temp = QDate.currentDate()

        # window settings
        self.setWindowTitle(self.tr("Date creator"))

        # toggle and status
        self.check_box = QCheckBox(self.tr("Range date"))

        # date layout
        self.form_layout_date = QFormLayout()

        # simple date layout
        self.label_simple_date = QLabel(self.tr("Date"))
        self.form_layout_date.setWidget(0, QFormLayout.LabelRole, self.label_simple_date)
        self.date_edit_simple = QDateEdit()
        self.form_layout_date.setWidget(0, QFormLayout.FieldRole, self.date_edit_simple)

        self.date_edit_simple.setCalendarPopup(True)
        self.date_edit_simple.setDisplayFormat('dd.MM.yyyy')
        self.date_edit_simple.setDate(QDate.currentDate())
        self.date_edit_simple.setDateRange(QDate.currentDate().addDays(-365),
                                           QDate.currentDate().addDays(365))

        # range date layout
        self.label_date_start = QLabel(self.tr("Start"))
        self.form_layout_date.setWidget(1, QFormLayout.LabelRole, self.label_date_start)
        self.date_edit_start = QDateEdit()
        self.form_layout_date.setWidget(1, QFormLayout.FieldRole, self.date_edit_start)

        self.label_date_end = QLabel(self.tr("End"))
        self.form_layout_date.setWidget(2, QFormLayout.LabelRole, self.label_date_end)
        self.date_edit_end = QDateEdit()
        self.form_layout_date.setWidget(2, QFormLayout.FieldRole, self.date_edit_end)

        self.label_date_frequency = QLabel(self.tr("Frequency"))
        self.form_layout_date.setWidget(3, QFormLayout.LabelRole, self.label_date_frequency)
        self.combo_box_frequency = QComboBox()
        self.form_layout_date.setWidget(3, QFormLayout.FieldRole, self.combo_box_frequency)

        self.date_edit_start.setCalendarPopup(True)
        self.date_edit_start.setDisplayFormat('dd.MM.yyyy')
        self.date_edit_start.setDate(QDate.currentDate())
        self.date_edit_start.setDateRange(QDate.currentDate().addDays(-365),
                                          QDate.currentDate().addDays(365))

        self.date_edit_end.setCalendarPopup(True)
        self.date_edit_end.setDisplayFormat('dd.MM.yyyy')
        self.date_edit_end.setDate(QDate.currentDate().addDays(self._date_delta))
        self.date_edit_end.setDateRange(QDate.currentDate().addDays(self._date_delta),
                                        QDate.currentDate().addDays(365))

        self.combo_box_frequency.addItem(str(FrequencyDate.Every), FrequencyDate.Every)
        self.combo_box_frequency.addItem(str(FrequencyDate.Throughout), FrequencyDate.Throughout)

        # navigate
        self.horizontal_layout_down = QHBoxLayout()

        self.horizontal_layout_down.addStretch(1)

        self.push_button_ok = QPushButton(self.tr("OK"))
        self.horizontal_layout_down.addWidget(self.push_button_ok)

        self.push_button_apply = QPushButton(self.tr("Apply"))
        self.horizontal_layout_down.addWidget(self.push_button_apply)

        self.push_button_cancel = QPushButton(self.tr("Cancel"))
        self.horizontal_layout_down.addWidget(self.push_button_cancel)

        # layout setup
        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignCenter)

        self.main_layout.addWidget(self.check_box)
        self.main_layout.addLayout(self.form_layout_date)
        self.main_layout.addStretch(1)
        self.main_layout.addLayout(self.horizontal_layout_down)

        self.setLayout(self.main_layout)

        # connection
        self.check_box.clicked.connect(self.check_box_clicked)
        self.date_edit_start.dateChanged.connect(self.date_edit_start_change)
        self.date_edit_end.dateChanged.connect(self.date_range_validation)
        self.combo_box_frequency.currentIndexChanged.connect(self.combo_box_frequency_changed)
        self.push_button_ok.clicked.connect(self.push_button_ok_clicked)
        self.push_button_apply.clicked.connect(self.push_button_apply_clicked)
        self.push_button_cancel.clicked.connect(self.push_button_cancel_clicked)

        self.show_simple_date()

    def set_date(self, date_item) -> None:
        """ Sets the date for editing """
        if isinstance(date_item, DateItem):
            self.show_simple_date()
            self.date_edit_simple.setDate(QDate.fromString(date_item.date, "yyyy.MM.dd"))
            self._date = date_item

        if isinstance(date_item, DateRange):
            self.show_range_date()
            self.date_edit_start.setDate(QDate.fromString(date_item.date_from, "yyyy.MM.dd"))
            self.date_edit_end.setDate(QDate.fromString(date_item.date_to, "yyyy.MM.dd"))
            self.combo_box_frequency.setCurrentText(str(date_item.frequency))
            self._date = date_item

    def get_date(self) -> (DateItem, DateRange, None):
        """ Returns the created date """
        return self._date

    def show_simple_date(self) -> None:
        """ Switches the window to simple date editing mode """
        self.label_simple_date.setVisible(True)
        self.date_edit_simple.setVisible(True)

        self.label_date_start.setVisible(False)
        self.date_edit_start.setVisible(False)
        self.label_date_end.setVisible(False)
        self.date_edit_end.setVisible(False)
        self.label_date_frequency.setVisible(False)
        self.combo_box_frequency.setVisible(False)

    def show_range_date(self) -> None:
        """ Switches the window to range date editing mode """
        self.label_date_start.setVisible(True)
        self.date_edit_start.setVisible(True)
        self.label_date_end.setVisible(True)
        self.date_edit_end.setVisible(True)
        self.label_date_frequency.setVisible(True)
        self.combo_box_frequency.setVisible(True)

        self.label_simple_date.setVisible(False)
        self.date_edit_simple.setVisible(False)

    def date_edit_start_change(self, date: QDate) -> None:
        """ Slot for start date edit """
        end_date = self.date_edit_end.date().addDays(self._date_start_temp.daysTo(date))
        self.date_edit_end.setDateRange(date.addDays(self._date_delta),
                                        date.addDays(365))
        self.date_edit_end.setDate(end_date)
        self._date_start_temp = QDate(date)

    def combo_box_frequency_changed(self, index: int) -> None:
        """ Slot for frequency combo box """
        if index == 0:
            self._date_delta = 7
        else:
            self._date_delta = 14

        self.date_edit_end.setDateRange(self.date_edit_start.date().addDays(self._date_delta),
                                        self.date_edit_start.date().addDays(365))
        self.date_range_validation()

    def date_range_validation(self) -> None:
        """ Checks the correctness of the entered dates """
        if self.date_edit_start.date().dayOfWeek() == self.date_edit_end.date().dayOfWeek():
            if self.date_edit_start.date().daysTo(self.date_edit_end.date()) % self._date_delta == 0:
                msg = ""
                style = ""
            else:
                msg = self.tr("The number of days between dates is not a multiple of {}").format(self._date_delta)
                style = "QDateEdit { background-color: #ff5e5e; }"
        else:
            msg = self.tr("Different days of the week at dates")
            style = "QDateEdit { background-color: #ff5e5e; }"

        if msg == "":
            self.push_button_ok.setEnabled(True)
            self.push_button_apply.setEnabled(True)
        else:
            self.push_button_ok.setEnabled(False)
            self.push_button_apply.setEnabled(False)

        self.date_edit_start.setStyleSheet(style)
        self.date_edit_end.setStyleSheet(style)
        self.date_edit_start.setToolTip(msg)
        self.date_edit_end.setToolTip(msg)

    def check_box_clicked(self, value: bool) -> None:
        """ Slot for check box """
        if value is False:
            # simple date
            self.show_simple_date()
        else:
            # range date
            self.show_range_date()

    def push_button_ok_clicked(self) -> None:
        """ Slot for ok button """
        if self.push_button_apply_clicked():
            self.close()

    def push_button_apply_clicked(self) -> bool:
        """ Slot for apply button """
        try:
            if self.check_box.isChecked() is False:
                # simple date
                self._date = DateItem(self.date_edit_simple.date().toString("yyyy.MM.dd"))
            else:
                # range date
                self._date = DateRange(self.date_edit_start.date().toString("yyyy.MM.dd"),
                                       self.date_edit_end.date().toString("yyyy.MM.dd"),
                                       self.combo_box_frequency.currentData(Qt.UserRole))
            return True
        except InvalidDatePair as pair_ex:
            QMessageBox.warning(self, self.tr("Date error"), str(pair_ex))

        except Exception as ex:
            QMessageBox.critical(self, self.tr("Unknown error"), str(ex))

        return False

    def push_button_cancel_clicked(self):
        self._date = None
        self.close()
