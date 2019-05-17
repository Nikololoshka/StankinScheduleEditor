# coding: utf-8

# imports
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


def compute_font_for_text(text: str, flags: int, size: QSize) -> QFont:
    font = qApp.font()
    for i in range(1, 14):
        font.setPixelSize(i)
        rect = QFontMetrics(font).boundingRect(0, 0, size.width(), size.height(), flags, text)
        if rect.width() > size.width() or rect.height() > size.height():
            font.setPixelSize(i - 1)
            break

    return font


class CustomHeaderView(QHeaderView):
    def __init__(self, orientation):
        super().__init__(orientation)

    def paintSection(self, painter, rect, index):
        super().paintSection(painter, rect, -1)
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
