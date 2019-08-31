# coding: utf-8

# imports
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QPushButton, \
                            QProgressBar, QLabel, QGridLayout, QFormLayout, \
                            QWidget, QListWidget, QGroupBox, QCheckBox, QFileDialog, \
                            QListWidgetItem, QFileIconProvider, QComboBox, qApp, \
                            QDateEdit, QColorDialog, QSpinBox, QToolButton, QAction
from PyQt5.QtCore import Qt, QFileInfo, QTimer, QDate
from PyQt5.QtGui import QCloseEvent, QColor

from .import_logic import ImportManager, import_from_pdf
from .confuse_window import ConfuseWindow
from .. import util


import os
from multiprocessing import Process


class ImportWindow(QDialog):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self._size: int = os.cpu_count()
        if self._size is None:
            self._size = 2

        self._processes_pool = []
        self._manager = ImportManager(self._size)
        self._max_progress: int = 0
        self._timer: QTimer = QTimer()
        self._confuser = ConfuseWindow(self)
        self._date_start_cache = None
        self._tesseract_path_cache = None
        self._poppler_path_cache = None

        # window settings
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setWindowTitle(self.tr("Import window"))

        # list widget with files
        self.list_widget = QListWidget()
        self.list_widget.setSortingEnabled(True)

        self.layout_open_folder = QHBoxLayout()
        self.label_find = QLabel(self.tr("Schedules: ") + "0")
        self.layout_open_folder.addWidget(self.label_find)

        self.layout_open_folder.addStretch(1)

        self.push_button_open_folder = QToolButton()
        self.layout_open_folder.addWidget(self.push_button_open_folder)

        self.push_button_open_folder.setText(self.tr("Open folder"))
        self.push_button_open_folder.setPopupMode(QToolButton.MenuButtonPopup)

        self.action_open_files = QAction(self.tr("Open files"))
        self.push_button_open_folder.addAction(self.action_open_files)

        # main progress
        self.group_box_main_progress = QGroupBox(self.tr("Main progress"))
        self.layout_main_progress = QVBoxLayout(self.group_box_main_progress)

        self.process_bar_main = QProgressBar()
        self.layout_main_progress.addWidget(self.process_bar_main)

        self.layout_start_process = QHBoxLayout()
        self.layout_start_process.addStretch(1)

        self.push_button_import = QPushButton(self.tr("Import"))
        self.layout_start_process.addWidget(self.push_button_import)

        self.push_button_stop = QPushButton(self.tr("Stop"))
        self.layout_start_process.addWidget(self.push_button_stop)

        self.push_button_stop.setEnabled(False)

        self.layout_main_progress.addLayout(self.layout_start_process)

        # threads process
        self.group_box_threads = QGroupBox(self.tr("Threads"))
        self.grid_layout_threads = QGridLayout(self.group_box_threads)

        self._progresses_bars = []
        rows = self._size // 2
        columns = 2
        for i in range(rows):
            for j in range(columns):
                progress_bar = QProgressBar()
                progress_bar.setTextVisible(True)
                self._progresses_bars.append(progress_bar)
                self.grid_layout_threads.addWidget(progress_bar, i, j)

        # options
        self.group_box_options = QGroupBox(self.tr("Options"))
        self.form_layout_options = QFormLayout(self.group_box_options)

        self.check_box_weekly = QCheckBox(self.tr("Create weekly schedule"))
        self.form_layout_options.addRow(self.check_box_weekly)

        self.check_box_full = QCheckBox(self.tr("Create full schedule"))
        self.form_layout_options.addRow(self.check_box_full)

        self.check_box_debug_img = QCheckBox(self.tr("Create debug image"))
        self.form_layout_options.addRow(self.check_box_debug_img)

        self.spin_box_dpi = QSpinBox()
        self.form_layout_options.addRow(self.tr("DPI"), self.spin_box_dpi)

        self.combo_box_tesseract_path = QComboBox()
        self.form_layout_options.addRow(self.tr("Tesseract path"), self.combo_box_tesseract_path)

        self.combo_box_poppler_path = QComboBox()
        self.form_layout_options.addRow(self.tr("Poppler path"), self.combo_box_poppler_path)

        self.check_box_debug_img.setChecked(True)
        self.check_box_debug_img.setEnabled(False)

        self.spin_box_dpi.setRange(200, 800)
        self.spin_box_dpi.setValue(500)

        self.combo_box_tesseract_path.addItem(self.tr("<select tesseract path>"))
        self.combo_box_tesseract_path.addItem("Default", "tesseract")
        self.combo_box_tesseract_path.setCurrentIndex(1)
        self._tesseract_path_cache = self.combo_box_tesseract_path.currentText()

        self.combo_box_poppler_path.addItem(self.tr("<select poppler path>"))
        self.combo_box_poppler_path.addItem("Default", None)
        self.combo_box_poppler_path.setCurrentIndex(1)
        self._poppler_path_cache = self.combo_box_poppler_path.currentText()

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

        self.combo_box_pattern_a_b.addItem(self.tr("Chess order"))
        self.combo_box_pattern_a_b.setEnabled(False)

        # navigate
        self.layout_navigate = QHBoxLayout()

        self.layout_navigate.addStretch(1)

        self.push_button_ok = QPushButton(self.tr("OK"))
        self.layout_navigate.addWidget(self.push_button_ok)

        self.push_button_cancel = QPushButton(self.tr("Cancel"))
        self.layout_navigate.addWidget(self.push_button_cancel)

        # layout setup
        self.layout_left = QVBoxLayout()
        self.layout_left.addWidget(self.list_widget)
        self.layout_left.addLayout(self.layout_open_folder)

        self.layout_right = QVBoxLayout()
        self.layout_right.addWidget(self.group_box_main_progress)
        self.layout_right.addWidget(self.group_box_threads)

        self.layout_down = QGridLayout()
        self.layout_down.addWidget(self.group_box_options, 0, 0)
        self.layout_down.addWidget(self.group_box_font, 1, 0)
        self.layout_down.addWidget(self.group_box_date, 0, 1)
        self.layout_down.addWidget(self.group_box_subgroup, 1, 1)

        self.layout_right.addLayout(self.layout_down)
        self.layout_right.addStretch(1)
        self.layout_right.addLayout(self.layout_navigate)

        self.layout_main = QHBoxLayout()
        self.layout_main.addLayout(self.layout_left, 1)
        self.layout_main.addLayout(self.layout_right, 2)

        self.setLayout(self.layout_main)

        # connections
        self._timer.timeout.connect(self.check_processes)

        self.push_button_open_folder.clicked.connect(self.open_folder_clicked)
        self.action_open_files.triggered.connect(self.open_files_clicked)

        self.push_button_import.clicked.connect(self.push_button_import_clicked)
        self.push_button_stop.clicked.connect(self.push_button_stop_clicked)

        self.check_box_weekly.clicked.connect(self.check_box_weekly_clicked)
        self.combo_box_tesseract_path.activated.connect(self.combo_box_tesseract_path_clicked)
        self.combo_box_poppler_path.activated.connect(self.combo_box_poppler_path_clicked)

        self.date_edit_start.dateChanged.connect(self.date_edit_start_changed)
        self.combo_box_color_a.activated.connect(self.combo_box_color_a_clicked)
        self.combo_box_color_b.activated.connect(self.combo_box_color_b_clicked)

        self.push_button_ok.clicked.connect(self.close)
        self.push_button_cancel.clicked.connect(self.close)

    def check_processes(self):
        work_processes = 0
        for index in range(self._size):
            if self._processes_pool[index].is_alive():
                work_processes += 1

            text = self._manager.progress_text_list[index]
            if text is not None and text != "":
                self._progresses_bars[index].setFormat(text)
                self._progresses_bars[index].setValue(self._manager.progress_value_list[index])

            if self._manager.confuse_answer_list[index] == ConfuseWindow.NeededSolution:
                if self._confuser.status == ConfuseWindow.Solved:
                    answer_index = self._confuser.index
                    self._manager.confuse_list[answer_index] = self._confuser.answer
                    self._manager.confuse_answer_list[answer_index] = ConfuseWindow.Solved
                    self._confuser.status = ConfuseWindow.Nothing
                elif self._confuser.status == ConfuseWindow.Nothing:
                    self._confuser.status = ConfuseWindow.Work
                    self._confuser.index = index
                    self._confuser.text_edit_confuse.setText(self._manager.confuse_info[index])
                    self._confuser.text_edit_answer.setText(self._manager.confuse_list[index])
                    self._confuser.set_image(self._manager.confuse_file_path[index])
                    self._confuser.show()

        progress = self._max_progress - self._manager.queue.qsize() - work_processes
        self.process_bar_main.setValue(progress)

        if work_processes == 0:
            self.push_button_stop_clicked()
            return

        if not self._manager.flags["stop"]:
            self._timer.start(1000)

    def open_folder_clicked(self):
        path = QFileDialog.getExistingDirectory(self, self.tr("Select folder"))

        provider = QFileIconProvider()
        self.list_widget.clear()

        for dir_path, dir_names, file_names in os.walk(path):
            for file_name in file_names:
                if file_name.endswith(".pdf"):
                    item = QListWidgetItem()
                    item.setText(file_name[0:-4])
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
                                             "PDF file (*.pdf) ;; All files (*.*)")[0]
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

    def push_button_import_clicked(self):
        self.group_box_options.setEnabled(False)
        self.group_box_font.setEnabled(False)
        self.group_box_date.setEnabled(False)
        self.group_box_subgroup.setEnabled(False)
        self.push_button_import.setEnabled(False)
        self.push_button_stop.setEnabled(True)
        self.push_button_ok.setEnabled(False)
        self.push_button_cancel.setEnabled(False)
        self.push_button_open_folder.setEnabled(False)

        for number in range(self.list_widget.count()):
            path = self.list_widget.item(number).data(Qt.UserRole)
            self._manager.queue.put(path)

        self._max_progress = self.list_widget.count()
        self.process_bar_main.setRange(0, self._max_progress)
        self.process_bar_main.setValue(0)

        self._manager.weekly = self.check_box_weekly.isChecked()
        self._manager.full = self.check_box_full.isChecked()
        self._manager.debug_image = self.check_box_debug_img.isChecked()

        self._manager.dpi = self.spin_box_dpi.value()
        self._manager.tesseract_path = self.combo_box_tesseract_path.currentData(Qt.UserRole)
        self._manager.poppler_path = self.combo_box_poppler_path.currentData(Qt.UserRole)

        self._manager.font_name = self.combo_box_font.currentText()
        self._manager.font_path = self.combo_box_font.currentData(Qt.UserRole)
        self._manager.encoding = self.combo_box_encoding.currentText()

        self._manager.start = self.date_edit_start.date().toPyDate()
        self._manager.end = self.date_edit_end.date().toPyDate()

        self._manager.color_a = self.combo_box_color_a.currentData(Qt.UserRole)
        self._manager.color_b = self.combo_box_color_b.currentData(Qt.UserRole)

        self._manager.flags["stop"] = False

        self._processes_pool.clear()
        for index in range(self._size):
            process = Process(target=import_from_pdf,
                              args=(index, self._manager),
                              daemon=True)
            process.start()
            self._processes_pool.append(process)

        self._timer.start(500)

    def push_button_stop_clicked(self):
        self.push_button_stop.setEnabled(False)

        self._manager.flags["stop"] = True

        self.group_box_options.setEnabled(True)
        self.group_box_font.setEnabled(True)
        self.group_box_date.setEnabled(True)
        self.group_box_subgroup.setEnabled(True)
        self.push_button_import.setEnabled(True)
        self.push_button_ok.setEnabled(True)
        self.push_button_cancel.setEnabled(True)
        self.push_button_open_folder.setEnabled(True)

    def check_box_weekly_clicked(self):
        if self.check_box_weekly.isChecked():
            self.group_box_date.setEnabled(True)
            self.group_box_subgroup.setEnabled(True)
        else:
            self.group_box_date.setEnabled(False)
            self.group_box_subgroup.setEnabled(False)

    def combo_box_tesseract_path_clicked(self, index):
        if index == 0:
            path = QFileDialog.getOpenFileName(self, self.tr("Select Tesseract"))[0]

            if path == "":
                self.combo_box_tesseract_path.setCurrentText(self._tesseract_path_cache)
                return

            self.combo_box_tesseract_path.addItem(path, path)
            self.combo_box_tesseract_path.setCurrentText(path)
            self._tesseract_path_cache = path

    def combo_box_poppler_path_clicked(self, index):
        if index == 0:
            path = QFileDialog.getOpenFileName(self, self.tr("Select Poppler"))[0]

            if path == "":
                self.combo_box_poppler_path.setCurrentText(self._poppler_path_cache)
                return

            self.combo_box_poppler_path.addItem(path, path)
            self.combo_box_poppler_path.setCurrentText(path)
            self._poppler_path_cache = path

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

    def closeEvent(self, event: QCloseEvent) -> None:
        for process in self._processes_pool:
            process.terminate()

        print("Processes terminate")
