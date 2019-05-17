# coding: utf-8

# imports
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from pair import DateItem, DateRange, FrequencyDate, InvalidDatePair


class DateCreatorWindow(QDialog):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.date = None

        # window settings
        self.setWindowTitle("Date creator")

        # toggle and status layout
        self.horizontal_layout_up = QHBoxLayout()

        self.slider = QSlider(Qt.Horizontal)
        self.horizontal_layout_up.addWidget(self.slider)

        self.label_status = QLabel("Simple date")
        self.horizontal_layout_up.addWidget(self.label_status)

        self.slider.setRange(0, 1)

        # date layout
        self.form_layout_date = QFormLayout()

        # simple date layout
        self.label_simple_date = QLabel("Date")
        self.form_layout_date.setWidget(0, QFormLayout.LabelRole, self.label_simple_date)
        self.date_edit_simple = QDateEdit()
        self.form_layout_date.setWidget(0, QFormLayout.FieldRole, self.date_edit_simple)

        self.date_edit_simple.setCalendarPopup(True)
        self.date_edit_simple.setDisplayFormat('dd.MM.yyyy')
        self.date_edit_simple.setDate(QDate.currentDate())
        self.date_edit_simple.setDateRange(QDate.currentDate().addDays(-365),
                                           QDate.currentDate().addDays(365))

        # range date layout
        self.label_date_start = QLabel("Start")
        self.form_layout_date.setWidget(1, QFormLayout.LabelRole, self.label_date_start)
        self.date_edit_start = QDateEdit()
        self.form_layout_date.setWidget(1, QFormLayout.FieldRole, self.date_edit_start)

        self.label_date_end = QLabel("End")
        self.form_layout_date.setWidget(2, QFormLayout.LabelRole, self.label_date_end)
        self.date_edit_end = QDateEdit()
        self.form_layout_date.setWidget(2, QFormLayout.FieldRole, self.date_edit_end)

        self.label_date_frequency = QLabel("Frequency")
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
        self.date_edit_end.setDate(QDate.currentDate().addDays(7))
        self.date_edit_end.setDateRange(QDate.currentDate().addDays(7),
                                        QDate.currentDate().addDays(365))

        self.combo_box_frequency.addItem(str(FrequencyDate.Every), FrequencyDate.Every)
        self.combo_box_frequency.addItem(str(FrequencyDate.Throughout), FrequencyDate.Throughout)

        # navigate
        self.horizontal_layout_down = QHBoxLayout()

        self.horizontal_layout_down.addStretch(1)

        self.push_button_ok = QPushButton("OK")
        self.horizontal_layout_down.addWidget(self.push_button_ok)

        self.push_button_cancel = QPushButton("Cancel")
        self.horizontal_layout_down.addWidget(self.push_button_cancel)

        # layout setup
        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignCenter)

        self.main_layout.addLayout(self.horizontal_layout_up)
        self.main_layout.addLayout(self.form_layout_date)
        self.main_layout.addStretch(1)
        self.main_layout.addLayout(self.horizontal_layout_down)

        self.setLayout(self.main_layout)

        # connection
        self.slider.valueChanged.connect(self.slider_value_change)
        self.date_edit_start.dateChanged.connect(self.date_edit_start_change)
        self.push_button_ok.clicked.connect(self.push_button_ok_clicked)
        self.push_button_cancel.clicked.connect(self.close)

        self.show_simple_date()

    def set_date(self, date_item):
        if isinstance(date_item, DateItem):
            self.show_simple_date()
            self.slider.setValue(0)
            self.date_edit_simple.setDate(QDate.fromString(date_item.date, "yyyy.MM.dd"))
            self.date = date_item

        if isinstance(date_item, DateRange):
            self.show_range_date()
            self.slider.setValue(1)
            self.date_edit_start.setDate(QDate.fromString(date_item.date_from, "yyyy.MM.dd"))
            self.date_edit_end.setDate(QDate.fromString(date_item.date_to, "yyyy.MM.dd"))
            self.combo_box_frequency.setCurrentText(str(date_item.frequency))
            self.date = date_item

    def get_date(self) -> (DateItem, DateRange, None):
        return self.date

    def show_simple_date(self):
        self.label_simple_date.setVisible(True)
        self.date_edit_simple.setVisible(True)

        self.label_date_start.setVisible(False)
        self.date_edit_start.setVisible(False)
        self.label_date_end.setVisible(False)
        self.date_edit_end.setVisible(False)
        self.label_date_frequency.setVisible(False)
        self.combo_box_frequency.setVisible(False)

    def show_range_date(self):
        self.label_date_start.setVisible(True)
        self.date_edit_start.setVisible(True)
        self.label_date_end.setVisible(True)
        self.date_edit_end.setVisible(True)
        self.label_date_frequency.setVisible(True)
        self.combo_box_frequency.setVisible(True)

        self.label_simple_date.setVisible(False)
        self.date_edit_simple.setVisible(False)

    def date_edit_start_change(self, date: QDate):
        self.date_edit_end.setMinimumDate(date.addDays(7))

    def slider_value_change(self, value: int):
        if value == 0:
            # simple date
            self.label_status.setText("Simple date")
            self.show_simple_date()
        else:
            # range date
            self.label_status.setText("Range date")
            self.show_range_date()

    def push_button_ok_clicked(self):
        try:
            if self.slider.value() == 0:
                # simple date
                self.date = DateItem(self.date_edit_simple.date().toString("yyyy.MM.dd"))
            else:
                # range date
                self.date = DateRange(self.date_edit_start.date().toString("yyyy.MM.dd"),
                                      self.date_edit_end.date().toString("yyyy.MM.dd"),
                                      self.combo_box_frequency.currentData(Qt.UserRole))

            self.close()
        except InvalidDatePair as pair_ex:
            QMessageBox.warning(self, "Date error", str(pair_ex))

        except Exception as ex:
            QMessageBox.critical(self, "Unknown error", str(ex))
