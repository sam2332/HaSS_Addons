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

    @bp.route('/set_post_journal_url<page>')
    def set_post_journal_url(page):
        user = get_remote_user()
        user_settings = ConfigFile(f"{app.filesystem_paths['ADDON_FILES_DIR_PATH']}/{user}.json")
        user_settings.set("post_journal_url", page)
        return redirect(app.wrapped_url_for('settings.main'))
        
    @bp.route('/enable_auto_hasher')
    def enable_auto_hasher():
        user = get_remote_user()
        user_settings = ConfigFile(f"{app.filesystem_paths['ADDON_FILES_DIR_PATH']}/{user}.json")
        user_settings.set("EnableAutoHasher", 'true')
        return redirect(app.wrapped_url_for('settings.main'))

    @bp.route('/disable_auto_hasher')
    def disable_auto_hasher():
        user = get_remote_user()
        user_settings = ConfigFile(f"{app.filesystem_paths['ADDON_FILES_DIR_PATH']}/{user}.json")
        user_settings.set("EnableAutoHasher", 'false')
        return redirect(app.wrapped_url_for('settings.main'))
    



    @bp.route('/')
    def main():       
        user = get_remote_user()
        user_settings = ConfigFile(f"{app.filesystem_paths['ADDON_FILES_DIR_PATH']}/{user}.json")
        return render_template('settings.html',user_settings=user_settings)
    app.register_blueprint(bp)


