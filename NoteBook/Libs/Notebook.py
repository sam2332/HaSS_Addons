import os
import json
from werkzeug.utils import secure_filename

CONFIG_PATH = '/config/'
# Check if CONFIG_PATH is set in the environment
if os.environ.get('CONFIG_PATH'):
    CONFIG_PATH = os.environ.get('CONFIG_PATH')
NOTEBOOK_DIR = os.path.join(CONFIG_PATH, 'Notebook')
NOTEBOOKS_DIR = os.path.join(NOTEBOOK_DIR, 'Notebooks')
class NotebookSection:
    def __init__(self, notebook_name, section_name, load_pages=False):        
        notebook_name = secure_filename(notebook_name)
        section_name = secure_filename(section_name)
        self.name = section_name
        self.notebook_name = notebook_name
        self.name = secure_filename(self.name)
        self.section_path = os.path.join(NOTEBOOKS_DIR, self.notebook_name, self.name)

        # Load metadata
        with open(os.path.join(self.section_path, 'metadata.json'), 'r', encoding='utf-8') as f:
            self.metadata = json.load(f)
            self.display_name = self.metadata['name']
        if load_pages:
            self.load_pages()
    def load_pages(self):
        pages = os.listdir(self.section_path)
        self.pages = [f for f in os.listdir(self.section_path) if f.endswith('.md')]
        
class Notebook:
    def __init__(self,notebook_name,load_sections=False):
        notebook_name = secure_filename(notebook_name)
        
        self.name = notebook_name        

        self.name = secure_filename(self.name)
        self.notebook_path = os.path.join(NOTEBOOKS_DIR, self.name)

        # Load metadata
        with open(os.path.join(self.notebook_path, 'metadata.json'), 'r', encoding='utf-8') as f:
            self.metadata = json.load(f)
            self.display_name = self.metadata['name']
            try:
                theme_id = int(self.metadata['theme'])
                self.theme = "Notebook_Theme_"+self.metadata['theme']
            except:
                self.theme = "Notebook_Theme_0"
                theme_id = 0
        if load_sections:
            self.load_sections()
            
    def load_sections(self):
        sections = os.listdir(self.notebook_path)
        self.sections = [NotebookSection(self.name, sec) for sec in sections if os.path.isdir(os.path.join(self.notebook_path, sec))]
        return self.sections