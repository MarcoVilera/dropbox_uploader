import os
from utils import jsonReader

APP_KEY = os.getenv('APP_KEY')
APP_SECRET = os.getenv('APP_SECRET')
REFRESH_TOKEN = os.getenv('REFRESH_TOKEN')
REGEX = r'^(.*?)_(\d{4}\d{2})(01|30|31|28)_(\d{6})\.bak$'
CHUNK_SIZE = 4 * 1024 * 1024 # 4MB

configData = jsonReader.read_json("./settings.json")
ALLOWED_EXTENSIONS = configData["validExtensions"]
FOLDER_TO_WATCH = configData['Folder']
DESTINATION_FOLDER = configData['DestinationFolder']
LOGS_DIRECTORY = configData['logDirectory']

