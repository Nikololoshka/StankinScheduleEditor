# coding: utf-8

# imports
from PyQt5.QtWidgets import QHeaderView, QMainWindow, QTableWidget, QAbstractItemView, \
                            QSizePolicy, QTableWidgetItem, QAction, qApp, \
                            QFileDialog, QMessageBox, QMenu
from PyQt5.QtCore import QRectF, Qt, QSize, QFileInfo, QPoint, QEvent
from PyQt5.QtGui import QFont, QFontMetrics, QIcon, QResizeEvent

from project.pair_selector_window import PairSelectorWindow
from project.exports.export_window import ExportWindow
from project.imports.import_window import ImportWindow
from project.settings import SettingsWindow
from project.schedule import Schedule, AlongTwoPairsException
from project.pair import DaysOfWeek, TimePair


def compute_font_for_text(text: str, flags: int, size: QSize) -> QFont:
    """
    Calculates the font for the text for the area of the specified dimensions

    :param text: input text
    :param flags: the alignment flags of the text
    :param size: the size of the area
    :return: QFont
    """
    font = qApp.font()
    for i in range(2, 14):
        font.setPixelSize(i)
        rect = QFontMetrics(font).boundingRect(0, 0, size.width(), size.height(), flags, text)
        if rect.width() > size.width() or rect.height() > size.height():
            font.setPixelSize(i - 1)
            break

    return font


class CustomHeaderView(QHeaderView):
    """
    HeaderView class with vertical text support
    """
    def __init__(self, orientation, indexes: list = None):
        super().__init__(orientation)
        self._indexes_ref = indexes

    def paintSection(self, painter, rect, index) -> None:
        painter.save()
        if self.orientation() == Qt.Vertical:
            new_index = index
            for i, value in enumerate(self._indexes_ref):
                new_index -= value
                if new_index < 0:
                    index = new_index + value + 1
                    new_index = i
                    break

            delta = self._indexes_ref[new_index] - index
            index = self._indexes_ref[new_index]
            data = self.model().headerData(new_index, self.orientation(), Qt.DisplayRole)
            painter.translate(rect.x() + rect.width(), rect.y() + rect.height())
            painter.rotate(-90)
            painter.drawText(QRectF(-rect.height() * delta, 0, rect.height() * index, -rect.width()),
                             Qt.AlignCenter,
                             data)

        else:
            painter.drawText(QRectF(rect.x(), rect.y(), rect.width(), rect.height()),
                             Qt.AlignCenter,
                             self.model().headerData(index, self.orientation(), Qt.DisplayRole))
        painter.restore()


