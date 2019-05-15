# coding: utf-8

# imports
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from schedule import Schedule
from pair import StudentPair
from pair_creator_window import PairCreatorWindow


class PairSelectorWindow(QDialog):

    pairsListChanged = pyqtSignal()
    SaveRole = Qt.UserRole + 1

    def __init__(self, scheduler_ref: Schedule, index: QModelIndex, parent: QWidget = None):
        super().__init__(parent)

        self.scheduler_ref = scheduler_ref
        self.index = index

        # window settings
        self.setWindowTitle("Selector")
        self.setMinimumSize(500, 300)

        # build and layout settings
        self.list_widget = QListWidget(self)
        self.list_widget.setWordWrap(True)
        self.list_widget.setSelectionMode(QAbstractItemView.SingleSelection)

        horizontal_layout = QHBoxLayout(self)

        horizontal_layout.addWidget(self.list_widget)
        vertical_layout = QVBoxLayout()

        self.push_button_new = QPushButton("New", self)
        vertical_layout.addWidget(self.push_button_new)

        self.push_button_edit = QPushButton("Edit", self)
        vertical_layout.addWidget(self.push_button_edit)

        self.push_button_remove = QPushButton("Remove", self)
        vertical_layout.addWidget(self.push_button_remove)

        self.push_button_cancel = QPushButton("Cancel", self)
        vertical_layout.addWidget(self.push_button_cancel)

        vertical_layout.addStretch(1)
        horizontal_layout.addLayout(vertical_layout)

        self.update_pairs_list()

        # connection
        self.list_widget.itemDoubleClicked.connect(self.push_button_edit_clicked)
        self.push_button_new.clicked.connect(self.push_button_new_clicked)
        self.push_button_edit.clicked.connect(self.push_button_edit_clicked)
        self.push_button_remove.clicked.connect(self.push_button_remove_clicked)
        self.push_button_cancel.clicked.connect(self.close)

    def update_pairs_list(self):
        self.list_widget.clear()
        pairs = self.scheduler_ref.pairs_by_index(self.index.row(), self.index.column())
        for pair in pairs:
            item = QListWidgetItem(str(pair))
            item.setData(PairSelectorWindow.SaveRole, pair)
            self.list_widget.addItem(item)

        self.pairsListChanged.emit()

    def remove_pair(self, item):
        remove_pair = item.data(PairSelectorWindow.SaveRole)
        pairs = self.scheduler_ref.pairs_by_index(self.index.row(), self.index.column())
        for pair in pairs:
            if pair == remove_pair:
                pairs.remove(pair)
                break

    def push_button_new_clicked(self):
        new_pair = StudentPair()
        creator = PairCreatorWindow(self.scheduler_ref, self.index, new_pair, self)
        creator.pairChanged.connect(self.update_pairs_list)
        creator.exec_()

        self.scheduler_ref.add_pair(new_pair)
        self.update_pairs_list()

    def push_button_edit_clicked(self):
        item = self.list_widget.currentItem()
        if item is None:
            QMessageBox.information(self, "Information", "No pair selected")
            return

        edit_pair = item.data(PairSelectorWindow.SaveRole)
        self.remove_pair(item)

        creator = PairCreatorWindow(self.scheduler_ref, self.index, edit_pair, self)
        creator.pairChanged.connect(self.update_pairs_list)
        creator.exec_()

        self.scheduler_ref.add_pair(edit_pair)
        self.update_pairs_list()

    def push_button_remove_clicked(self):
        item = self.list_widget.currentItem()
        if item is None:
            QMessageBox.information(self, "Information", "No pair selected")
            return

        self.remove_pair(item)
        self.update_pairs_list()
