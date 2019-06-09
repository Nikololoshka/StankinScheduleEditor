# coding: utf-8

# imports
from PyQt5.QtWidgets import QHeaderView, QMainWindow, QTableWidget, QAbstractItemView, \
                            QSizePolicy, QTableWidgetItem, QAction, qApp, \
                            QFileDialog, QMessageBox, QMenu
from PyQt5.QtCore import QRectF, Qt, QSize, QFileInfo, QPoint, QEvent
from PyQt5.QtGui import QFont, QFontMetrics, QIcon, QResizeEvent

from project.pair_selector_window import PairSelectorWindow
from project.export_window import ExportWindow
from project.settings import SettingsWindow
from project.schedule import Schedule
from project.pair import DaysOfWeek
from project import defaults


def compute_font_for_text(text: str, flags: int, size: QSize) -> QFont:
    """
    Calculates the font for the text for the area of the specified dimensions.
    Returns the font
    """
    font = qApp.font()
    for i in range(1, 14):
        font.setPixelSize(i)
        rect = QFontMetrics(font).boundingRect(0, 0, size.width(), size.height(), flags, text)
        if rect.width() > size.width() or rect.height() > size.height():
            font.setPixelSize(i - 1)
            break

    return font


class CustomHeaderView(QHeaderView):
    """ HeaderView class with vertical text support """
    def __init__(self, orientation):
        super().__init__(orientation)

    def paintSection(self, painter, rect, index) -> None:
        painter.save()
        if self.orientation() == Qt.Vertical:
            painter.translate(rect.x() + rect.width(), rect.y() + rect.height())
            painter.rotate(-90)
            painter.drawText(QRectF(0, 0, rect.height(), -rect.width()),
                             Qt.AlignCenter,
                             self.model().headerData(index, self.orientation(), Qt.DisplayRole))
        else:
            painter.drawText(QRectF(rect.x(), rect.y(), rect.width(), rect.height()),
                             Qt.AlignCenter,
                             self.model().headerData(index, self.orientation(), Qt.DisplayRole))
        painter.restore()


