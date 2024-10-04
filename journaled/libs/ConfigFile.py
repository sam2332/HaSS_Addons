
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
            json.dump(self.config, file)
    
    def get(self, key):
        return self.config.get(key)
    
    def set(self, key, value):
        self.config[key] = value
        self.save()