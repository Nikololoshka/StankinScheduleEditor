# coding: utf-8

# imports
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from schedule import Schedule
from pair import DaysOfWeek
from window_helper import CustomHeaderView, compute_font_for_text
from pair_selector_window import PairSelectorWindow
import defaults


class ScheduleEditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.schedule = Schedule()
        self.file = None

        # window settings
        self.setWindowTitle("Schedule Editor")
        self.setMinimumSize(QSize(800, 600))

        # central widget settings
        self.table_widget = QTableWidget()
        self.table_widget.setVerticalHeader(CustomHeaderView(Qt.Vertical))
        self.table_widget.setHorizontalHeader(CustomHeaderView(Qt.Horizontal))
        self.table_widget.setWordWrap(True)
        self.table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_widget.horizontalHeader().setMaximumHeight(25)
        self.table_widget.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_widget.verticalHeader().setMaximumWidth(25)
        self.table_widget.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.table_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.table_widget.setColumnCount(8)
        for i in range(8):
            item = QTableWidgetItem(defaults.get_time_start_end(i))
            self.table_widget.setHorizontalHeaderItem(i, item)

        self.table_widget.setRowCount(6)
        for i, day in enumerate(DaysOfWeek.to_list()):
            item = QTableWidgetItem(day)
            self.table_widget.setVerticalHeaderItem(i, item)

        self.setCentralWidget(self.table_widget)

        # menu bar settings
        menu_bar = self.menuBar()
        menu_file = menu_bar.addMenu("&File")

        action_new_file = QAction(QIcon.fromTheme("document-new"), "&New file", self)
        action_new_file.setShortcut("Ctrl+N")
        menu_file.addAction(action_new_file)

        action_open = QAction(QIcon.fromTheme("document-open"), "&Open", self)
        action_open.setShortcut("Ctrl+O")
        menu_file.addAction(action_open)

        action_save = QAction(QIcon.fromTheme("document-save"), "&Save", self)
        action_save.setShortcut("Ctrl+S")
        menu_file.addAction(action_save)

        action_save_as = QAction(QIcon.fromTheme("document-save-as"), "Save as...", self)
        action_save_as.setShortcut("Ctrl+S+A")
        menu_file.addAction(action_save_as)

        action_export = QAction("Export", self)
        action_export.setShortcut("Ctrl+E")
        menu_file.addAction(action_export)

        menu_file.addSeparator()

        action_about = QAction("About", self)
        menu_file.addAction(action_about)

        action_exit = QAction("&Quit", self)
        action_exit.setShortcut("Ctrl+Q")
        menu_file.addAction(action_exit)

        # status bar settings
        self.statusBar().showMessage("Ready!")

        # connection
        action_new_file.triggered.connect(self.action_new_file_clicked)
        action_open.triggered.connect(self.action_open_clicked)
        action_save.triggered.connect(self.action_save_clicked)
        action_save_as.triggered.connect(self.action_save_as_clicked)
        action_export.triggered.connect(self.action_export_clicked)
        action_about.triggered.connect(self.action_about_clicked)
        action_exit.triggered.connect(self.close)

        self.table_widget.doubleClicked.connect(self.cell_clicked)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        self.update_table_widget()
        super().resizeEvent(a0)

    def update_table_widget(self):
        for i, day in enumerate(self.schedule.schedule_list.values()):
            for j, times in enumerate(day.values()):
                text = ""
                for k, pair in enumerate(times):
                    text += str(pair) + "\n"

                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignTop | Qt.AlignLeft)
                font = compute_font_for_text(item.text(),
                                             Qt.AlignTop | Qt.AlignLeft | Qt.TextWordWrap,
                                             self.cell_size(j, i))
                item.setFont(font)

                self.table_widget.setItem(i, j, item)

    def cell_size(self, column, row) -> QSize:
        return QSize(self.table_widget.columnWidth(column),
                     self.table_widget.rowHeight(row))

    def action_new_file_clicked(self):
        pass

    def action_open_clicked(self):
        path = QFileDialog.getOpenFileName(self, "Open xml file", "./examples", "XML file (*.xml)")[0]
        if path == "":
            return
        try:
            self.schedule.load(path)
            self.file = QFileInfo(path)
            self.update_table_widget()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e),)

    def action_save_clicked(self):
        pass

    def action_save_as_clicked(self):
        path = QFileDialog.getSaveFileName(self, "Save schedule as xml file", "./examples", "XML file (*.xml)")[0]
        if path == "":
            return
        self.schedule.save(path + ".xml")

    def action_export_clicked(self):
        pass

    def action_about_clicked(self):
        pass

    def cell_clicked(self, index: QModelIndex):
        selector = PairSelectorWindow(self.schedule, index, self)
        selector.pairsListChanged.connect(self.update_table_widget)
        selector.exec_()
        self.update_table_widget()
