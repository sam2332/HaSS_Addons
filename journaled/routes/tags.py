from flask import Blueprint, render_template, request
from libs.models import Tag
from libs.utils import get_remote_user
from collections import defaultdict
def register_blueprint(app):
    bp = Blueprint('tags', __name__, url_prefix='/tags')

    @bp.route('/<tag_name>')
    def tag_detail(tag_name):
        # Extract the user from request headers
        user = get_remote_user()

        tag_name = tag_name.lower()
        # Filter tags by name and user
        tags = Tag.query.filter_by(name=tag_name, user=user).all()
        return render_template('tags.html', tags=tags, tag_name=tag_name)
    
    @bp.route('/')
    def all_tags():
        user = get_remote_user()
        tags = Tag.query.filter_by(user=user).with_entities(Tag.name).all()

        # Convert to a dictionary of tag frequencies
        word_cloud = defaultdict(int)
        for tag in tags:
            word_cloud[tag[0]] += 1
        
        # Normalize sizes (for example, min size = 10, max size = 50)
        max_count = max(word_cloud.values(), default=1)
        min_count = min(word_cloud.values(), default=1)
        
        # Define a range for font sizes
        def get_font_size(count, min_size=10, max_size=50):
            if max_count == min_count:
                return max_size  # If all tags have the same count
            return min_size + (count - min_count) * (max_size - min_size) // (max_count - min_count)

        # Create a list of tags with sizes
        tags_with_size = [{'name': tag, 'size': get_font_size(count)} for tag, count in word_cloud.items()]

        return render_template('all_tags.html', tags_with_size=tags_with_size)
    app.register_blueprint(bp)