import sys
import time
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QProgressBar, QPushButton
from PyQt5.QtCore import Qt, QBasicTimer

class LoadingBarWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Initialize the UI
        self.initUI()

    def initUI(self):
        # Create a vertical layout
        layout = QVBoxLayout()

        # Create a progress bar
        self.progress = QProgressBar(self)
        self.progress.setGeometry(30, 40, 200, 25)
        self.progress.setAlignment(Qt.AlignCenter)  # Center the text in the bar
        layout.addWidget(self.progress)

        # Create a button to start the progress
        self.button = QPushButton('Start Loading', self)
        self.button.clicked.connect(self.startProgress)
        layout.addWidget(self.button)

        # Set layout and window properties
        self.setLayout(layout)
        self.setGeometry(300, 300, 280, 170)
        self.setWindowTitle('Loading Bar')

        # Timer for updating the progress bar
        self.timer = QBasicTimer()
        self.step = 0

    def timerEvent(self, e):
        if self.step >= 100:
            self.timer.stop()
            self.button.setText('Finished')
            return

        # Increment the progress
        self.step += 5 # this controls the progress bar
        self.progress.setValue(self.step)

    def startProgress(self):
        if self.timer.isActive():
            self.timer.stop()
            self.button.setText('Start Loading')
        else:
            self.timer.start(100, self)  # Timer interval of 100 ms
            self.button.setText('Stop')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = LoadingBarWindow()
    ex.show()
    sys.exit(app.exec_())