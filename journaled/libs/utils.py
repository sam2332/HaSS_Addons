import re
import os
import requests
from flask import request, abort, url_for
import logging
import sys
from datetime import timezone, datetime
import time
from zoneinfo import ZoneInfo  # Import ZoneInfo for timezone handling
from CONST import STOPWORDS
import re

from nltk import RegexpParser, pos_tag, word_tokenize

def extract_phrases(text):
    # Tokenize and tag parts of speech
    words = word_tokenize(text)
    tagged_words = pos_tag(words)
    
    # Define multiple grammars for extracting phrases
    grammars = [
        # Verb followed by a determiner, adjective, and noun(s)
        r"""
        VP1: {<VB.*><DT>?<JJ>*<NN.*>+}
        """,
        # Verb followed by a preposition and noun (e.g., "spent time with Mitch")
        r"""
        VP2: {<VB.*><IN><NNP|NN.*>+}
        """,
        # Verb followed by a cardinal number and a noun (e.g., "took two walks")
        r"""
        VP3: {<VB.*><CD><NN.*>+}
        """,
        # Adjective followed by noun (e.g., "great time")
        r"""
        AP1: {<JJ><NN.*>+}
        """,
        # Verb followed by gerund (e.g., "went shopping")
        r"""
        VP4: {<VB.*><VBG>}
        """
    ]
    
    # Extract phrases using each grammar
    phrases = []
    for grammar in grammars:
        parser = RegexpParser(grammar)
        tree = parser.parse(tagged_words)
        
        # Extract continuous phrases from the tree
        for subtree in tree.subtrees():
            if subtree.label() in ['VP1', 'VP2', 'VP3', 'AP1', 'VP4']:
                phrases.append(' '.join(word for word, tag in subtree.leaves()))
    
    
    #remove phrases that are just a single word
    phrases = [phrase for phrase in phrases if len(phrase.split()) > 1]
    return phrases


def extract_words(text):
    # Extract words from text
    return [word.lower() for word in re.findall(r'\b\w+\b', text) if word.lower() not in STOPWORDS]
    
def extract_tags(content):
    pattern = r'#([\w()]+)'
    tags = re.findall(pattern, content)
    lowercased_tags = [tag.lower() for tag in tags]
    return lowercased_tags

def link_tags(content):
    tag_pattern = r'#([\w()]+)'
    
    def replace_tag(match):
        tag = match.group(1)
        url = wrapped_url_for('tags.tag_detail', tag_name=tag)
        return f'<a href="{url}">#{tag}</a>'
    
    linked_content = re.sub(tag_pattern, replace_tag, content)
    return linked_content

def get_remote_user():
    if os.environ.get("local_dev_user"):
        return os.environ.get("local_dev_user") 
    else:
        user = request.headers.get('X-Remote-User-Name')
        if not user:
            abort(400, description="User not specified")
        return user

def nl2br(value):
    return value.replace('\n', '<br>')

def u2s(value):
    return value.replace('_',' ')

def time_link(timestamp):
    # Ensure TZ is set, fallback to UTC if not
    tz_name = os.environ.get('TZ', 'EST')

    # Convert the timestamp from UTC to the local timezone
    local_timezone = ZoneInfo(tz_name)
    timestamp = timestamp.replace(tzinfo=timezone.utc).astimezone(local_timezone)
    
    # Format the date part (like '2024-10-04')
    day = timestamp.strftime('%Y-%m-%d')

    # Generate the URL for the specific day using Flask's `url_for`
    day_url = wrapped_url_for('main.on_day', day=day)
    
    # Create the HTML link for the date
    date_link = f'<a href="{day_url}">{day}</a>'
    
    # Format the time part separately (like '10:15:30 AM')
    time_formatted = timestamp.strftime('%I:%M:%S %p')
    
    # Combine the date link with the formatted time
    return f'{date_link} {time_formatted}'


    
    
def wrapped_url_for(endpoint, **values):
    # Get the ingress path from the request headers
    ingress_path = request.headers.get('X-Ingress-Path', '')
    if ingress_path:
        # Use the ingress path from the header to build the URL
        return f"{ingress_path}{url_for(endpoint, **values)}"
    else:
        # Fallback to normal url_for if no ingress path is found
        return url_for(endpoint, **values)




SUPERVISOR_TOKEN = os.getenv("SUPERVISOR_TOKEN")

def set_timezone():
    url = "http://supervisor/info"
    headers = {"Authorization": f"Bearer {SUPERVISOR_TOKEN}"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        timezone = data['data']['timezone']
        os.environ['TZ'] = timezone
    except Exception as e:
        os.environ['TZ'] = "UTC"  # Fallback to UTC if the request fails





def basic_markdown(text):
    out =[]
    lines = text.split('\n')
    in_list = False
    for line in lines:
        if line.startswith('>'):
            out.append(f'<blockquote class="blockquote"><p>{line[1:]}</p></blockquote>')
        elif line.startswith('* '):
            if not in_list:
                in_list = True
                out.append('<ul>')
            out.append(f'<li>{line[2:]}</li>')
        else:
            if in_list:
                in_list = False
                out.append('</ul>')
            out.append(line)
            
    if in_list:
        in_list = False
        out.append('</ul>')
    return '\n'.join(out)

def dbl_br_remover(text):
    return text.replace('<br><br>','<br>')



def youtube_embedder(text):
    url = text.replace('https://www.youtube.com/watch?v=','https://www.youtube.com/embed/')
    
    return f"""
    <iframe width="560" height="315" src="{url}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
    """

# Register the custom filter in Flask

import re

def auto_linker(text):
    url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
    if len(url) > 0:
        #replace the url with the link
        for u in url:
            text = text.replace(u,f'<a href="{u}" target="_blank" >{u}</a>')
    return text

    
    
def datetime_jinja(year, month, day):
    return datetime.datetime(year, month, day)
