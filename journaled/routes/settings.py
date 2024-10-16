from flask import Blueprint, render_template, request, redirect, Response
import random
import time
import uuid
import io
import csv
import logging
from libs.ConfigFile import ConfigFile
from libs.HashTagAdder import HashTagAdder
from libs.models import db, JournalEntry, Tag
from libs.utils import get_remote_user
from collections import defaultdict
from libs.utils import extract_tags
from libs.ha_datetime_helpers import  list_datetime_helpers, update_datetime_helper
import requests
import os
from datetime import datetime

def register_blueprint(app):
    bp = Blueprint('settings', __name__, url_prefix='/settings')

    @bp.route('/set_post_journal_url/<page>')
    def set_post_journal_url(page):
        user = get_remote_user()
        user_settings = ConfigFile(f"{app.filesystem_paths['ADDON_FILES_DIR_PATH']}/{user}.json")
        user_settings.set("post_journal_url", page)
        return redirect(app.wrapped_url_for('settings.main'))
    
    @bp.route('/set_auto_blur_mode/<mode>')
    def set_auto_blur_mode(mode):
        user = get_remote_user()
        user_settings = ConfigFile(f"{app.filesystem_paths['ADDON_FILES_DIR_PATH']}/{user}.json")
        user_settings.set("auto_blur_mode", mode)
        return redirect(app.wrapped_url_for('settings.main'))
    
    @bp.route('/enable_auto_hasher')
    def enable_auto_hasher():
        user = get_remote_user()
        user_settings = ConfigFile(f"{app.filesystem_paths['ADDON_FILES_DIR_PATH']}/{user}.json")
        user_settings.set("autohasher_enabled", 'true')
        return redirect(app.wrapped_url_for('settings.main'))

    @bp.route('/disable_auto_hasher')
    def disable_auto_hasher():
        user = get_remote_user()
        user_settings = ConfigFile(f"{app.filesystem_paths['ADDON_FILES_DIR_PATH']}/{user}.json")
        user_settings.set("autohasher_enabled", 'false')
        return redirect(app.wrapped_url_for('settings.main'))
    



    @bp.route('/')
    def main():       
        user = get_remote_user()
        user_settings = ConfigFile(f"{app.filesystem_paths['ADDON_FILES_DIR_PATH']}/{user}.json")
        return render_template('settings.html',user_settings=user_settings)

    @bp.route('/add_hashtag', methods=['POST'])
    def add_hashtag():
        user = get_remote_user()
        user_settings = ConfigFile(f"{app.filesystem_paths['ADDON_FILES_DIR_PATH']}/{user}.json")
        tag = request.form['tag']
        tag = tag.lower()
        tags = user_settings.get("auto_blur_tags", [])
        tags.append(tag)
        user_settings.set("auto_blur_tags", tags)
        return redirect(app.wrapped_url_for('settings.main'))
    
    @bp.route('/remove_hashtag/<tag>')
    def remove_hashtag(tag):
        user = get_remote_user()
        user_settings = ConfigFile(f"{app.filesystem_paths['ADDON_FILES_DIR_PATH']}/{user}.json")
        tags = user_settings.get("auto_blur_tags", [])
        tags.remove(tag)
        user_settings.set("auto_blur_tags", tags)
        return redirect(app.wrapped_url_for('settings.main'))



    @bp.route('/keyword_helper_manager')
    def keyword_helper_manager():
        user = get_remote_user()
        input_helpers = list_datetime_helpers()
        user_settings = ConfigFile(f"{app.filesystem_paths['ADDON_FILES_DIR_PATH']}/{user}.json")
        keyword_datetime_helpers = user_settings.get("keyword_datetime_helpers", {})
        logging.info(input_helpers)  
        return render_template('keyword_helper_manager.html', keyword_datetime_helpers=keyword_datetime_helpers,input_helpers=input_helpers)

    @bp.route('/add_keyword_datetime_helper', methods=['POST'])
    def add_keyword_datetime_helper():
        user = get_remote_user()
        user_settings = ConfigFile(f"{app.filesystem_paths['ADDON_FILES_DIR_PATH']}/{user}.json")
        hashtag = request.form['hashtag']
        helper = request.form['helper']
        keyword_datetime_helpers = user_settings.get("keyword_datetime_helpers", {})
        keyword_datetime_helpers[hashtag] = helper
        user_settings.set("keyword_datetime_helpers", keyword_datetime_helpers)
        return redirect(app.wrapped_url_for('settings.keyword_helper_manager'))

    @bp.route('/remove_keyword_datetime_helper/<hashtag>')
    def remove_keyword_datetime_helper(hashtag):
        user = get_remote_user()
        user_settings = ConfigFile(f"{app.filesystem_paths['ADDON_FILES_DIR_PATH']}/{user}.json")
        keyword_datetime_helpers = user_settings.get("keyword_datetime_helpers", {})
        if hashtag in keyword_datetime_helpers:
            # Optional: Add API call to remove the helper from Home Assistant
            keyword_datetime_helpers.pop(hashtag)
            user_settings.set("keyword_datetime_helpers", keyword_datetime_helpers)
        return redirect(app.wrapped_url_for('settings.keyword_helper_manager'))




    @bp.route('/set_max_word_cloud_count', methods=['POST', 'GET'])
    def set_max_word_cloud_count(count):
        user = get_remote_user()
        user_settings = ConfigFile(f"{app.filesystem_paths['ADDON_FILES_DIR_PATH']}/{user}.json")
        count = request.form['count']
        user_settings.set("max_word_cloud_count", count)
        return redirect(request.referrer or app.wrapped_url_for('settings.main'))


    #toggle_inspirational_quotes
    @bp.route('/toggle_inspirational_quotes')
    def toggle_inspirational_quotes():
        user = get_remote_user()
        user_settings = ConfigFile(f"{app.filesystem_paths['ADDON_FILES_DIR_PATH']}/{user}.json")
        if user_settings.get("inspirational_quotes_enabled",'false') == 'true':
            user_settings.set("inspirational_quotes_enabled", 'false')
        else:
            user_settings.set("inspirational_quotes_enabled", 'true')
        return redirect(request.referrer or app.wrapped_url_for('settings.main'))
    
                    
    @bp.route('/set_name_override', methods=['POST'])
    def set_name_override():
        user = get_remote_user()
        user_settings = ConfigFile(f"{app.filesystem_paths['ADDON_FILES_DIR_PATH']}/{user}.json")
        name_override = request.form['name_override']
        user_settings.set("name_override", name_override)
        return redirect(app.wrapped_url_for('settings.main'))
    app.register_blueprint(bp)
