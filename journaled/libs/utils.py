import re
from flask import request, abort, url_for

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
    user = request.headers.get('X-Remote-User-Name')
    if not user:
        user = 'DEV'
        #abort(400, description="User not specified")
    return user

def nl2br(value):
    return value.replace('\n', '<br>')


def wrapped_url_for(endpoint, **values):
    # Get the ingress path from the request headers
    ingress_path = request.headers.get('X-Ingress-Path', '')
    if ingress_path:
        # Use the ingress path from the header to build the URL
        return f"{ingress_path}{url_for(endpoint, **values)}"
    else:
        # Fallback to normal url_for if no ingress path is found
        return url_for(endpoint, **values)


