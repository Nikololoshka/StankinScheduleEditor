from PyQt5.QtWidgets import QWidget

class EditorWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Editor")