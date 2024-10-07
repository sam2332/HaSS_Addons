from flask import Blueprint, render_template, request, redirect, url_for, session
from libs.models import db, JournalEntry, Tag
from libs.utils import extract_tags
from libs.utils import get_remote_user
from libs.HashTagAdder import HashTagAdder
from libs.ConfigFile import ConfigFile
import random
from CONST import SAYINGS,PAST_SAYINGS
import time
import uuid
from datetime import datetime, timedelta
from libs.file_attachment_manager import FileAttachmentManager
from sqlalchemy.orm import joinedload


def register_blueprint(app):
    bp = Blueprint('main', __name__)

    @bp.route('/', methods=['GET', 'POST'])
    def journal():
        user = get_remote_user()
        file_attachment_manager = FileAttachmentManager(app,user)
        if request.method == 'POST':
            content = request.form['content']
            attachments = request.files.getlist('attachments')
            print(attachments)

            ah = HashTagAdder()
            user_settings = ConfigFile(f"{app.filesystem_paths['ADDON_FILES_DIR_PATH']}/{user}.json")
            if bool(user_settings.get("EnableAutoHasher",'false')):
                content = ah.add_hashtags(content)
            tags_in_content = extract_tags(content)

            # Save journal entry with user
            entry = JournalEntry(content=content, user=user)
            db.session.add(entry)
            db.session.commit()

            # Save attachments with user
            for attachment in attachments:
                if attachment.filename == '':
                    continue  # Skip empty files
                print(attachment)
                file_attachment_manager.save_file(attachment, entry.id)

            # Save tags with user, avoiding duplicates
            for tag_name in tags_in_content:
                tag = Tag.query.filter_by(name=tag_name, user=user).first()
                if not tag:
                    tag = Tag(name=tag_name, user=user)
                    db.session.add(tag)
                    db.session.commit()  # Commit here to ensure tag.id is available
                else:
                    tag.last_used = datetime.now()

                # Check if the tag is already associated with the entry
                if tag not in entry.tags:
                    entry.tags.append(tag)

            db.session.commit()

            last_post_uuid = uuid.uuid4()
            session['last_post_uuid'] = last_post_uuid


            user_post_journal_page = user_settings.get("post_journal_url",'past')
            if user_post_journal_page == 'journal':
                return redirect(app.wrapped_url_for('main.journal'))
            elif user_post_journal_page == 'past':
                return redirect(app.wrapped_url_for('main.past'))
            elif user_post_journal_page == 'tags':
                return redirect(app.wrapped_url_for('tags.all_tags'))

        if session.get('saying'):
            if session.get('saying_set_time') + 15 < time.time():
                saying = random.choice(SAYINGS)
                session['saying'] = saying
                session['saying_set_time'] = time.time()
            saying = session.get('saying')
        else:   
            saying = random.choice(SAYINGS)
            session['saying'] = saying
            session['saying_set_time'] = time.time()
            
            
            
        if session.get('last_post_uuid'):
            last_post_uuid = session.get('last_post_uuid')
        else:
            last_post_uuid = uuid.uuid4()
            session['last_post_uuid'] = last_post_uuid

        return render_template('journal.html', user = user,saying=saying, last_post_uuid =last_post_uuid)
    
    #delete file
    @bp.route('/delete_file', methods=['GET'])
    def delete_file():
        user = get_remote_user()
        entry_id = request.args.get('entry_id')
        file_name = request.args.get('file_name')
        file_attachment_manager = FileAttachmentManager(app, user)
        file_attachment_manager.delete_file(entry_id, file_name)
        return redirect(app.wrapped_url_for('main.update_journal_entry', entry_id=entry_id))
    
    #update_journal_entry
    @bp.route('/update_journal_entry', methods=['GET', 'POST'])
    def update_journal_entry():
        user = get_remote_user()
        file_attachment_manager = FileAttachmentManager(app,user)
        if request.method == 'POST':
            entry_id = request.form['entry_id']
            content = request.form['content']
            print(content)
            ah = HashTagAdder()
            user_settings = ConfigFile(f"{app.filesystem_paths['ADDON_FILES_DIR_PATH']}/{user}.json")
            if bool(user_settings.get("EnableAutoHasher",'false')):
                content = ah.add_hashtags(content)
            print(content)
            tags_in_content = extract_tags(content)
            attachments = request.files.getlist('attachements')

            # Save journal entry with user
            entry = JournalEntry.query.filter_by(id=entry_id).first()
            entry.content = content
            db.session.commit()

            # Save attachements with user   
            for attachement in attachments:
                file_attachment_manager.save_file(attachement, entry.id)

            #delete existing tags
            for tag in entry.tags:
                entry.tags.remove(tag)
            db.session.commit()
            
           
              # Save tags with user, avoiding duplicates
            for tag_name in tags_in_content:
                tag = Tag.query.filter_by(name=tag_name, user=user).first()
                if not tag:
                    tag = Tag(name=tag_name, user=user)
                    db.session.add(tag)
                    db.session.commit()  # Commit here to ensure tag.id is available
                else:
                    tag.last_used = datetime.now()


                # Check if the tag is already associated with the entry
                if tag not in entry.tags:
                    entry.tags.append(tag)

            db.session.commit()
            return redirect(session['return_url'] or app.wrapped_url_for('main.past'))
        else:
            session['return_url'] = request.referrer
            entry_id = request.args.get('entry_id')
            entry = JournalEntry.query.filter_by(id=entry_id).first()
            return render_template('update_journal_entry.html', entry = entry, user = user,entry_id=entry_id)
    
    #show_journal_entry
    @bp.route('/unblur_journal_entry', methods=['GET'])
    def unblur_journal_entry():
        user = get_remote_user()
        entry_id = request.args.get('entry_id')
        entry = JournalEntry.query.filter_by(id=entry_id).first()
        entry.visible = True
        db.session.commit()
        return redirect(request.referrer or app.wrapped_url_for('main.past'))
    
    #hide_journal_entry
    @bp.route('/blur_journal_entry', methods=['GET'])
    def blur_journal_entry():
        user = get_remote_user()
        entry_id = request.args.get('entry_id')
        entry = JournalEntry.query.filter_by(id=entry_id).first()
        entry.visible = False
        db.session.commit()
        return redirect(request.referrer or app.wrapped_url_for('main.past'))
        


    @bp.route('/delete_journal_entry', methods=['GET'])
    def delete_journal_entry():
        user = get_remote_user()
        entry_id = request.args.get('entry_id')
        entry = JournalEntry.query.options(joinedload(JournalEntry.tags)).filter_by(id=entry_id).first()
        # Copy the list of tags before deleting the entry
        tags = entry.tags[:]


        # Check for orphaned tags and delete them
        for tag in tags:
            if tag.is_orphaned():
                print("deleting tag", tag)
                db.session.delete(tag)
        db.session.delete(entry)
        db.session.commit()
        return redirect(session['return_url'] or app.wrapped_url_for('main.past'))
    
    @bp.route('/past')
    def past():
        user = get_remote_user()
        file_attachment_manager = FileAttachmentManager(app, user)

        if session.get('past_saying'):
            if session.get('past_saying_set_time') + 15 < time.time():
                past_saying= random.choice(PAST_SAYINGS)
                session['past_saying'] = past_saying
                session['past_saying_set_time'] = time.time()
            past_saying = session.get('past_saying')
        else:   
            past_saying = random.choice(PAST_SAYINGS)
            session['past_saying'] = past_saying
            session['past_saying_set_time'] = time.time()
        entries = JournalEntry.query.options(joinedload(JournalEntry.tags)).filter_by(user=user).order_by(JournalEntry.timestamp.desc()).all()

        entries_with_attachements = []
        for entry in entries:
            attachements = file_attachment_manager.get_files(entry.id)
            entries_with_attachements.append((entry,attachements))
        return render_template('past.html', entries_with_attachements=entries_with_attachements, user = user,past_saying=past_saying)
    
    @bp.route('/download_attachment', methods=['GET'])
    def download_attachment():
        user = get_remote_user()
        entry_id = request.args.get('entry_id')
        file_name = request.args.get('file_name')
        file_attachment_manager = FileAttachmentManager(app, user)
        return file_attachment_manager.get_file_stream(entry_id, file_name)
                                                       
    @bp.route('/on_day/<day>')
    def on_day(day):
        user = get_remote_user()
        
        # Convert day string (e.g., '2024-10-04') into a date object
        day_start = datetime.strptime(day, '%Y-%m-%d')

        # Filter journal entries that match the given day (ignoring time), and timezone
        entries = (
            JournalEntry.query.filter(
                JournalEntry.timestamp >= day_start,
                JournalEntry.timestamp < day_start + timedelta(days=1),
                JournalEntry.user == user
            )
            .order_by(JournalEntry.timestamp.desc())
            .all()
        )

        return render_template('on_day.html', entries=entries, user=user, day=day)
    
    app.register_blueprint(bp)