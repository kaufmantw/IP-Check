import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QScrollArea, QPushButton

class ScrollableWidgetExample(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Create a QVBoxLayout and add some widgets to it
        layout = QVBoxLayout()
        for i in range(2):  # Add many buttons to demonstrate scrolling
            layout.addWidget(QPushButton(f"Button {i+1}"))

        # Create a container widget and set the layout
        container_widget = QWidget()
        container_widget.setLayout(layout)

        # Create a QScrollArea and set the container widget inside it
        scroll_area = QScrollArea()
        scroll_area.setWidget(container_widget)
        scroll_area.setWidgetResizable(True)  # Allows the container widget to resize dynamically

        # Optionally, you can limit the maximum size of the scrollable area
        scroll_area.setMaximumHeight(200)  # Set max height for scrolling
        scroll_area.setMaximumWidth(300)   # Set max width for scrolling

        # Create the main layout for the window and add the scroll area
        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll_area)

        self.setLayout(main_layout)

        # Set window properties
        self.setWindowTitle('Scrollable Widget Example')
        self.setGeometry(300, 300, 400, 300)
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ScrollableWidgetExample()
    sys.exit(app.exec_())