# coding: utf-8

# imports
from PyQt5.QtWidgets import QDialog, QWidget, QHBoxLayout, QVBoxLayout, \
                            QTextEdit, QPushButton, QLabel, QScrollArea, qApp, QSizePolicy

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QSyntaxHighlighter, QTextDocument,\
                        QTextCharFormat, QPixmap, QCloseEvent, QPalette, QImage, QWheelEvent

import re


class ConfuseWindow(QDialog):

    Nothing = 0
    NeededSolution = 1
    Work = 2
    Solved = 3

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.setWindowTitle(self.tr("Confuse window"))
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setWindowFlag(Qt.WindowTitleHint, True)
        self.setMinimumSize(800, 400)
        self.resize(qApp.desktop().screen().size() * 0.75)

        self.status = ConfuseWindow.Nothing
        self.index = 0
        self.answer = ""

        self.text_edit_confuse = QTextEdit("")
        self.highlighter_confuse = PairParserHighlighter(self.text_edit_confuse.document())

        self.text_edit_answer = QTextEdit("")
        self.highlighter_answer = PairParserHighlighter(self.text_edit_answer.document())

        self.push_button_ok = QPushButton(self.tr("OK"))

        self.image_viewer = ImageViewer()

        self.layout_down = QHBoxLayout()
        self.layout_down.addStretch(1)
        self.layout_down.addWidget(self.push_button_ok)

        self.layout_left = QVBoxLayout()
        self.layout_left.addWidget(self.text_edit_confuse)
        self.layout_left.addWidget(self.text_edit_answer)

        self.layout_center = QHBoxLayout()
        self.layout_center.addLayout(self.layout_left, 3)
        self.layout_center.addWidget(self.image_viewer, 2)

        self.layout_main = QVBoxLayout()
        self.layout_main.addLayout(self.layout_center)
        self.layout_main.addLayout(self.layout_down)

        self.setLayout(self.layout_main)

        # connection
        self.push_button_ok.clicked.connect(self.push_button_ok_clicked)

    def push_button_ok_clicked(self):
        self.answer = self.text_edit_answer.toPlainText()
        self.status = ConfuseWindow.Solved
        self.text_edit_confuse.clear()
        self.text_edit_answer.clear()
        super().close()

    def set_image(self, file_path):
        self.image_viewer.set_image(file_path)

    def closeEvent(self, a0: QCloseEvent) -> None:
        if self.status == ConfuseWindow.Work:
            self.status = ConfuseWindow.Nothing
        super().closeEvent(a0)


class PairParserHighlighter(QSyntaxHighlighter):
    def __init__(self, parent : QTextDocument = None):
        super().__init__(parent)
        self._formats = []
        colors = [Qt.darkGray, Qt.blue, Qt.green, Qt.darkYellow, Qt.darkMagenta, Qt.darkCyan, Qt.red]
        for color in colors:
            text_format = QTextCharFormat()
            text_format.setForeground(color)
            self._formats.append(text_format)

    def highlightBlock(self, text: str) -> None:
        from project.imports.import_logic import PairParser

        for match in re.finditer(PairParser.Pattern, text):
            for i, text_format in enumerate(self._formats, 1):
                group = match.group(i)
                if group is not None and i != 3:
                    self.setFormat(match.start(i), match.end(i) - match.start(i), text_format)


class ImageViewer(QWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self._scale_factor = 1
        self.scroll_area = QScrollArea()
        self.scroll_area.setBackgroundRole(QPalette.Dark)

        self.label_image = QLabel()
        self.label_image.setScaledContents(True)
        self.label_image.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.scroll_area.setWidget(self.label_image)

        self.push_button_zoom_in = QPushButton(self.tr("Zoom in"))
        self.push_button_zoom_out = QPushButton(self.tr("Zoom out"))

        self.layout_down = QHBoxLayout()
        self.layout_down.addStretch(1)
        self.layout_down.addWidget(self.push_button_zoom_in)
        self.layout_down.addWidget(self.push_button_zoom_out)

        self.layout_main = QVBoxLayout()
        self.layout_main.addWidget(self.scroll_area)
        self.layout_main.addLayout(self.layout_down)

        self.setLayout(self.layout_main)

        self.push_button_zoom_in.clicked.connect(self.push_button_zoom_in_clicked)
        self.push_button_zoom_out.clicked.connect(self.push_button_zoom_out_clicked)

    def set_image(self, file_path):
        image = QImage(file_path)
        self._scale_factor = 1
        self.label_image.setPixmap(QPixmap.fromImage(image))
        resize = self.label_image.pixmap().size()
        self.label_image.resize(resize / 4)

    def push_button_zoom_in_clicked(self):
        self._scale_factor *= 1.25
        self.label_image.resize(self._scale_factor
                                 * self.label_image.pixmap().size())
        if self._scale_factor > 3:
            self.push_button_zoom_in.setEnabled(False)
        if self._scale_factor > 0.3:
            self.push_button_zoom_out.setEnabled(True)

    def push_button_zoom_out_clicked(self):
        self._scale_factor *= 0.75
        self.label_image.resize(self._scale_factor
                                * self.label_image.pixmap().size())
        if self._scale_factor < 0.3:
            self.push_button_zoom_out.setEnabled(False)
        if self._scale_factor < 3:
            self.push_button_zoom_in.setEnabled(True)
