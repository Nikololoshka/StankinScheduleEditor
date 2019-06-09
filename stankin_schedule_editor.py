# !/usr/bin/python3
# coding: utf-8

# imports
import sys

from PyQt5.QtCore import QTranslator
from PyQt5.QtWidgets import QApplication

from project.schedule_editor_window import ScheduleEditorWindow
from project.settings import Settings

from res import resources

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Load settings
    app_settings = Settings()

    # translation settings
    app_translator = QTranslator()
    app_translator.load(":/translations/application_" +
                        Settings.ApplicationLang)

    schedule_translator = QTranslator()
    schedule_translator.load(":/translations/schedule_" +
                             Settings.ScheduleLang)

    app.installTranslator(app_translator)
    app.installTranslator(schedule_translator)

    Settings.ApplicationTranslator = app_translator
    Settings.ScheduleTranslator = schedule_translator

    # application setup
    w = ScheduleEditorWindow()
    w.show()

    sys.exit(app.exec_())
