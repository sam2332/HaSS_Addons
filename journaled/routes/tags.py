from flask import Blueprint, render_template, request, abort,redirect
from libs.models import Tag, JournalEntry, db
from libs.utils import get_remote_user,extract_words,extract_tags
from CONST import STOPWORDS
from libs.ConfigFile import ConfigFile
from collections import defaultdict
from sqlalchemy import func
import logging


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
        user_settings = ConfigFile(f"{app.filesystem_paths['ADDON_FILES_DIR_PATH']}/{user}.json")

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
        word_cloud = {tag: entry_count for tag, entry_count in tags_with_counts}
        
        
        table_items = sorted(word_cloud.items(), key=lambda x: x[1], reverse=True)
        
        max_word_cloud_count = user_settings.get('max_word_cloud_count', 20)
        
        #Top max_word_cloud_count tags are displayed in the word cloud
        word_cloud = dict(sorted(word_cloud.items(), key=lambda x: x[1], reverse=True)[:max_word_cloud_count])
        
     
        # Pass the word cloud data and table items to the template
        return render_template('all_tags.html', word_cloud=word_cloud, table_items=table_items,fluid_layout=True)
    
    @bp.route('/create_tag/<tag_name>', methods=['GET'])
    def create_tag(tag_name):
        user = get_remote_user()
        tag_name = tag_name.lower().replace('%20', '_').replace(' ', '_')
        tag = Tag(name=tag_name, user=user)
        db.session.add(tag)
        db.session.commit()
        
        journal_entries = JournalEntry.query.filter_by(user=user).all()
        for entry in journal_entries:
            tags_in_content = extract_tags(entry.content)
            
            for tag in entry.tags:
                entry.tags.remove(tag)
            db.session.commit()
            for tag_name in tags_in_content:
                logging.info(f"Found Tag: {tag_name}")
                tag = Tag.query.filter_by(name=tag_name, user=user).first()
                if not tag:
                    tag = Tag(name=tag_name, user=user)
                    db.session.add(tag)
                    db.session.commit()  # Commit here to ensure tag.id is available
                if tag not in entry.tags:
                    entry.tags.append(tag)
        db.session.commit()  
        return redirect(request.referrer or app.wrapped_url_for('tags.all_tags'))


    @bp.route('/suggested_tags', methods=['GET'])
    def suggested_tags():
        user = get_remote_user()
        user_settings = ConfigFile(f"{app.filesystem_paths['ADDON_FILES_DIR_PATH']}/{user}.json")
        # [{tag: count}]
        entries = JournalEntry.query.filter_by(user=user).all()
        word_count = defaultdict(int)
        for entry in entries:
            words = extract_words(entry.content)
            for word in words:
                word_count[word] += 1     
        #only show ones with more that 8 occurances
        word_count = {k: v for k, v in word_count.items() if v > 3}
        
        all_existing_tags = Tag.query.filter_by(user=user).all()
        word_count = {k: v for k, v in word_count.items() if k not in [tag.name for tag in all_existing_tags]}
        return render_template('suggested_tags.html', word_count=word_count,fluid_layout=True) 
       
       
    @bp.route('/remove_tag/<tag_name>', methods=['GET'])
    def remove_tag(tag_name):
        user = get_remote_user()
        tag = Tag.query.filter_by(name=tag_name, user=user).first()
        if not tag:
            return render_template('tag_not_found.html', tag_name=tag_name), 404
        
        for entry in tag.entries:
            entry.content = entry.content.replace(f"#{tag_name}", tag_name)
        db.session.delete(tag)
        db.session.commit()
        
        
        return redirect(request.referrer or app.wrapped_url_for('tags.all_tags'))
    app.register_blueprint(bp)
