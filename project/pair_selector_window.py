# coding: utf-8

# imports
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from project.schedule import Schedule
from project.pair_creator_window import PairCreatorWindow


class PairSelectorWindow(QDialog):
    """
    Class describing a dialog box to select the pair.
    """
    pairsListChanged = pyqtSignal()

    def __init__(self, scheduler_ref: Schedule, day, number, duration, parent: QWidget = None):
        super().__init__(parent)

        self._scheduler_ref = scheduler_ref
        self._day = day
        self._number = number
        self._duration = duration

        # window settings
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setWindowTitle(self.tr("Selector"))
        self.setMinimumSize(500, 300)

        # build and layout settings
        self.list_widget = QListWidget(self)
        self.list_widget.setWordWrap(True)
        self.list_widget.setSelectionMode(QAbstractItemView.SingleSelection)

        self.layout_horizontal = QHBoxLayout()

        self.layout_horizontal.addWidget(self.list_widget)
        self.layout_navigate = QVBoxLayout()

        self.push_button_new = QPushButton(self.tr("New"))
        self.layout_navigate.addWidget(self.push_button_new)

        self.push_button_edit = QPushButton(self.tr("Edit"))
        self.layout_navigate.addWidget(self.push_button_edit)

        self.push_button_remove = QPushButton(self.tr("Remove"))
        self.layout_navigate.addWidget(self.push_button_remove)

        self.push_button_cancel = QPushButton(self.tr("Cancel"))
        self.layout_navigate.addWidget(self.push_button_cancel)

        self.layout_navigate.addStretch(1)
        self.layout_horizontal.addLayout(self.layout_navigate)

        self.setLayout(self.layout_horizontal)
        self.setLayout(self.layout_horizontal)

        self.update_pairs_list()

        # connection
        self.list_widget.itemDoubleClicked.connect(self.push_button_edit_clicked)
        self.push_button_new.clicked.connect(self.push_button_new_clicked)
        self.push_button_edit.clicked.connect(self.push_button_edit_clicked)
        self.push_button_remove.clicked.connect(self.push_button_remove_clicked)
        self.push_button_cancel.clicked.connect(self.close)

    def update_pairs_list(self) -> None:
        """
        Updates the list of pairs in the window.
        """
        self.list_widget.clear()
        pairs = self._scheduler_ref.pairs_by_index(self._day, self._number, self._duration)
        for pair in pairs:
            item = QListWidgetItem(str(pair))
            item.setData(Qt.UserRole, pair)
            self.list_widget.addItem(item)

        self.pairsListChanged.emit()

    def remove_pair(self, item, back_mode: bool = False) -> None:
        """
        Removes a pair from the schedule.

        :param item: Selected object with pair
        :param back_mode: True - if the pair is deleted for editing
        """
        remove_pair = item.data(Qt.UserRole)
        self._scheduler_ref.remove_pair(remove_pair, back_mode)

    def push_button_new_clicked(self) -> None:
        """
        Slot to create a new pair.
        """
        creator = PairCreatorWindow(self._number, self)
        while True:
            creator.exec_()
            new_pair = creator.get_pair()
            if new_pair is not None:
                try:
                    self._scheduler_ref.add_pair(new_pair)
                    self.update_pairs_list()
                    break
                except Exception as ex:
                    QMessageBox.critical(self, self.tr("Invalid pair"), str(ex))
            else:
                break

    def push_button_edit_clicked(self) -> None:
        """
        Slot to edit the pair.
        """
        item = self.list_widget.currentItem()
        if item is None:
            QMessageBox.information(self, self.tr("Information"), self.tr("No pair selected"))
            return

        origin_pair = item.data(Qt.UserRole)
        self.remove_pair(item, True)

        creator = PairCreatorWindow(self._number, self)
        creator.set_pair(origin_pair.copy())

        while True:
            creator.exec_()
            edit_pair = creator.get_pair()
            if edit_pair is not None:
                try:
                    self._scheduler_ref.add_pair(edit_pair)
                    self.update_pairs_list()
                    break
                except Exception as ex:
                    QMessageBox.critical(self, self.tr("Invalid pair"), str(ex))
            else:
                self._scheduler_ref.add_pair(origin_pair, True)
                break

    def push_button_remove_clicked(self) -> None:
        """
        Slot to remove the pair.
        """
        item = self.list_widget.currentItem()
        if item is None:
            QMessageBox.information(self, self.tr("Information"), self.tr("No pair selected"))
            return

        self.remove_pair(item)
        self.update_pairs_list()
