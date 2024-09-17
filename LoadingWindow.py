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
        self.progress = QProgressBar(self)

        self.confirm_button = QPushButton('Press to Confirm')
        self.confirm_button.clicked.connect(self.startProgress)

        self.step = 0

        msg_layout = QVBoxLayout()

        self.setWindowTitle('Confirmation')
        warning_lbl = QLabel('Are you sure you want to scan the IPs of ' + self.file_path + '?\nUsing column \"ip\"')

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
    # get api keys
    with open('keys.yaml', 'r') as file:
        data = yaml.safe_load(file)
    virus_api = data['virus_api_key']
    abuse_api = data['abuse_api_key']

    #csv_files = glob.glob('*.csv')
    try:
        df = pd.read_csv(file_path)
        ips = df['ip'].to_list()
        data = {'ip':[],'VirusTotal score':[],'AbuseIPDB score':[]}
        output_df = pd.DataFrame(data)

        # number of IPs to check + 1 operation for converting to csv
        num_tasks = len(ips) + 1
        #print('num of tasks: ' + str(num_tasks))
        percent_per_task = (int)(100 / num_tasks)
        #print('percent per task: ' + str(percent_per_task))

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