from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from libs.models import db, JournalEntry, Tag
from libs.utils import extract_tags, extract_phrases
from libs.utils import get_remote_user
from libs.HashTagAdder import HashTagAdder
from libs.ha_datetime_helpers import update_datetime_helper
from flask import send_file, make_response
from libs.ConfigFile import ConfigFile
import random
from CONST import get_random_saying, get_random_past_saying, get_random_inspirational_quote,WritingPromptGenerator
import time
from collections import defaultdict
import logging
import uuid
from datetime import datetime, timedelta
from libs.file_attachment_manager import FileAttachmentManager
from sqlalchemy.orm import joinedload

def register_blueprint(app):
    bp = Blueprint('main', __name__)



















    @bp.route('/', methods=['GET', 'POST'])
    def journal():
        user = get_remote_user()
        user_settings = ConfigFile(f"{app.filesystem_paths['ADDON_FILES_DIR_PATH']}/{user}.json")
        file_attachment_manager = FileAttachmentManager(app,user)
        if request.method == 'POST':
            content = request.form['content']
            mood = request.form['mood']
            custom_date_used = request.form.get('custom_date_used', False)
            custom_date = request.form.get('custom_date', None)
            if custom_date_used and custom_date_used != 'false':
                print("custom date")
                print(custom_date)
                
                #its a datetime-local input so we need to convert it to a datetime object, and correct tz
                post_date = datetime.strptime(custom_date, '%Y-%m-%dT%H:%M')
                print(post_date)
                post_date = post_date.replace(tzinfo=None)
                print(post_date)
            else:
                print("no custom date")
                post_date = datetime.now()
                print(post_date)
            attachments = request.files.getlist('attachments')
            
            ah = HashTagAdder()
            if bool(user_settings.get("autohasher_enabled",'false')):
                content = ah.add_hashtags(content)
            auto_blur_tags = user_settings.get("auto_blur_tags", [])  
            keyword_datetime_helpers = user_settings.get("keyword_datetime_helpers", {})
            tags_in_content = extract_tags(content)

            # Save journal entry with user
            entry = JournalEntry(content=content, user=user,mood=mood,timestamp=post_date)
            #if any tags_in_content in auto_blur_tags then set visible to False
            
            if user_settings.get("auto_blur_mode","off") == 'partial match':
                if any(blocked_tag in tag for blocked_tag in auto_blur_tags for tag in tags_in_content):
                    entry.visible = False
                    
            elif user_settings.get("auto_blur_mode","off") == 'full match':
                if set(tag.lower() for tag in tags_in_content) & set(tag.lower() for tag in auto_blur_tags):
                    entry.visible = False
        
            db.session.add(entry)
            db.session.commit()

            # Save tags with user, avoiding duplicates
            for tag_name in tags_in_content:
                logging.info(f"Found Tag: {tag_name}")
                if keyword_datetime_helpers.get(tag_name):
                    logging.info(f"Updating datetime helper for {tag_name}")
                    update_datetime_helper(keyword_datetime_helpers.get(tag_name))
                tag = Tag.query.filter_by(name=tag_name, user=user).first()
                if not tag:
                    logging.info(f"Creating new tag: {tag_name}")
                    tag = Tag(name=tag_name, user=user)
                    db.session.add(tag)
                    db.session.commit()  # Commit here to ensure tag.id is available
                else:
                    logging.info(f"Updating last used for tag: {tag_name}")
                    tag.last_used = datetime.now()

                # Check if the tag is already associated with the entry
                if tag not in entry.tags:
                    entry.tags.append(tag)

            db.session.commit()
            # Save attachments with user
            logging.info(f"Attachments: {len(attachments)}")
            for attachment in attachments:
                if attachment.filename == '':
                    continue  # Skip empty files
                logging.info(f"Saving attachment: {attachment.filename}")
                file_attachment_manager.save_file(attachment, entry.id)


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
                saying = get_random_saying()
                session['saying'] = saying
                session['saying_set_time'] = time.time()
            saying = session.get('saying')
        else:   
            saying = get_random_saying()
            session['saying'] = saying
            session['saying_set_time'] = time.time()
            
            
            
        if session.get('last_post_uuid'):
            last_post_uuid = session.get('last_post_uuid')
        else:
            last_post_uuid = uuid.uuid4()
            session['last_post_uuid'] = last_post_uuid
        inspirational_quote=None
        if user_settings.get("inspirational_quotes_enabled",'false') == 'true':
            inspirational_quote = get_random_inspirational_quote()
            
        if user_settings.get("name_override","") != "":
            user = user_settings.get("name_override")
        wpg = WritingPromptGenerator()
        writing_prompt = ""
        if user_settings.get("writing_prompt_count",0) > 0:
            writing_prompt_count = int(user_settings.get("writing_prompt_count",0))
            for i in range(writing_prompt_count):
                writing_prompt +=  wpg.get_next_prompt() + "\n> \n\n"
                
        date = datetime.now()
        return render_template('journal.html',
            date=date.strftime("%Y-%m-%dT%H:%M"),
            fdate = date.strftime("%m-%d-%Y"),
            user = user,
            saying=saying,
            last_post_uuid =last_post_uuid,
            inspirational_quote=inspirational_quote,
            writing_prompt=writing_prompt
        )
    
    
    
    
    
    
    
    # generate_random_question
    @bp.route('/generate_random_question', methods=['POST'])
    def generate_random_question():
        data = request.get_json()  # Parse JSON data from the request
        existing_content = data.get('content', [])  # Get content from JSON, defaulting to empty list
        
        user = get_remote_user()
        user_settings = ConfigFile(f"{app.filesystem_paths['ADDON_FILES_DIR_PATH']}/{user}.json")
        
        # Generate the writing prompt
        wpg = WritingPromptGenerator(existing_content=existing_content)
        writing_prompt = wpg.get_next_prompt() + "\n> \n\n"
        
        # Return the writing prompt as a JSON response
        return jsonify(prompt=writing_prompt), 200

    
    
    
    
    
        
    from calendar import monthrange
    from datetime import datetime

    @bp.route('/mood_calendar/<int:year>/<int:month>')
    def mood_calendar(year, month):
        user = get_remote_user()
        user_settings = ConfigFile(f"{app.filesystem_paths['ADDON_FILES_DIR_PATH']}/{user}.json")
        if user_settings.get("name_override","") != "":
            user = user_settings.get("name_override")
        entries = JournalEntry.query.filter_by(user=user).all()
        mood_calendar = {}

        # Organize mood data by date
        for entry in entries:
            entry_date = entry.timestamp.date()
            if entry_date.year == year and entry_date.month == month:
                if entry_date not in mood_calendar:
                    mood_calendar[entry_date] = {}
                if entry.mood not in mood_calendar[entry_date]:
                    mood_calendar[entry_date][entry.mood] = 1
                else:
                    mood_calendar[entry_date][entry.mood] += 1

        # Days in month and starting weekday
        days_in_month = monthrange(year, month)[1]
        start_day = datetime(year, month, 1).weekday()

        return render_template(
            'mood_calendar.html',
            user=user,
            mood_calendar=mood_calendar,
            year=year,
            month=month,
            days_in_month=days_in_month,
            start_day=start_day
        )

        
        
        
        
    
    
    
    
    
    #update_journal_entry
    @bp.route('/update_journal_entry', methods=['GET', 'POST'])
    def update_journal_entry():
        user = get_remote_user()
        user_settings = ConfigFile(f"{app.filesystem_paths['ADDON_FILES_DIR_PATH']}/{user}.json")
            
        file_attachment_manager = FileAttachmentManager(app,user)
        if request.method == 'POST':
            entry_id = request.form['entry_id']
            content = request.form['content']
            mood = request.form['mood']
            ah = HashTagAdder()
            if bool(user_settings.get("autohasher_enabled",'false')):
                content = ah.add_hashtags(content)
            tags_in_content = extract_tags(content)
            attachments = request.files.getlist('attachements')

            auto_blur_tags = user_settings.get("auto_blur_tags", [])
            # Save journal entry with user
            entry = JournalEntry.query.filter_by(id=entry_id).first()
            entry.content = content
            entry.mood = mood
            if user_settings.get("auto_blur_mode","off") == 'partial match':
                if any(blocked_tag in tag for blocked_tag in auto_blur_tags for tag in tags_in_content):
                    entry.visible = False

            elif user_settings.get("auto_blur_mode","off") == 'full match':
                if set(tag.lower() for tag in tags_in_content) & set(tag.lower() for tag in auto_blur_tags):
                    entry.visible = False
            db.session.commit()

            # Save attachements with user   
            for attachement in attachments:
                file_attachment_manager.save_file(attachement, entry.id)

            #delete existing tags
            for tag in entry.tags:
                entry.tags.remove(tag)
            db.session.commit()
            
            keyword_datetime_helpers = user_settings.get("keyword_datetime_helpers", {})
            # Save tags with user, avoiding duplicates
            for tag_name in tags_in_content:
                
                logging.info(f"Found Tag: {tag_name}")
                if keyword_datetime_helpers.get(tag_name):
                    logging.info(f"Updating datetime helper for {tag_name}")
                    update_datetime_helper(keyword_datetime_helpers.get(tag_name))
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
            return_url = session.get('return_url', app.wrapped_url_for('main.past'))
            if return_url is None:
                return_url = app.wrapped_url_for('main.past')   
            return redirect(return_url)
        else:
            session['return_url'] = request.referrer
            entry_id = request.args.get('entry_id')
            entry = JournalEntry.query.filter_by(id=entry_id).first()
            
            if user_settings.set("name_override","") != "":
                user = user_settings.get("name_override")
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
        




    
    
    
    
    
    #delete file
    @bp.route('/delete_file', methods=['GET'])
    def delete_file():
        user = get_remote_user()
        entry_id = request.args.get('entry_id')
        file_name = request.args.get('file_name')
        file_attachment_manager = FileAttachmentManager(app, user)
        file_attachment_manager.delete_file(entry_id, file_name)
        return redirect(app.wrapped_url_for('main.update_journal_entry', entry_id=entry_id))
    
    
    
    
    



    @bp.route('/delete_journal_entry', methods=['GET'])
    def delete_journal_entry():
        user = get_remote_user()
        file_attachment_manager = FileAttachmentManager(app, user)
        entry_id = request.args.get('entry_id')
        entry = JournalEntry.query.options(joinedload(JournalEntry.tags)).filter_by(id=entry_id).first()
        # Copy the list of tags before deleting the entry
        tags = entry.tags[:]


        # Check for orphaned tags and delete them
        for tag in tags:
            if tag.is_orphaned(when_removing=entry):
                db.session.delete(tag)
        db.session.delete(entry)
        db.session.commit()
        
        file_attachment_manager.delete_all_files(entry_id)
        return_url = session.get('return_url', app.wrapped_url_for('main.past'))
        if return_url is None:
            return_url = app.wrapped_url_for('main.past')   
        return redirect(return_url)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    @bp.route('/past')
    def past():
        user = get_remote_user()
        file_attachment_manager = FileAttachmentManager(app, user)
        user_settings = ConfigFile(f"{app.filesystem_paths['ADDON_FILES_DIR_PATH']}/{user}.json")
        if session.get('past_saying'):
            if session.get('past_saying_set_time') + 15 < time.time():
                past_saying= get_random_past_saying()
                session['past_saying'] = past_saying
                session['past_saying_set_time'] = time.time()
            past_saying = session.get('past_saying')
        else:   
            past_saying = get_random_past_saying()
            session['past_saying'] = past_saying
            session['past_saying_set_time'] = time.time()
        entries = JournalEntry.query.options(joinedload(JournalEntry.tags)).filter_by(user=user).order_by(JournalEntry.timestamp.desc()).all()
        
        tally_entries = [f if f.timestamp > datetime.now() - timedelta(days=10) else None for f in entries]
        #over the last 10 days, tally up the moods
        mood_tally = defaultdict(int)
        for entry in tally_entries:
            if entry is not None:
                if entry.mood is not None and entry.mood != "":
                    mood_tally[entry.mood]+=1
        mood_tally = dict(sorted(mood_tally.items(), key=lambda item: item[1],reverse=True))

        entries_with_attachements = []
        for entry in entries:
            attachements = file_attachment_manager.get_files(entry.id)
            entries_with_attachements.append((entry,attachements))
            
            
        if user_settings.get("name_override","") != "":
            user = user_settings.get("name_override")
            
            
            
        
    
        now = datetime.now()
        this_months_mood_calendar = app.wrapped_url_for('main.mood_calendar', year=now.year, month=now.month)


        return render_template('past.html', entries_with_attachements=entries_with_attachements, user = user,past_saying=past_saying,mood_tally=mood_tally,this_months_mood_calendar=this_months_mood_calendar)














    @bp.route('/download_attachment', methods=['GET'])
    def download_attachment():
        user = get_remote_user()
        entry_id = request.args.get('entry_id')
        file_name = request.args.get('file_name')
        file_attachment_manager = FileAttachmentManager(app, user)

        # Get the file stream (assuming it's a BytesIO or similar)
        file_stream = file_attachment_manager.get_file_stream(entry_id, file_name)

        # Create a response with the file stream
        response = make_response(file_stream)

        # Set headers for downloading the file
        response.headers['Content-Disposition'] = f'attachment; filename={file_name}'
        response.headers['Content-Type'] = 'application/octet-stream'

        return response

    @bp.route('/on_day/<day>')
    def on_day(day):
        user = get_remote_user()
        user_settings = ConfigFile(f"{app.filesystem_paths['ADDON_FILES_DIR_PATH']}/{user}.json")
        
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
        if user_settings.get("name_override","") != "":
            user = user_settings.get("name_override")
        return render_template('on_day.html', entries=entries, user=user, day=day)
    
    
    @bp.route('/phrases')
    def phrases():
        user = get_remote_user()
        user_settings = ConfigFile(f"{app.filesystem_paths['ADDON_FILES_DIR_PATH']}/{user}.json")
        if user_settings.get("name_override","") != "":
            user = user_settings.get("name_override")
        
        
        entries = JournalEntry.query.filter_by(user=user).all()
        phrases = defaultdict(int)
        for entry in entries:
            c_phrases = extract_phrases(entry.content)
            for phrase in c_phrases:
                phrases[phrase]+=1
                
        #sort descending
        phrases = dict(sorted(phrases.items(), key=lambda item: item[1],reverse=True))
        
        #remove symbols with only spaces around them from phrases
        for item in phrases:
            p_words = item.split()
            for word in p_words:
                if word in ['.',',','!','?',';',':','(',')','[',']','{','}','-','_','"','\'','’','‘','“','”','…','—','–','*','+','/','\\','|','<','>']:
                    phrases[item] = 0
                    
        #dont show phrases that occures only once
        phrases = {k: v for k, v in phrases.items() if v > 1}
        return render_template('phrases.html', user=user,phrases=phrases,fluid_layout=True)
    
    
    
    #search get=q
    @bp.route('/search')
    def search():
        user = get_remote_user()
        user_settings = ConfigFile(f"{app.filesystem_paths['ADDON_FILES_DIR_PATH']}/{user}.json")
        if user_settings.get("name_override","") != "":
            user = user_settings.get("name_override")
        q = request.args.get('q')
        entries = JournalEntry.query.filter(JournalEntry.content.contains(q),JournalEntry.user == user).all()
        return render_template('search.html', entries=entries, user=user, q=q)
    
    
    
    
    app.register_blueprint(bp)