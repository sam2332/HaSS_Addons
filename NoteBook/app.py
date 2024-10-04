from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import time
import json
from flask import flash
from threading import Lock
from Libs.Notebook import Notebook, NotebookSection
import os
import logging
import markdown
import sqlite3
from werkzeug.utils import secure_filename
from Libs.ConfigFile import ConfigFile
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.log = logging.getLogger(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Default config path
CONFIG_PATH = '/config/'
# Check if CONFIG_PATH is set in the environment
if os.environ.get('CONFIG_PATH'):
    CONFIG_PATH = os.environ.get('CONFIG_PATH')
    app.log.info(f"Using config path from environment: {CONFIG_PATH}")
NOTEBOOK_DIR = os.path.join(CONFIG_PATH, 'Notebook')
if not os.path.exists(NOTEBOOK_DIR):
    os.makedirs(NOTEBOOK_DIR)
NOTEBOOKS_DIR = os.path.join(NOTEBOOK_DIR, 'Notebooks')
if not os.path.exists(NOTEBOOKS_DIR):
    os.makedirs(NOTEBOOKS_DIR)
CONFIG_PATH = os.path.join(NOTEBOOK_DIR, 'config.json')
INDEX_DB = os.path.join(NOTEBOOK_DIR, 'index.db')
CONFIG_FILE = ConfigFile(CONFIG_PATH)


# Ensure directories exist
os.makedirs(NOTEBOOKS_DIR, exist_ok=True)

# Initialize logging
logging.basicConfig(level=logging.INFO)
# Initialize SQLite database for indexing
def init_db():
    conn = sqlite3.connect(INDEX_DB)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS word_index (
            word TEXT,
            filepath TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()
import bleach

@app.template_filter('markdown')
def markdown_filter(content):
    allowed_tags = bleach.sanitizer.ALLOWED_TAGS + ['p', 'pre', 'img', 'h1', 'h2', 'h3']
    cleaned = bleach.clean(markdown.markdown(content), tags=allowed_tags)
    return Markup(cleaned)



def wrapped_url_for(endpoint, **values):
    # Get the ingress path from the request headers
    ingress_path = request.headers.get('X-Ingress-Path', '')
    if ingress_path:
        # Use the ingress path from the header to build the URL
        return f"{ingress_path}{url_for(endpoint, **values)}"
    else:
        # Fallback to normal url_for if no ingress path is found
        return url_for(endpoint, **values)
    
@app.context_processor
def override_url_for():
    global wrapped_url_for
    return dict(url_for=wrapped_url_for)


def index_markdown_file(filepath):
    # Read the markdown file
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract words, remove stop words, and index
    words = extract_words(content)
    conn = sqlite3.connect(INDEX_DB)
    c = conn.cursor()
    for word in words:
        c.execute('INSERT INTO word_index (word, filepath) VALUES (?, ?)', (word, filepath))
    conn.commit()
    conn.close()


import re
import string
from nltk.corpus import stopwords
import nltk

def extract_words(text):
    # Remove code blocks
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    # Remove inline code
    text = re.sub(r'`[^`]*`', '', text)
    # Remove images ![alt text](image_url)
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    # Remove links but keep the link text [text](url)
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    # Remove emphasis markers *italic*, **bold**, _italic_, __bold__
    text = re.sub(r'[*_]{1,3}', '', text)
    # Remove headings (leading #)
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
    # Remove blockquotes (leading >)
    text = re.sub(r'^>\s*', '', text, flags=re.MULTILINE)
    # Remove list markers (-, *, +, 1., etc.)
    text = re.sub(r'^\s*([*\-+]|\d+\.)\s+', '', text, flags=re.MULTILINE)
    # Remove horizontal rules
    text = re.sub(r'^([-*_]\s*){3,}$', '', text, flags=re.MULTILINE)
    # Remove any residual markdown characters
    text = text.replace('#', '')
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Now extract words
    words = text.lower().split()
    words = [word.strip(string.punctuation) for word in words]
    # Load stop words from NLTK
    stop_words = set(stopwords.words('english'))
    return [word for word in words if word and word not in stop_words]

# Download stop words if not already downloaded
nltk.download('stopwords')

# Routes

@app.route('/')
def home():
    # List all notebooks
    notebooks = os.listdir(NOTEBOOKS_DIR)
    notebooks = [Notebook(nb) for nb in notebooks if os.path.isdir(os.path.join(NOTEBOOKS_DIR, nb))]
    return render_template('index.html', notebooks=notebooks)

@app.route('/notebook/create', methods=['GET', 'POST'])
def create_notebook():
    if request.method == 'POST':
        oname = request.form['name']
        description = request.form.get('description', '')
        tags = request.form.get('tags', '')
        theme = request.form.get('theme', '')
        
        name = secure_filename(oname)

        # Create notebook directory
        notebook_path = os.path.join(NOTEBOOKS_DIR, name)
        os.makedirs(notebook_path, exist_ok=True)

        # Save metadata
        metadata = {
            'name': oname,
            'description': description,
            'tags': tags.split(','),
            'theme': theme
        }
        with open(os.path.join(notebook_path, 'metadata.json'), 'w', encoding='utf-8') as f:
            json.dump(metadata, f)

        return redirect(wrapped_url_for('view_notebook', notebook_name=name))
    return render_template('create_notebook.html')

@app.route('/notebook/<notebook_name>')
def view_notebook(notebook_name):
    notebook = Notebook(notebook_name,load_sections=True)
    return render_template('view_notebook.html', notebook=notebook)

@app.route('/notebook/<notebook_name>/section/create', methods=['GET', 'POST'])
def create_section(notebook_name):
    notebook_name = secure_filename(notebook_name)
    notebook_path = os.path.join(NOTEBOOKS_DIR, notebook_name)
    if request.method == 'POST':
        name = request.form['name']
        section_name = secure_filename(name)
        # Create section directory
        section_path = os.path.join(notebook_path, section_name)
        os.makedirs(section_path, exist_ok=True)
        # section metadata
        metadata = {
            'name': name,
        }
        with open(os.path.join(section_path, 'metadata.json'), 'w', encoding='utf-8') as f:
            json.dump(metadata, f)
            
        return redirect(wrapped_url_for('view_section', notebook_name=notebook_name, section_name=name))
    return render_template('create_section.html', notebook_name=notebook_name)

@app.route('/notebook/<notebook_name>/section/<section_name>')
def view_section(notebook_name, section_name):
    notebook_name = secure_filename(notebook_name)
    section_name = secure_filename(section_name)
    section = NotebookSection(notebook_name, section_name,load_pages=True)
    return render_template('view_section.html', notebook_name=notebook_name, section_name=section_name, section=section)

@app.route('/notebook/<notebook_name>/section/<section_name>/page/create', methods=['GET', 'POST'])
def create_page(notebook_name, section_name):
    notebook_name = secure_filename(notebook_name)
    section_name = secure_filename(section_name)
    section_path = os.path.join(NOTEBOOKS_DIR, notebook_name, section_name)
    if request.method == 'POST':
        title = request.form['title']
        content = request.form.get('content', '')
        filename = title + '.md'
        filepath = os.path.join(section_path, filename)

        # Save markdown file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        # Index content
        index_markdown_file(filepath)

        return redirect(wrapped_url_for('view_page', notebook_name=notebook_name, section_name=section_name, page_name=secure_filename(title)))
    return render_template('create_page.html', notebook_name=notebook_name, section_name=section_name)

@app.route('/notebook/<notebook_name>/section/<section_name>/page/<page_name>')
def view_page(notebook_name, section_name, page_name):
    
    notebook_name = secure_filename(notebook_name)
    section_name = secure_filename(section_name)
    page_name = secure_filename(page_name)
    page_path = os.path.join(NOTEBOOKS_DIR, notebook_name, section_name, page_name + '.md')
    if not os.path.exists(page_path):
        return "Page not found", 404

    # Load markdown content
    with open(page_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return render_template('view_page.html', content=content, notebook_name=notebook_name, section_name=section_name, page_name=page_name)

@app.route('/notebook/<notebook_name>/section/<section_name>/page/<page_name>/edit', methods=['GET', 'POST'])
def edit_page(notebook_name, section_name, page_name):
    notebook_name = secure_filename(notebook_name)
    section_name = secure_filename(section_name)
    page_name = secure_filename(page_name)
    page_path = os.path.join(NOTEBOOKS_DIR, notebook_name, section_name, page_name + '.md')
    if not os.path.exists(page_path):
        return "Page not found", 404

    if request.method == 'POST':
        content = request.form.get('content', '')
        # Save markdown file
        with open(page_path, 'w', encoding='utf-8') as f:
            f.write(content)

        # Re-index content
        conn = sqlite3.connect(INDEX_DB)
        c = conn.cursor()
        c.execute('DELETE FROM word_index WHERE filepath = ?', (page_path,))
        conn.commit()
        conn.close()
        index_markdown_file(page_path)

        return redirect(wrapped_url_for('view_page', notebook_name=notebook_name, section_name=section_name, page_name=page_name))
    else:
        with open(page_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return render_template('edit_page.html', content=content, notebook_name=notebook_name, section_name=section_name, page_name=page_name)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    words = query.lower().split()
    conn = sqlite3.connect(INDEX_DB)
    c = conn.cursor()
    results = []
    for word in words:
        c.execute('SELECT filepath FROM word_index WHERE word = ?', (word,))
        results.extend(c.fetchall())
    conn.close()

    # Remove duplicates
    results = list(set(results))
    # Convert filepaths to notebook, section, page names
    pages = []
    for result in results:
        filepath = result[0]
        relative_path = os.path.relpath(filepath, NOTEBOOKS_DIR)
        parts = relative_path.split(os.sep)
        if len(parts) == 3:
            notebook_name, section_name, page_file = parts
            page_name = os.path.splitext(page_file)[0]
            pages.append({
                'notebook_name': notebook_name,
                'section_name': section_name,
                'page_name': page_name
            })
    return render_template('search_results.html', pages=pages, query=query)

# Additional routes for grouping, sorting, themes, etc.

# Group by tags
@app.route('/tags/<tag>')
def view_tag(tag):
    notebooks = []
    for notebook_name in os.listdir(NOTEBOOKS_DIR):
        notebook_path = os.path.join(NOTEBOOKS_DIR, notebook_name)
        metadata_path = os.path.join(notebook_path, 'metadata.json')
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                if tag in metadata.get('tags', []):
                    notebooks.append(notebook_name)
    return render_template('tag_view.html', tag=tag, notebooks=notebooks)

# Sort notebooks
@app.route('/sort')
def sort_notebooks():
    sort_by = request.args.get('by', 'name')
    notebooks = os.listdir(NOTEBOOKS_DIR)
    notebooks = [nb for nb in notebooks if os.path.isdir(os.path.join(NOTEBOOKS_DIR, nb))]

    if sort_by == 'name':
        notebooks.sort()
    elif sort_by == 'last_modified':
        notebooks.sort(key=lambda nb: os.path.getmtime(os.path.join(NOTEBOOKS_DIR, nb)), reverse=True)
    elif sort_by == 'page_count':
        notebooks.sort(key=lambda nb: count_pages_in_notebook(nb), reverse=True)
    elif sort_by == 'importance':
        # Define your own importance metric
        pass

    return render_template('sorted_notebooks.html', notebooks=notebooks, sort_by=sort_by)

def count_pages_in_notebook(notebook_name):
    notebook_path = os.path.join(NOTEBOOKS_DIR, notebook_name)
    count = 0
    for root, dirs, files in os.walk(notebook_path):
        count += len([f for f in files if f.endswith('.md')])
    return count

# Theme management routes would go here
@app.route('/notebook/<notebook_name>/section/<section_name>/page/<page_name>/autosave', methods=['POST'])
def autosave_page(notebook_name, section_name, page_name):
    page_path = os.path.join(NOTEBOOKS_DIR, notebook_name, section_name, page_name + '.md')
    data = request.get_json()
    content = data.get('content', '')

    # Save content
    with open(page_path, 'w', encoding='utf-8') as f:
        f.write(content)

    # Re-index content
    conn = sqlite3.connect(INDEX_DB)
    c = conn.cursor()
    c.execute('DELETE FROM word_index WHERE filepath = ?', (page_path,))
    conn.commit()
    conn.close()
    index_markdown_file(page_path)


    return jsonify(status='success')



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

