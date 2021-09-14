import json
import os

class Settings(object):
    def __init__(self):
        self.settings = self.read_settings("config.json")

    def read_settings(self, settings_file):
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))  
        settings_path = os.path.join(__location__, settings_file)      
        open_settings_file = open(settings_path, "r")
        settings_file_data = open_settings_file.read()
        open_settings_file.close()
        settings_json = json.loads(settings_file_data)
        return settings_json 