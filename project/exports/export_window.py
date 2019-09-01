# coding: utf-8

# imports
from PyQt5.QtWidgets import QDialog, QWidget, QFormLayout, QLineEdit, QLabel, QCheckBox, \
    QGroupBox, QDateEdit, QHBoxLayout, QVBoxLayout, QPushButton, QMessageBox, QComboBox, \
    QProgressDialog, QFileDialog, QColorDialog, qApp, QListWidget, QToolButton, QAction, \
    QFileIconProvider, QListWidgetItem
from PyQt5.QtCore import Qt, QDate, QUrl, QFileInfo
from PyQt5.QtGui import QColor, QDesktopServices

from project.schedule import Schedule
from project.exports.export_logic import export_weeks_to_pdf, export_full_to_pdf

from project import util
import os


class ExportWindow(QDialog):
    """
    Class describing a dialog for exports of schedules.
    """
    def __init__(self, schedule: Schedule, parent: QWidget = None):
        super().__init__(parent)
        self._schedule_ref = schedule
        self._date_start_cache = None

        # window settings
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setWindowTitle(self.tr("Export window"))
        self.setMinimumWidth(800)

        # title, add_date, work mode
        self.layout_title_date_mode = QHBoxLayout()

        self.label_title = QLabel(self.tr("Title"))
        self.layout_title_date_mode.addWidget(self.label_title)

        self.line_edit_title = QLineEdit()
        self.layout_title_date_mode.addWidget(self.line_edit_title)

        self.check_box_add_date = QCheckBox(self.tr("Add date"))
        self.layout_title_date_mode.addWidget(self.check_box_add_date)

        self.combo_box_work_mode = QComboBox()
        self.layout_title_date_mode.addWidget(self.combo_box_work_mode)

        self.line_edit_title.setPlaceholderText(self.tr("My Group. A subgroup - green color, "
                                                        "B subgroup - yellow color. "))
        self.check_box_add_date.setChecked(True)

        self.combo_box_work_mode.addItem(self.tr("Weekly"))
        self.combo_box_work_mode.addItem(self.tr("Full"))

        # list widget with files
        self.layout_list_widget = QVBoxLayout()

        self.check_box_use_current = QCheckBox(self.tr("Use current schedule"))
        self.layout_list_widget.addWidget(self.check_box_use_current)
        self.check_box_use_current.setChecked(True)

        self.list_widget = QListWidget()
        self.layout_list_widget.addWidget(self.list_widget)
        self.list_widget.setSortingEnabled(True)
        self.list_widget.setEnabled(False)

        self.layout_open_folder = QHBoxLayout()
        self.layout_list_widget.addLayout(self.layout_open_folder)

        self.label_find = QLabel(self.tr("Schedules: ") + "0")
        self.layout_open_folder.addWidget(self.label_find)

        self.layout_open_folder.addStretch(1)

        self.push_button_open_folder = QToolButton()
        self.layout_open_folder.addWidget(self.push_button_open_folder)
        self.push_button_open_folder.setEnabled(False)

        self.push_button_open_folder.setText(self.tr("Open folder"))
        self.push_button_open_folder.setPopupMode(QToolButton.MenuButtonPopup)

        self.action_open_files = QAction(self.tr("Open files"))
        self.push_button_open_folder.addAction(self.action_open_files)

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

        for font_name, font_path in util.get_fonts():
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

        if QDate.currentDate().day() < (QDate.currentDate().dayOfYear() / 2):
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

        self.combo_box_pattern_a_b.addItem(self.tr("Chess order"))
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
        self.layout_center.addLayout(self.layout_list_widget)
        self.layout_center.addLayout(self.layout_right_setting)

        self.layout_main = QVBoxLayout()
        self.layout_main.addLayout(self.layout_title_date_mode)
        self.layout_main.addLayout(self.layout_center)
        self.layout_main.addLayout(self.layout_navigate)

        self.setLayout(self.layout_main)

        # connection
        self.check_box_use_current.clicked.connect(self.check_box_use_current_clicked)
        self.push_button_open_folder.clicked.connect(self.open_folder_clicked)
        self.action_open_files.triggered.connect(self.open_files_clicked)

        self.date_edit_start.dateChanged.connect(self.date_edit_start_changed)
        self.combo_box_color_a.activated.connect(self.combo_box_color_a_clicked)
        self.combo_box_color_b.activated.connect(self.combo_box_color_b_clicked)
        self.push_button_export.clicked.connect(self.export_to_pdf)
        self.push_button_cancel.clicked.connect(self.close)

    def add_standard_colors(self, combo_box: QComboBox) -> None:
        """
        Adds colors to the color selection menu.

        :param combo_box: Color selection menu
        """
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
            combo_box.addItem(util.create_color_icon(data), name, data)

    def export_to_pdf(self) -> None:
        # select path

        paths = []

        if self.check_box_use_current.isChecked():
            path = QFileDialog.getSaveFileName(self,
                                               self.tr("Export to pdf"),
                                               ".",
                                               "PDF file (*.pdf)")[0]
            if path == "":
                return

            if not path.endswith(".pdf"):
                path += ".pdf"

            paths.append(path)
        else:
            for index in range(self.list_widget.count()):
                path = self.list_widget.item(index).data(Qt.UserRole)
                paths.append(path)

        # progress dialog
        progress = QProgressDialog(self.tr("Export to pdf"),
                                   self.tr("Abort exports"), 0, 100, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(2000)

        try:
            for index, path in enumerate(paths):

                if self.check_box_use_current.isChecked():
                    title_text = self.line_edit_title.text()
                    schedule = self._schedule_ref
                else:
                    title_text = QFileInfo(path).baseName()
                    schedule = Schedule()
                    schedule.load(path)
                    path = path[0:-5] + ".pdf"

                print(path)
                mode = self.combo_box_work_mode.currentIndex()
                if mode == 0:
                    export_weeks_to_pdf(schedule,
                                        title_text,
                                        self.check_box_add_date.isChecked(),
                                        path,
                                        self.combo_box_font.currentText(),
                                        self.combo_box_font.currentData(Qt.UserRole),
                                        self.combo_box_encoding.currentText(),
                                        self.date_edit_start.date().toPyDate(),
                                        self.date_edit_end.date().toPyDate(),
                                        self.combo_box_color_a.currentData(Qt.UserRole),
                                        self.combo_box_color_b.currentData(Qt.UserRole),
                                        progress if self.check_box_use_current.isChecked() else None)
                else:
                    export_full_to_pdf(schedule,
                                       title_text,
                                       path,
                                       self.combo_box_font.currentText(),
                                       self.combo_box_font.currentData(Qt.UserRole),
                                       self.combo_box_encoding.currentText(),
                                       progress if self.check_box_use_current.isChecked() else None)

                progress.setValue(int(index * 100 / len(paths)))

            # finish dialog
            progress.setValue(100)
            finish_msg_box = QMessageBox(QMessageBox.Information, self.tr("Export to pdf"),
                                         self.tr("Gone!"))
            open_folder_button = finish_msg_box.addButton(self.tr("Open folder"),
                                                          QMessageBox.ActionRole)
            finish_msg_box.addButton(QMessageBox.Ok)
            finish_msg_box.exec_()

            if finish_msg_box.clickedButton() == open_folder_button:
                QDesktopServices.openUrl(QUrl(QFileInfo(paths[0] if len(paths) != 0 else ".").absolutePath()))

        except UnicodeEncodeError as ex:
            QMessageBox.critical(self,
                                 self.tr("Encoding error"),
                                 str(ex))
        except Exception as ex:
            QMessageBox.critical(self,
                                 self.tr("Unknown error"),
                                 str(ex))
        progress.setValue(100)

    def check_box_use_current_clicked(self, checked: bool):
        if checked:
            self.list_widget.setEnabled(False)
            self.push_button_open_folder.setEnabled(False)
            self.line_edit_title.setEnabled(False)
        else:
            self.list_widget.setEnabled(True)
            self.push_button_open_folder.setEnabled(True)
            self.line_edit_title.setEnabled(True)

    def open_folder_clicked(self):
        path = QFileDialog.getExistingDirectory(self, self.tr("Select folder"))

        provider = QFileIconProvider()
        self.list_widget.clear()

        for dir_path, dir_names, file_names in os.walk(path):
            for file_name in file_names:
                if file_name.endswith(".json"):
                    item = QListWidgetItem()
                    item.setText(file_name[0:-5])
                    item.setData(Qt.UserRole, dir_path + os.sep + file_name)
                    item.setIcon(provider.icon(QFileInfo(dir_path
                                                         + os.sep + file_name)))

                    self.list_widget.addItem(item)

        self.label_find.setText(self.tr("Schedules: ")
                                + str(self.list_widget.count()))

    def open_files_clicked(self):
        files = QFileDialog.getOpenFileNames(self,
                                             self.tr("Select files"),
                                             "",
                                             "JSON file (*.json) ;; All files (*.*)")[0]
        provider = QFileIconProvider()
        self.list_widget.clear()

        for file_path in files:
            file = QFileInfo(file_path)
            item = QListWidgetItem()
            item.setText(file.baseName())
            item.setData(Qt.UserRole, file_path)
            item.setIcon(provider.icon(file))
            self.list_widget.addItem(item)

        self.label_find.setText(self.tr("Schedules: ")
                                + str(self.list_widget.count()))

    def combo_box_color_a_clicked(self) -> None:
        """
        Slot for color selection of A subgroup.
        """
        if self.combo_box_color_a.currentIndex() == 0:
            self.custom_color_selected(self.combo_box_color_a)

    def combo_box_color_b_clicked(self) -> None:
        """
        Slot for color selection of B subgroup.
        """
        if self.combo_box_color_b.currentIndex() == 0:
            self.custom_color_selected(self.combo_box_color_b)

    def custom_color_selected(self, combo_box: QComboBox) -> None:
        """
        Slot to select the color for the desired menu.

        :param combo_box: Menu
        """
        color = QColorDialog.getColor(combo_box.currentData(), self)
        if color.isValid():
            combo_box.setItemIcon(0, util.create_color_icon(color))
            combo_box.setItemData(0, color)

    def date_edit_start_changed(self, date: QDate):
        """
        Slot for changing the end of a range of dates.

        :param date: Start of the date range
        """
        end_date = self.date_edit_end.date().addDays(self._date_start_cache.daysTo(date))
        self.date_edit_end.setMinimumDate(date.addDays(7))
        self.date_edit_end.setDate(end_date)
        self._date_start_cache = QDate(date)
