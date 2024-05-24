from utils import jsonReader
import os
from datetime import datetime
def write(message):

    configContent = jsonReader.read_json("./settings.json")

    dateFormat = configContent['logFileFormat']['dateFormat'].split('-')

    current_date = datetime.now().strftime(f"%{dateFormat[0]}-%{dateFormat[1]}-%{dateFormat[2]}")

    time_format = configContent['logFileFormat']['timeFormat'].lower()
    if time_format == '24h':
        log_time = datetime.now().strftime('%H:%M:%S')
    elif time_format =='12h':
        log_time = datetime.now().strftime('%I:%M:%S%p')

    file = configContent["logFileFormat"]["logFile"] + current_date+".txt"
    with open(configContent['logDirectory'] +"/"+ file, 'a') as file:
        file.write(log_time+" "+message + '\n')
        file.close()

def existsFolder():
    configContent = jsonReader.read_json("./settings.json")
    if not os.path.exists(configContent['logDirectory']):
        os.mkdir(configContent['logDirectory'])