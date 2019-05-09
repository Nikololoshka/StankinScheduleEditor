# coding: utf-8

# imports
from PyQt5.QtWidgets import qApp, QHeaderView
from PyQt5.QtCore import Qt, QSize, QRect, QPoint
from PyQt5.QtGui import QFont, QFontMetrics


def compute_font_for_text(text: str, flags: int, size: QSize) -> QFont:
    font = qApp.font()
    for i in range(1, 18):
        font.setPixelSize(i)
        rect = QFontMetrics(font).boundingRect(0, 0, size.width(), size.height(), flags, text)
        if rect.width() > size.width() or rect.height() > size.height():
            font.setPixelSize(i - 1)
            break

    return font


class MyHeaderView(QHeaderView):
    def __init__(self):
        super().__init__(Qt.Vertical)

    def paintSection(self, painter, rect, index):
        super().paintSection(painter, rect, index)
