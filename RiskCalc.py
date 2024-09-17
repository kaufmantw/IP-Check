import requests
import time
import pandas as pd
import glob
import random

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QProgressBar, QPushButton, QScrollArea
from PyQt5.QtCore import Qt, QBasicTimer
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QMouseEvent

class LoadingWindow(QDialog):
    def __init__(self, file_path, parent=None):
        self.file_path = file_path
        super().__init__()

        self.initUI()

    def initUI(self):
        self.progress = QProgressBar(self)

        self.confirm_button = QPushButton('Press to Confirm')
        self.confirm_button.clicked.connect(self.startProgress)

        self.step = 0

        msg_layout = QVBoxLayout()

        self.setWindowTitle('Confirmation')
        warning_lbl = QLabel('Are you sure you want to scan the IPs of ' + self.file_path + '?')

        msg_layout.addWidget(warning_lbl)
        msg_layout.addWidget(self.progress)
        msg_layout.addWidget(self.confirm_button)
        self.setLayout(msg_layout)

    def startProgress(self):
        # adjust here for IP actions
        #self.timer.start(10, self)  # Timer interval of 100 ms
        self.confirm_button.clicked.disconnect(self.startProgress)
        self.confirm_button.setEnabled(False)
        process_ips(self.progress, self.step, self.file_path)
        self.confirm_button.setText('Finished. You are free to close this window.')
        self.confirm_button.clicked.connect(self.close)
        self.confirm_button.setEnabled(True)

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

# Function to query VirusTotal for an IP address
def query_virustotal(ip, api_key):
    url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip}"
    headers = {"x-apikey": api_key}
    response = requests.get(url, headers=headers)
    data = response.json()
    # Extract the vulnerability score from the response
    # Note: Adjust the path according to the actual API response structure
    score = data.get('data', {}).get('attributes', {}).get('last_analysis_stats', {}).get('malicious', 0)
    return score

def query_abuse(ip, api_key):
    URL = 'https://api.abuseipdb.com/api/v2/check'
    # Request headers
    headers = {
        'Accept': 'application/json',
        'Key': api_key
    }

    # Parameters for the request
    params = {
        'ipAddress': ip,
        'maxAgeInDays': 90  # Set the number of days to check for reports
    }

    # Make the API request
    response = requests.get(URL, headers=headers, params=params)

    # Check if the response is successful
    if response.status_code == 200:
        result = response.json()
        #print(f"IP: {result['data']['ipAddress']}")
        #print(f"Abuse Score: {result['data']['abuseConfidenceScore']}")
        #print(f"Reports: {result['data']['totalReports']}")
        return result['data']['abuseConfidenceScore']
    else:
        return "N/A"
    
# Main function to read CSV, process IPs and write results
def process_ips(progress, step, file_path):
    virus_api = 'REPLACE'
    abuse_api = 'REPLACE2'

    #csv_files = glob.glob('*.csv')
    try:
        df = pd.read_csv(file_path)
        ips = df['ip'].to_list()
        data = {'ip':[],'VirusTotal score':[],'AbuseIPDB score':[]}
        output_df = pd.DataFrame(data)

        # number of IPs to check + 1 operation for converting to csv
        num_tasks = len(ips)
        print('num of tasks: ' + str(num_tasks))
        percent_per_task = (int)(100 / num_tasks)
        print('percent per task: ' + str(percent_per_task))

        # check the IPs. Record the data to output_df
        for ip in ips:
            vt_score = query_virustotal(ip, virus_api)
            ab_score = query_abuse(ip, abuse_api)

            print("Processed " + str(ip) + "\nVirusTotal:\t" + str(vt_score) + "\nAbuseIPDB:\t" + str(ab_score) + "\n")

            new_data = {'ip':[ip], 'VirusTotal score':[vt_score], 'AbuseIPDB score':[ab_score]}
            new_row = pd.DataFrame(new_data)
            output_df = pd.concat([output_df, new_row], ignore_index=True)

            step += percent_per_task
            progress.setValue(step)
            time.sleep(0.25)
        
        # create a new file for the output
        output_df.to_csv('spreadsheets\\output.csv')
        step = 100
        progress.setValue(step)
    except IndexError:
        print('error: no csv files in working directory!')
    except Exception as e:
        print('an error has occured: ' + str(e))

    return

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
    scroll_area.setMaximumHeight(600)
    main_layout.addWidget(scroll_area)
                
    start_btn = QPushButton('push me!')
    start_btn.clicked.connect(lambda: process_ips())
    start_btn.setFixedSize(150, 50)
    main_layout.addWidget(start_btn, alignment=Qt.AlignBottom | Qt.AlignHCenter)

    window.show()
    app.exec_()

main()