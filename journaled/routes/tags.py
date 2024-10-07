from flask import Blueprint, render_template, request, abort
from libs.models import Tag, JournalEntry, db
from libs.utils import get_remote_user
from collections import defaultdict
from sqlalchemy import func

def register_blueprint(app):
    bp = Blueprint('tags', __name__, url_prefix='/tags')

    @bp.route('/<tag_name>')
    def tag_detail(tag_name):
        # Extract the user from request headers
        user = get_remote_user()

        # Normalize the tag name
        tag_name = tag_name.lower().replace('%20', '_').replace(' ', '_')

        # Get the tag object for the user
        tag = Tag.query.filter_by(name=tag_name, user=user).first()
        if not tag:
            # If the tag doesn't exist, return a 404 error
            return render_template('tag_not_found.html', tag_name=tag_name), 404

        # Get the journal entries associated with the tag, ordered by timestamp
        entries = tag.entries.order_by(JournalEntry.timestamp.desc()).all()

        return render_template('tags.html', tag=tag, entries=entries, tag_name=tag_name)

    @bp.route('/')
    def all_tags():
        user = get_remote_user()

        # Fetch tags and their associated entry counts for the user
        tags_with_counts = (
            db.session.query(Tag, func.count(JournalEntry.id).label('entry_count'))
            .outerjoin(Tag.entries)
            .filter(Tag.user == user)
            .group_by(Tag.id)
            .order_by(func.count(JournalEntry.id).desc())
            .all()
        )

        # If no tags are found, render the template with an empty list
        if not tags_with_counts:
            return render_template('all_tags.html',word_cloud={}, table_items=[])

        # Prepare data for the word cloud and table
        word_cloud = {tag.name: entry_count for tag, entry_count in tags_with_counts}
        table_items = sorted(word_cloud.items(), key=lambda x: x[1], reverse=True)
        print(word_cloud)
        # Pass the word cloud data and table items to the template
        return render_template('all_tags.html', word_cloud=word_cloud, table_items=table_items)

    app.register_blueprint(bp)
