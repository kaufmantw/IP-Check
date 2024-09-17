from PyQt5.QtWidgets import *
import LoadingWindow
from PyQt5.QtGui import QMouseEvent

from LoadingWindow import LoadingWindow

# custom class for enabling mouse press events for labels.
class ClickableLabel(QLabel):
    def __init__(self, file_path, parent=None):
        self.file_path = file_path
        self.popup = None
        super().__init__(file_path, parent)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == 1:  # Left mouse button
            print("File path: " + self.file_path)

            # create a new window for the loading/confirmation
            self.popup = LoadingWindow(self.file_path)
            self.popup.exec_()
        super().mousePressEvent(event)