class ScheduleTableWidget(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._schedule_ref = None
        self._indexes_ref = None

    def set_schedule(self, schedule: Schedule):
        self._schedule_ref = schedule
        self._indexes_ref = self._schedule_ref.indexes()
        self.update_schedule()

    def update_schedule(self) -> None:
        self.clearSpans()
        self.clearContents()

        rows = self._schedule_ref.rows()
        columns = self._schedule_ref.columns()

        self.setRowCount(rows)
        self.setColumnCount(columns)

        i = 0
        for day_number, schedule_element in enumerate(self._schedule_ref):
            min_i = i
            for line in schedule_element:
                j = 0
                while j < columns:
                    text = ""
                    duration = 1

                    pairs = line.get(j)
                    if pairs is not None:
                        duration = pairs[0]["time"].duration()
                        for pair in pairs:
                            text += str(pair) + "\n"

                    item = QTableWidgetItem(text)
                    item.setTextAlignment(Qt.AlignTop | Qt.AlignLeft)
                    item.setData(Qt.UserRole, duration)
                    self.setItem(i, j, item)

                    j += duration
                i += 1

            for n in range(columns):
                for m in range(i - 1, min_i - 1, -1):
                    item = self.item(m, n)
                    if item is not None:
                        up_level, down_level = m, m
                        duration = item.data(Qt.UserRole)
                        # down
                        for p in range(m + 1, i):
                            free = True
                            for r in range(duration):
                                cmp_item = self.item(p, n + r)
                                if cmp_item is None or cmp_item.text() != "":
                                    free = False
                                    break
                            if free:
                                down_level = p
                                for r in range(duration):
                                    self.takeItem(p, n + r)
                            else:
                                break
                        # up
                        for p in range(m - 1, min_i - 1, -1):
                            free = True
                            for r in range(duration):
                                cmp_item = self.item(p, n + r)
                                if cmp_item is None or cmp_item.text() != "":
                                    free = False
                                    break
                            if free:
                                up_level = p
                                for r in range(duration):
                                    self.takeItem(p, n + r)
                            else:
                                break

                        if (abs(up_level - down_level) + 1) > 1 or duration > 1:
                            if self.columnSpan(up_level, n) == 1 or \
                                    self.rowSpan(up_level, n) == 1:
                                self.setItem(up_level,
                                             n,
                                             self.takeItem(m, n))
                                self.setSpan(up_level,
                                             n,
                                             abs(up_level - down_level) + 1,
                                             duration)

        self.resize_table()

    def resize_table(self):
        simple_row = (self.height() - self.horizontalHeader().height()) / 6
        for i in range(self.rowCount()):
            new_index = i
            for k, value in enumerate(self._indexes_ref):
                new_index -= value
                if new_index < 0:
                    new_index = k
                    break
            size = int(simple_row / self._indexes_ref[new_index])
            self.verticalHeader().resizeSection(i, size)

        for i in range(self.rowCount()):
            for j in range(self.columnCount()):
                item = self.item(i, j)
                if item is not None:
                    size = QSize(self.columnWidth(item.column()) *
                                 self.columnSpan(item.row(), item.column()),
                                 self.rowHeight(item.row()) *
                                 self.rowSpan(item.row(), item.column()))
                    item.setFont(compute_font_for_text(item.text(),
                                                       Qt.AlignTop | Qt.AlignLeft | Qt.TextWordWrap,
                                                       size))

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.resize_table()
        super().resizeEvent(event)


class ScheduleEditorWindow(QMainWindow):
    """
    Class describing the main window of the program.
    """
    def __init__(self):
        super().__init__()

        self._schedule = Schedule()
        self._indexes_ref = self._schedule.indexes()
        self._file = None

        # window settings
        self.setWindowTitle(self.tr("Schedule Editor"))
        self.setMinimumSize(800, 600)

        # central widget settings
        self.table_widget = ScheduleTableWidget()
        self.table_widget.set_schedule(self._schedule)
        self.table_widget.setVerticalHeader(CustomHeaderView(Qt.Vertical, self._indexes_ref))
        self.table_widget.setHorizontalHeader(CustomHeaderView(Qt.Horizontal))
        self.table_widget.setWordWrap(True)
        self.table_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_widget.horizontalHeader().setMaximumHeight(25)
        self.table_widget.horizontalHeader().setStretchLastSection(True)
        self.table_widget.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.table_widget.verticalHeader().setMaximumWidth(25)
        self.table_widget.verticalHeader().setStretchLastSection(True)
        self.table_widget.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.table_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.table_widget.setColumnCount(self._schedule.columns())
        for i in range(8):
            item = QTableWidgetItem(TimePair.time_start_end(i))
            self.table_widget.setHorizontalHeaderItem(i, item)

        self.table_widget.setRowCount(self._schedule.rows())
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

        self.action_import = QAction(self.tr("Import"), self)
        self.action_import.setShortcut("Ctrl+I")
        self.menu_file.addAction(self.action_import)

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
        self.action_import.triggered.connect(self.action_import_clicked)
        self.action_settings.triggered.connect(self.action_settings_clicked)
        self.action_about.triggered.connect(self.action_about_clicked)
        self.action_exit.triggered.connect(self.close)

        # self.table_widget.clicked.connect(self.test)
        self.table_widget.doubleClicked.connect(self.cell_clicked)
        self.table_widget.customContextMenuRequested.connect(self.context_menu_requested)

    # def test(self) -> None:
    #     """
    #     Method for tests.
    #     """
    #     item = self.table_widget.currentItem()
    #     if item is not None:
    #         print(item.row(),
    #               item.column(),
    #               self.table_widget.rowSpan(item.row(), item.column()),
    #               self.table_widget.columnSpan(item.row(), item.column()))

    def changeEvent(self, event: QEvent) -> None:
        if event.type() == QEvent.LanguageChange:
            self.setWindowTitle(self.tr("Schedule Editor"))
            self.menu_file.setTitle(self.tr("&File"))
            self.action_new_file.setText(self.tr("&New file"))
            self.action_open.setText(self.tr("&Open"))
            self.action_save.setText(self.tr("&Save"))
            self.action_save_as.setText(self.tr("Save as..."))
            self.action_export.setText(self.tr("Export"))
            self.action_import.setText(self.tr("Import"))
            self.action_settings.setText(self.tr("Settings"))
            self.action_about.setText(self.tr("About"))
            self.action_exit.setText(self.tr("&Quit"))

            for i, day in enumerate(DaysOfWeek.to_list()):
                item = QTableWidgetItem(day)
                self.table_widget.setVerticalHeaderItem(i, item)

            self.table_widget.update_schedule()
        else:
            super().changeEvent(event)

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.table_widget.resize_table()
        super().resizeEvent(event)

    def context_menu_requested(self, pos: QPoint) -> None:
        """
        Create a context menu to edit a table cell.

        :param pos: Menu call position
        """
        menu = QMenu(self)

        action_edit = QAction(QIcon.fromTheme("accessories-text-editor"), self.tr("Edit cell"), self)
        action_edit.triggered.connect(self.cell_clicked)
        menu.addAction(action_edit)

        menu.popup(self.table_widget.viewport().mapToGlobal(pos))

    def action_new_file_clicked(self) -> bool:
        """
        Slot to handle file save, after changes.
        If the user has agreed to save / not save, then True is returned, otherwise False.
        """
        if self._schedule.is_change():
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

        self._schedule.clear()
        self.table_widget.update_schedule()
        self.setWindowTitle(self.tr("Schedule Editor"))
        return True

    def action_open_clicked(self) -> None:
        """
        Slot to handle file upload.
        """
        if self._file is not None:
            if not self.action_new_file_clicked():
                return

        path = QFileDialog.getOpenFileName(self,
                                           self.tr("Open schedule from JSON file"),
                                           ".",
                                           "JSON file (*.json)")[0]
        if path == "":
            return

        try:
            self._schedule.load(path)
        except AlongTwoPairsException as ex:
            QMessageBox.critical(self,
                                 self.tr("AlongTwoPairsException!"),
                                 str(ex))
            return
        except Exception as ex:
            QMessageBox.critical(self,
                                 self.tr("Unknown error!"),
                                 str(ex))
            return

        self._file = QFileInfo(path)
        self.statusBar().showMessage(self.tr("Load file: ") + path, 5000)
        self.setWindowTitle(self.tr("Schedule Editor [{}]").format(self._file.absoluteFilePath()))
        self.table_widget.update_schedule()

    def action_save_clicked(self) -> None:
        """
        Slot to handle file saving.
        """
        if self._file is None:
            self.action_save_as_clicked()
        else:
            self._schedule.save(self._file.absoluteFilePath())
            self.setWindowTitle(self.tr("Schedule Editor [{}]").format(self._file.absoluteFilePath()))
            self.statusBar().showMessage(self.tr("Save file: ") + self._file.absoluteFilePath(), 5000)

    def action_save_as_clicked(self) -> None:
        """
        Slot to save the file if it has not been saved before.
        """
        path = QFileDialog.getSaveFileName(self,
                                           self.tr("Save schedule as JSON file"),
                                           "./examples",
                                           "JSON file (*.json)")[0]
        if path == "":
            return

        if not path.endswith(".json"):
            path += ".json"

        self._schedule.save(path)
        self._file = QFileInfo(path)
        self.setWindowTitle(self.tr("Schedule Editor [{}]").format(self._file.absoluteFilePath()))
        self.statusBar().showMessage(self.tr("Save file: ") + self._file.absoluteFilePath(), 5000)

    def action_export_clicked(self) -> None:
        """
        Slot for schedule exports to PDF.
         """
        exporter = ExportWindow(self._schedule, self)
        exporter.exec_()

    def action_import_clicked(self) -> None:
        """
        Slot for schedule imports from PDF.
        """
        importer = ImportWindow(self)
        importer.exec_()

    def action_settings_clicked(self) -> None:
        """
        Slot for calling up the settings window.
        """
        settings = SettingsWindow(self)
        settings.exec_()

        self.table_widget.update_schedule()

    def action_about_clicked(self) -> None:
        """
        Slot display window: "About program".
        """
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
        """
        Processes the action to change a table cell.
        """
        day = self.table_widget.currentRow()
        number = self.table_widget.currentColumn()

        item = self.table_widget.currentItem()
        if item is not None:
            duration = item.data(Qt.UserRole)
        else:
            duration = self.table_widget.columnSpan(day, number)

        day, number, duration = self._schedule.normalize_index(day, number, duration)

        selector = PairSelectorWindow(self._schedule, day, number, duration, self)
        selector.pairsListChanged.connect(self.table_widget.update_schedule)
        selector.exec_()

        self.table_widget.update_schedule()
