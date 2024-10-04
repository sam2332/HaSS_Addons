from flask import Blueprint, render_template, request, redirect, Response
import random
import time
import uuid
import io
import csv

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
 

    @bp.route('/export_csv')
    def export_csv():
        user = get_remote_user()
        entries = JournalEntry.query.filter_by(user=user).all()

        # Create an in-memory file object to store the CSV data
        output = io.StringIO()

        # Create a CSV writer
        writer = csv.writer(output)

        # Write the header
        writer.writerow(['id', 'content'])

        # Write the entries, properly escaping content
        for entry in entries:
            writer.writerow([entry.id, entry.content])

        # Move to the start of the stream
        output.seek(0)

        # Return the CSV file as a response
        return Response(
            output,
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment;filename=journal_entries.csv'}
        )
        
    @bp.route('/')
    def main():       
        return render_template('settings.html')
    app.register_blueprint(bp)