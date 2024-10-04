from flask import Blueprint, render_template, request, redirect
import random

from libs.models import db, JournalEntry, Tag
from libs.utils import get_remote_user
from collections import defaultdict
from libs.utils import extract_tags
def register_blueprint(app):
    bp = Blueprint('settings', __name__, url_prefix='/settings')

    
    @bp.route('/reindex_tags')
    def reindex_tags():
        user = get_remote_user()
        entries = JournalEntry.query.filter_by(user=user).all()
        Tag.query.filter_by(user=user).delete()
        for entry in entries:
            tags = extract_tags(entry.content)
            for tag_name in tags:
                tag = Tag(name=tag_name, user=user, entry_id=entry.id)
                db.session.add(tag)
        db.session.commit()
        return redirect(app.wrapped_url_for('settings.main'))
    
    @bp.route('/')
    def main():       
        return render_template('settings.html')
    app.register_blueprint(bp)