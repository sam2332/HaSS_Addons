from flask import Blueprint, render_template, request
from libs.models import Tag, db
from libs.utils import get_remote_user
from collections import defaultdict
from sqlalchemy import func
def register_blueprint(app):
    bp = Blueprint('tags', __name__, url_prefix='/tags')

    @bp.route('/<tag_name>')
    def tag_detail(tag_name):
        # Extract the user from request headers
        user = get_remote_user()

        tag_name = tag_name.lower()
        if '%20' in tag_name:
            tag_name = tag_name.replace('%20', '_')
            
        if ' ' in tag_name:
            tag_name = tag_name.replace(' ', '_')
            
        # Filter tags by name and user
        tags = Tag.query.filter_by(name=tag_name, user=user).all()
        return render_template('tags.html', tags=tags, tag_name=tag_name)
    
    
    @bp.route('/')
    def all_tags():
        user = get_remote_user()

        # Fetch tag counts from the database
        tags = (
            db.session.query(Tag.name, func.count(Tag.name))
            .filter_by(user=user)
            .group_by(Tag.name)
            .all()
        )

        # If no tags are found, render the template with an empty list
        if not tags:
            return render_template('all_tags.html', tags_with_size=[])

        # Convert the list of tuples into a dictionary
        word_cloud = {tag_name: count for tag_name, count in tags}

        #table_items is sorted by count
        table_items = sorted(word_cloud.items(), key=lambda x: x[1], reverse=True)
        # Pass the word cloud data (tag name and count) to the template
        return render_template('all_tags.html', word_cloud=word_cloud,table_items=table_items)

    app.register_blueprint(bp)