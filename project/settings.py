# coding: utf-8

# imports
from PyQt5.QtWidgets import QWidget, QDialog, QGroupBox, QComboBox, QFormLayout, qApp, \
                            QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox
from PyQt5.QtCore import Qt, QSettings, QTranslator, QEvent

# importing resources
from res import resources


class SettingsWindow(QDialog):
    """
    Class describing the application settings window.
    """
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        # window settings
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setWindowTitle(self.tr("Settings window"))

        # language
        self.group_box_lang = QGroupBox(self.tr("Language"))
        self.form_layout_lang = QFormLayout(self.group_box_lang)

        self.label_app_lang = QLabel(self.tr("Application"))
        self.form_layout_lang.setWidget(0, QFormLayout.LabelRole, self.label_app_lang)
        self.combo_box_app_lang = QComboBox()
        self.form_layout_lang.setWidget(0, QFormLayout.FieldRole, self.combo_box_app_lang)

        self.label_sch_lang = QLabel(self.tr("Schedule"))
        self.form_layout_lang.setWidget(1, QFormLayout.LabelRole, self.label_sch_lang)
        self.combo_box_sch_lang = QComboBox()
        self.form_layout_lang.setWidget(1, QFormLayout.FieldRole, self.combo_box_sch_lang)

        languages = [("English", "en_US"), ("Русский", "ru_RU")]

        for lang_name, lang_code in languages:
            self.combo_box_app_lang.addItem(lang_name, lang_code)
            self.combo_box_sch_lang.addItem(lang_name, lang_code)

            if Settings.ApplicationLang == lang_code:
                self.combo_box_app_lang.setCurrentText(lang_name)

            if Settings.ScheduleLang == lang_code:
                self.combo_box_sch_lang.setCurrentText(lang_name)

        # schedule
        self.group_box_schedule = QGroupBox(self.tr("Schedule"))
        self.form_layout_schedule = QFormLayout(self.group_box_schedule)

        self.label_short_name = QLabel(self.tr("Short name"))
        self.form_layout_schedule.setWidget(0, QFormLayout.LabelRole, self.label_short_name)
        self.check_box_short_name = QCheckBox()
        self.form_layout_schedule.setWidget(0, QFormLayout.FieldRole, self.check_box_short_name)

        self.check_box_short_name.setChecked(Settings.ShortName)

        # navigate
        self.layout_navigate = QHBoxLayout()
        self.layout_navigate.addStretch(1)

        self.push_button_ok = QPushButton(self.tr("OK"))
        self.layout_navigate.addWidget(self.push_button_ok)

        self.push_button_apply = QPushButton(self.tr("Apply"))
        self.layout_navigate.addWidget(self.push_button_apply)

        self.push_button_cancel = QPushButton(self.tr("Cancel"))
        self.layout_navigate.addWidget(self.push_button_cancel)

        # layout setup
        self.layout_main = QVBoxLayout()

        self.layout_main.addWidget(self.group_box_lang)
        self.layout_main.addWidget(self.group_box_schedule)
        self.layout_main.addLayout(self.layout_navigate)

        self.setLayout(self.layout_main)

        # connection
        self.combo_box_app_lang.currentTextChanged.connect(self.application_lang_changed)
        self.combo_box_sch_lang.currentTextChanged.connect(self.schedule_lang_changed)

        self.check_box_short_name.clicked.connect(self.short_name_checked)

        self.push_button_ok.clicked.connect(self.close)
        self.push_button_apply.clicked.connect(self.close)
        self.push_button_cancel.clicked.connect(self.close)

    def changeEvent(self, event: QEvent) -> None:
        if event.type() == QEvent.LanguageChange:
            self.setWindowTitle(self.tr("Settings window"))

            self.group_box_lang.setTitle(self.tr("Language"))
            self.label_app_lang.setText(self.tr("Application"))
            self.label_sch_lang.setText(self.tr("Schedule"))

            self.push_button_ok.setText(self.tr("OK"))
            self.push_button_apply.setText(self.tr("Apply"))
            self.push_button_cancel.setText(self.tr("Cancel"))
        else:
            super().changeEvent(event)

    def application_lang_changed(self) -> None:
        """
        Method to change the application language.
        """
        Settings.ApplicationLang = self.combo_box_app_lang.currentData()

        translator = QTranslator()
        translator.load(":/translations/application_" +
                        Settings.ApplicationLang)

        qApp.removeTranslator(Settings.ApplicationTranslator)
        qApp.installTranslator(translator)
        Settings.ApplicationTranslator = translator

    def schedule_lang_changed(self) -> None:
        """
        Method to change the language of the schedule.
        """
        Settings.ScheduleLang = self.combo_box_sch_lang.currentData()

        translator = QTranslator()
        translator.load(":/translations/schedule_" +
                        Settings.ScheduleLang)

        qApp.removeTranslator(Settings.ScheduleTranslator)
        qApp.installTranslator(translator)
        Settings.ScheduleTranslator = translator

    def short_name_checked(self) -> None:
        """
        Method to change the display mode of names.
        """
        Settings.ShortName = int(self.check_box_short_name.isChecked())


class Settings:
    """
    Class describing the application settings.
    """
    ApplicationLang = "en_US"
    ScheduleLang = "en_US"
    ShortName = 0

    ApplicationTranslator = None
    ScheduleTranslator = None

    def __init__(self):
        Settings.load()

    def __del__(self):
        Settings.save()

    @staticmethod
    def load() -> None:
        """
        Loading settings.
        """
        settings = QSettings("settings.ini", QSettings.IniFormat)
        settings.beginGroup("Application")
        Settings.ApplicationLang = settings.value("application-lang", "en_US")
        Settings.ScheduleLang = settings.value("schedule-lang", "en_US")
        Settings.ShortName = int(settings.value("short-name", 0))
        settings.endGroup()

    @staticmethod
    def save() -> None:
        """
        Saving settings.
        """
        settings = QSettings("settings.ini", QSettings.IniFormat)
        settings.beginGroup("Application")
        settings.setValue("application-lang", Settings.ApplicationLang)
        settings.setValue("schedule-lang", Settings.ScheduleLang)
        settings.setValue("short-name", Settings.ShortName)
        settings.endGroup()
        settings.sync()
