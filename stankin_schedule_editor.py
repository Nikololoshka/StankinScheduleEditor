# !/usr/bin/python3
# coding: utf-8

# imports
import sys
from PyQt5.QtWidgets import QApplication
from schedule_editor_window import ScheduleEditorWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    w = ScheduleEditorWindow()
    w.setWindowTitle("Schedule Editor")
    w.setMaximumSize(800, 600)
    w.show()

    sys.exit(app.exec_())
