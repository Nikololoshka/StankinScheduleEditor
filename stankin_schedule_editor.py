# !/usr/bin/python3
# utf-8

import sys
from PyQt5.QtWidgets import QApplication
from editor_window import EditorWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    w = EditorWindow()
    w.show()

    sys.exit(app.exec_())
