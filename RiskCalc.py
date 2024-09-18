import requests
import time
import pandas as pd
import glob
import random
import sys
import yaml

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QProgressBar, QPushButton, QScrollArea
from PyQt5.QtCore import Qt, QBasicTimer
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QMouseEvent

from LoadingWindow import LoadingWindow
from ClickableLabel import ClickableLabel

def retrieve_image():
    rng = random.randint(1, 4)
    match rng:
        case 1:
            name = 'catchest.png'
            path = 'icon pictures\\catchest.png'
        case 2:
            name = 'erm.png'
            path = 'icon pictures\\erm.png'
        case 3:
            name = 'nerd_cat.jpg'
            path = 'icon pictures\\nerd_cat.jpg'
        case 4:
            name = 'wetcat.png'
            path = 'icon pictures\\wetcat.png'
        
    return {'name':name,
            'path':path}
        
def create_file_GUI(file_path):
    file_layout = QVBoxLayout()
    image_info = retrieve_image()
    pixmap = QPixmap(image_info['path'])
     # need to check for scaling
    max_width = 75
    max_height = 75

    if pixmap.width() > max_width:
        pixmap = pixmap.scaled(max_width, pixmap.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                
    if pixmap.height() > max_height:
        pixmap = pixmap.scaled(pixmap.width(), max_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    picture_lbl = ClickableLabel(file_path)
    picture_lbl.setPixmap(pixmap)
    picture_lbl.resize(pixmap.width(), pixmap.height())

    txt_lbl = ClickableLabel(file_path)

    file_layout.addWidget(picture_lbl, alignment=Qt.AlignCenter)
    file_layout.addWidget(txt_lbl, alignment=Qt.AlignTop | Qt.AlignHCenter)

    return file_layout

def create_file_grid():
    container_widget = QWidget()
    file_grid = QGridLayout()
    grid_width = 3
    csv_files = glob.glob('spreadsheets\\*.csv')
    #print(csv_files)

    x = 0
    y = 0
    for i in range(len(csv_files)):
        # determine coordinates
        x = i % grid_width
        if i > 0 and x == 0:
            y+=1

        file_layout_cwidget = QWidget()
        file_layout = create_file_GUI(csv_files[i])
        file_layout_cwidget.setLayout(file_layout)
        #this is weird, but im adding something for it to not work
        #the purpose is to cancel the above stylesheet on inside items...
        
        file_layout_cwidget.setStyleSheet("""
            QWidget {
                border: 1px red;   /* Border thickness and color */
                border-radius: 3px;       /* Optional rounded corners */
                padding: 2px;             /* Space between border and contents */
            }
        """)
        file_grid.addWidget(file_layout_cwidget, y, x)


    container_widget.setLayout(file_grid)
    # Apply a style sheet to the container widget to add a border
    container_widget.setStyleSheet("""
            QWidget {
                border: 2px solid black;   /* Border thickness and color */
                border-radius: 3px;       /* Optional rounded corners */
                padding: 10px;             /* Space between border and contents */
            }
    """)
    return container_widget


def main():
    app = QApplication([])
    window = QWidget()

    main_layout = QVBoxLayout()
    window.setLayout(main_layout)
    window.setGeometry(0, 0, 800, 900)

    label = QLabel("Click the file you wish to check for malicious IPs")
    label.setFont(QFont('Arial',24))
    main_layout.addWidget(label, alignment=Qt.AlignTop | Qt.AlignHCenter)

    scroll_area = QScrollArea()
    scroll_area.setWidget(create_file_grid())
    scroll_area.setWidgetResizable(True)  # Allows the container widget to resize dynamically
    scroll_area.setFixedSize(650,600)
    main_layout.addWidget(scroll_area, alignment=Qt.AlignCenter | Qt.AlignTop)

    window.show()
    app.exec_()

main()