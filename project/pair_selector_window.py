# coding: utf-8

# imports
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from project.schedule import Schedule
from project.pair_creator_window import PairCreatorWindow


class PairSelectorWindow(QDialog):

    pairsListChanged = pyqtSignal()

    def __init__(self, scheduler_ref: Schedule, index: QModelIndex, parent: QWidget = None):
        super().__init__(parent)

        self.scheduler_ref = scheduler_ref
        self.index = index

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
            item.setData(Qt.UserRole, pair)
            self.list_widget.addItem(item)

        self.pairsListChanged.emit()

    def remove_pair(self, item):
        remove_pair = item.data(Qt.UserRole)
        self.scheduler_ref.remove_pair(self.index.row(), self.index.column(), remove_pair)

    def push_button_new_clicked(self):
        creator = PairCreatorWindow(self.index, self)
        while True:
            creator.exec_()
            new_pair = creator.get_pair()
            if new_pair is not None:
                try:
                    self.scheduler_ref.add_pair(new_pair)
                    self.update_pairs_list()
                    break
                except Exception as ex:
                    QMessageBox.critical(self, self.tr("Invalid pair"), str(ex))
            else:
                break

    def push_button_edit_clicked(self):
        item = self.list_widget.currentItem()
        if item is None:
            QMessageBox.information(self, self.tr("Information"), self.tr("No pair selected"))
            return

        origin_pair = item.data(Qt.UserRole)
        self.remove_pair(item)

        creator = PairCreatorWindow(self.index, self)
        creator.set_pair(origin_pair.copy())

        while True:
            creator.exec_()
            edit_pair = creator.get_pair()
            if edit_pair is not None:
                try:
                    self.scheduler_ref.add_pair(edit_pair)
                    self.update_pairs_list()
                    break
                except Exception as ex:
                    QMessageBox.critical(self, self.tr("Invalid pair"), str(ex))
            else:
                self.scheduler_ref.add_pair(origin_pair)
                break

    def push_button_remove_clicked(self):
        item = self.list_widget.currentItem()
        if item is None:
            QMessageBox.information(self, self.tr("Information"), self.tr("No pair selected"))
            return

        self.remove_pair(item)
        self.update_pairs_list()