class ScheduleEditorWindow(QMainWindow):
    """ Class describing the main window of the program """
    def __init__(self):
        super().__init__()

        self.schedule = Schedule()
        self.file = None

        # window settings
        self.setWindowTitle(self.tr("Schedule Editor"))
        self.setMinimumSize(800, 600)

        # central widget settings
        self.table_widget = QTableWidget()
        self.table_widget.setVerticalHeader(CustomHeaderView(Qt.Vertical))
        self.table_widget.setHorizontalHeader(CustomHeaderView(Qt.Horizontal))
        self.table_widget.setWordWrap(True)
        self.table_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_widget.setSelectionMode(QAbstractItemView.SingleSelection)
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
        self.menu_bar = self.menuBar()
        self.menu_file = self.menu_bar.addMenu(self.tr("&File"))

        self.action_new_file = QAction(QIcon.fromTheme("document-new"), self.tr("&New file"), self)
        self.action_new_file.setShortcut("Ctrl+N")
        self.menu_file.addAction(self.action_new_file)

        self.action_open = QAction(QIcon.fromTheme("document-open"), self.tr("&Open"), self)
        self.action_open.setShortcut("Ctrl+O")
        self.menu_file.addAction(self.action_open)

        self.action_save = QAction(QIcon.fromTheme("document-save"), self.tr("&Save"), self)
        self.action_save.setShortcut("Ctrl+S")
        self.menu_file.addAction(self.action_save)

        self.action_save_as = QAction(QIcon.fromTheme("document-save-as"), self.tr("Save as..."), self)
        self.action_save_as.setShortcut("Ctrl+S+A")
        self.menu_file.addAction(self.action_save_as)

        self.action_export = QAction(self.tr("Export"), self)
        self.action_export.setShortcut("Ctrl+E")
        self.menu_file.addAction(self.action_export)

        self.menu_file.addSeparator()

        self.action_settings = QAction(self.tr("Settings"), self)
        self.menu_file.addAction(self.action_settings)

        self.action_about = QAction(self.tr("About"), self)
        self.menu_file.addAction(self.action_about)

        self.action_exit = QAction(self.tr("&Quit"), self)
        self.action_exit.setShortcut("Ctrl+Q")
        self.menu_file.addAction(self.action_exit)

        # status bar settings
        self.statusBar().showMessage(self.tr("Ready!"))

        # connection
        self.action_new_file.triggered.connect(self.action_new_file_clicked)
        self.action_open.triggered.connect(self.action_open_clicked)
        self.action_save.triggered.connect(self.action_save_clicked)
        self.action_save_as.triggered.connect(self.action_save_as_clicked)
        self.action_export.triggered.connect(self.action_export_clicked)
        self.action_settings.triggered.connect(self.action_settings_clicked)
        self.action_about.triggered.connect(self.action_about_clicked)
        self.action_exit.triggered.connect(self.close)

        self.table_widget.doubleClicked.connect(self.cell_clicked)
        self.table_widget.customContextMenuRequested.connect(self.context_menu_requested)

    def changeEvent(self, event: QEvent) -> None:
        if event.type() == QEvent.LanguageChange:
            self.setWindowTitle(self.tr("Schedule Editor"))
            self.menu_file.setTitle(self.tr("&File"))
            self.action_new_file.setText(self.tr("&New file"))
            self.action_open.setText(self.tr("&Open"))
            self.action_save.setText(self.tr("&Save"))
            self.action_save_as.setText(self.tr("Save as..."))
            self.action_export.setText(self.tr("Export"))
            self.action_settings.setText(self.tr("Settings"))
            self.action_about.setText(self.tr("About"))
            self.action_exit.setText(self.tr("&Quit"))

            for i, day in enumerate(DaysOfWeek.to_list()):
                item = QTableWidgetItem(day)
                self.table_widget.setVerticalHeaderItem(i, item)

            self.update_table_widget()
        else:
            super().changeEvent(event)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        self.update_table_widget()
        super().resizeEvent(a0)

    def context_menu_requested(self, pos: QPoint) -> None:
        """ Create a context menu to edit a table cell """
        menu = QMenu(self)

        action_edit = QAction(QIcon.fromTheme("accessories-text-editor"), self.tr("Edit cell"), self)
        action_edit.triggered.connect(self.cell_clicked)
        menu.addAction(action_edit)

        menu.popup(self.table_widget.viewport().mapToGlobal(pos))

    def update_table_widget(self) -> None:
        """ Updates the schedule table """
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
        """ Returns the size of the cell """
        return QSize(self.table_widget.columnWidth(column),
                     self.table_widget.rowHeight(row))

    def action_new_file_clicked(self) -> bool:
        """
        Slot to handle file save, after changes.
        If the user has agreed to save / not save, then True is returned, otherwise False.
        """
        if self.schedule.is_change():
            answer = QMessageBox.warning(self,
                                         self.tr("The document has been modified"),
                                         self.tr("Do you want to save the changes you made?\n"
                                                 "You changes will be lost if you don't save them"),
                                         QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                                         QMessageBox.Save
                                         )
            if answer == QMessageBox.Save:
                self.action_save_clicked()
            elif answer == QMessageBox.Cancel:
                return False

        self.schedule.clear()
        self.update_table_widget()
        self.setWindowTitle(self.tr("Schedule Editor"))
        return True

    def action_open_clicked(self) -> None:
        """ Slot to handle file upload. """
        if self.file is not None:
            if not self.action_new_file_clicked():
                return

        path = QFileDialog.getOpenFileName(self,
                                           self.tr("Open schedule from XML file"),
                                           ".",
                                           "XML file (*.xml)")[0]
        if path == "":
            return

        self.schedule.load(path)
        self.file = QFileInfo(path)
        self.statusBar().showMessage(self.tr("Load file: ") + path, 5000)
        self.setWindowTitle(self.tr("Schedule Editor [{}]").format(self.file.absoluteFilePath()))
        self.update_table_widget()

    def action_save_clicked(self) -> None:
        """ Slot to handle file saving. """
        if self.file is None:
            self.action_save_as_clicked()
        else:
            self.schedule.save(self.file.absoluteFilePath())
            self.setWindowTitle(self.tr("Schedule Editor [{}]").format(self.file.absoluteFilePath()))
            self.statusBar().showMessage(self.tr("Save file: ") + self.file.absoluteFilePath(), 5000)

    def action_save_as_clicked(self) -> None:
        """ Slot to save the file if it has not been saved before """
        path = QFileDialog.getSaveFileName(self,
                                           self.tr("Save schedule as XML file"),
                                           "./examples",
                                           "XML file (*.xml)")[0]
        if path == "":
            return

        if not path.endswith(".xml"):
            path += ".xml"

        self.schedule.save(path)
        self.file = QFileInfo(path)
        self.setWindowTitle(self.tr("Schedule Editor [{}]").format(self.file.absoluteFilePath()))
        self.statusBar().showMessage(self.tr("Save file: ") + self.file.absoluteFilePath(), 5000)

    def action_export_clicked(self) -> None:
        """ Slot for schedule export to PDF """
        exporter = ExportWindow(self.schedule, self)
        exporter.exec_()

    def action_settings_clicked(self) -> None:
        settings = SettingsWindow(self)
        settings.exec_()

    def action_about_clicked(self) -> None:
        """ Slot display window: "About program" """
        QMessageBox.information(self,
                                self.tr("About program"),
                                self.tr("""
                                    <b>Stankin Schedule Editor</b>
                                    <p>
                                        The project is designed to create a weekly
                                        schedule in the form of pdf-files.
                                    <p>
                                    <p>
                                        <b>Author</b>: Nick Vereshchagin<br>
                                        <b>GitHub</b>:
                                        <a href='https://github.com/Nikololoshka/StankinScheduleEditor'>
                                            https://github.com/Nikololoshka/StankinScheduleEditor
                                        </a>
                                    </p>
                                """))

    def cell_clicked(self) -> None:
        """ Processes the action to change a table cell """
        index = self.table_widget.currentIndex()
        selector = PairSelectorWindow(self.schedule, index, self)
        selector.pairsListChanged.connect(self.update_table_widget)
        selector.exec_()
        self.update_table_widget()
