from flask import Blueprint, render_template, request, redirect, Response
import random
import time
import uuid
import io
import csv
from libs.ConfigFile import ConfigFile
from libs.HashTagAdder import HashTagAdder
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

    @bp.route('/enable_auto_hasher')
    def enable_auto_hasher():
        user_settings = ConfigFile(f"{app.filesystem_paths['ADDON_FILES_DIR_PATH']}/{session['user']}.json")
        user_settings.set("EnableAutoHasher", 'true')

    @bp.route('/disable_auto_hasher')
    def disable_auto_hasher():
        user_settings = ConfigFile(f"{app.filesystem_paths['ADDON_FILES_DIR_PATH']}/{session['user']}.json")
        user_settings.set("EnableAutoHasher", 'false')
    

    @bp.route('/import_csv', methods=['POST'])
    def import_csv():
        user = get_remote_user()
        ah = HashTagAdder()
        file = request.files['file']
        if file:
            # Read the CSV file
            stream = io.StringIO(file.stream.read().decode('UTF8'), newline=None)
            # parse csv and add all entries autotag and tag them
            csv_input = csv.reader(stream)
            for row in csv_input:
                content = row[1]
                content = ah.add_hashtags(content)
                tags = extract_tags(content)
                entry = JournalEntry(content=content, user=user)
                db.session.add(entry)
                db.session.commit()
                for tag_name in tags:
                    tag = Tag(name=tag_name, user=user, entry_id=entry.id)
                    db.session.add(tag)
                db.session.commit()

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
        user_settings = ConfigFile(f"{app.filesystem_paths['ADDON_FILES_DIR_PATH']}/{session['user']}.json")
        return render_template('settings.html')
    app.register_blueprint(bp)



    """ ah = HashTagAdder(user)
            content = ah.add_hashtags(content)
            tags = extract_tags(content)

            # Save journal entry with user
            entry = JournalEntry(content=content, user=user)
            db.session.add(entry)
            db.session.commit()

            # Save tags with user
            for tag_name in tags:
                tag = Tag(name=tag_name, user=user, entry_id=entry.id)
                db.session.add(tag)
            db.session.commit()"""