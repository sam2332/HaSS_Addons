from flask import Blueprint, render_template, request, redirect, url_for, session
from libs.models import db, JournalEntry, Tag
from libs.utils import extract_tags
from libs.utils import get_remote_user
import random
from CONST import SAYINGS,PAST_SAYINGS
import time
import uuid


def register_blueprint(app):
    bp = Blueprint('main', __name__)

    @bp.route('/', methods=['GET', 'POST'])
    def journal():
        user = get_remote_user()
        if request.method == 'POST':
            content = request.form['content']
            tags = extract_tags(content)

            # Save journal entry with user
            entry = JournalEntry(content=content, user=user)
            db.session.add(entry)
            db.session.commit()

            # Save tags with user
            for tag_name in tags:
                tag = Tag(name=tag_name, user=user, entry_id=entry.id)
                db.session.add(tag)
            db.session.commit()
            last_post_uuid = uuid.uuid4()
            session['last_post_uuid'] = last_post_uuid

            return redirect(app.wrapped_url_for('main.journal'))

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
    
    
    
    #update_journal_entry
    @bp.route('/update_journal_entry', methods=['GET', 'POST'])
    def update_journal_entry():
        user = get_remote_user()
        if request.method == 'POST':
            entry_id = request.form['entry_id']
            content = request.form['content']
            tags = extract_tags(content)

            # Save journal entry with user
            entry = JournalEntry.query.filter_by(id=entry_id).first()
            entry.content = content
            db.session.commit()

            #delete existing tags
            Tag.query.filter_by(entry_id=entry_id).delete()
            db.session.commit()
            
            #reindex tags
            for tag_name in tags:
                tag = Tag(name=tag_name, user=user, entry_id=entry.id)
                db.session.add(tag)
            db.session.commit()
            return redirect(app.wrapped_url_for('main.past'))
        else:
            entry_id = request.args.get('entry_id')
            entry = JournalEntry.query.filter_by(id=entry_id).first()
            return render_template('update_journal_entry.html', entry = entry, user = user,entry_id=entry_id)
    
    @bp.route('/delete_journal_entry', methods=['GET'])
    def delete_journal_entry():
        user = get_remote_user()
        entry_id = request.args.get('entry_id')
        entry = JournalEntry.query.filter_by(id=entry_id).first()
        Tag.query.filter_by(entry_id=entry_id).delete()
        db.session.delete(entry)
        db.session.commit()
        return redirect(app.wrapped_url_for('main.past'))
    
    @bp.route('/past')
    def past():
        user = get_remote_user()

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
        entries = JournalEntry.query.filter_by(user=user).order_by(JournalEntry.timestamp.desc()).all()
        return render_template('past.html', entries=entries, user = user,past_saying=past_saying)
    
    app.register_blueprint(bp)