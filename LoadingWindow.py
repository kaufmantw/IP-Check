from PyQt5.QtWidgets import *
import pandas as pd
import requests
import yaml
import time

class LoadingWindow(QDialog):
    def __init__(self, file_path, parent=None):
        self.file_path = file_path
        super().__init__()

        self.initUI()

    def initUI(self):
        self.confirm_button = QPushButton('Press to Confirm')
        self.confirm_button.clicked.connect(self.startProgress)

        self.setWindowTitle('Confirmation')
        self.warning_lbl = QLabel('Are you sure you want to scan the IPs of ' + self.file_path + '?\nUsing column \"' + '\"')

        #get options for combo box
        self.choice = QComboBox(self)
        self.options = get_options(self)
        try:
            self.choice.addItems(self.options)
        except TypeError as e:
            print('No columns found. Free to exit')
            self.error_exit()

        self.progress = QProgressBar(self)

        # Connect the combo box selection change event to a method
        self.choice.currentIndexChanged.connect(self.on_combobox_changed)

        self.step = 0

        msg_layout = QVBoxLayout()

        msg_layout.addWidget(self.choice)
        msg_layout.addWidget(self.warning_lbl)
        msg_layout.addWidget(self.progress)
        msg_layout.addWidget(self.confirm_button)
        self.setLayout(msg_layout)

    # progress bar controlling method
    def startProgress(self):
        self.confirm_button.clicked.disconnect(self.startProgress)
        self.confirm_button.setEnabled(False)
        process_ips(self.progress, self.step, self.file_path, self.choice.currentText())
        self.confirm_button.setText('Finished. You are free to close this window.')
        self.confirm_button.clicked.connect(self.close)
        self.confirm_button.setEnabled(True)

    def on_combobox_changed(self):
        self.selected_option = self.choice.currentText()

    def error_exit(self):
        self.confirm_button.clicked.disconnect(self.startProgress)
        self.confirm_button.clicked.connect(self.close)
        self.warning_lbl.setText('Error in file scanning. You are free to close this page.')
        self.confirm_button.setText('Close')

    # Function to query VirusTotal for an IP address
def query_virustotal(ip, api_key):
    url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip}"
    headers = {"x-apikey": api_key}
    response = requests.get(url, headers=headers)
    data = response.json()
    # Extract the vulnerability score from the response
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
        return result['data']['abuseConfidenceScore']
    else:
        return "N/A"
    
# Main function to read CSV, process IPs and write results
def process_ips(progress, step, file_path, ip_key):
    # get api keys
    with open('keys.yaml', 'r') as file:
        data = yaml.safe_load(file)
    virus_api = data['virus_api_key']
    abuse_api = data['abuse_api_key']

    #csv_files = glob.glob('*.csv')
    try:
        df = pd.read_csv(file_path)
        ips = df[ip_key].to_list()
        data = {'ip':[],'VirusTotal score':[],'AbuseIPDB score':[]}
        output_df = pd.DataFrame(data)

        # number of IPs to check + 1 operation for converting to csv
        num_tasks = len(ips) + 1
        percent_per_task = (int)(100 / num_tasks)

        # check the IPs. Record the data to output_df
        for ip in ips:
            vt_score = query_virustotal(ip, virus_api)
            ab_score = query_abuse(ip, abuse_api)

            #print("Processed " + str(ip) + "\nVirusTotal:\t" + str(vt_score) + "\nAbuseIPDB:\t" + str(ab_score) + "\n")

            new_data = {'ip':[ip], 'VirusTotal score':[vt_score], 'AbuseIPDB score':[ab_score]}
            new_row = pd.DataFrame(new_data)
            output_df = pd.concat([output_df, new_row], ignore_index=True)

            step += percent_per_task
            progress.setValue(step)
            time.sleep(0.25)
        
        # create a new file for the output
        # should probably sort by VirusTotal
        output_df = output_df.sort_values(by='VirusTotal score', ascending=False)
        output_df.to_csv('spreadsheets\\output.csv')

        # finish progress bar
        step = 100
        progress.setValue(step)

    except IndexError:
        print('error: no csv files in working directory!')
    except Exception as e:
        print('an error has occured: ' + str(e))

    return

def get_options(self):
    try:
        df = pd.read_csv(self.file_path)
        cols = df.columns
        return cols
    except pd.errors.EmptyDataError as e:
        print('File contained no columsn')
    return