from PyQt5.QtWidgets import *
import LoadingWindow
import re
from PyQt5.QtGui import QMouseEvent

from LoadingWindow import LoadingWindow

# custom class for enabling mouse press events for labels.
class ClickableLabel(QLabel):
    def __init__(self, file_path, parent=None):
        self.file_path = file_path
        self.popup = None

        pattern = r'\\(.+)$'
        match = re.search(pattern, file_path)
        super().__init__(match.group(1), parent)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == 1:  # Left mouse button
            print("File path: " + self.file_path)

            # create a new window for the loading/confirmation
            self.popup = LoadingWindow(self.file_path)
            self.popup.exec_()
        super().mousePressEvent(event)