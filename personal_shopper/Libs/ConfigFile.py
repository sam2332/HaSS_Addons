import json

class ConfigFile:
#get set and save functions
    def __init__(self, file_name):
       self.file_name = file_name
       self.config = {}
       self.load()
    
    def load(self):
        try:
            with open(self.file_name, 'r') as file:
                self.config = json.load(file)
        except FileNotFoundError:
            self.config = {}
    
    def save(self):
        with open(self.file_name, 'w') as file:
            json.dump(self.config, file,indent=4)
    
    def get(self, key,default=None):
        if key not in self.config:
            self.set(key, default)
            return default
        return self.config.get(key)
    
    def set(self, key, value):
        self.config[key] = value
        self.save()
