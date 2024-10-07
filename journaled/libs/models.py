from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event

db = SQLAlchemy()

tags = db.Table('tags',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True),
    db.Column('journal_entry_id', db.Integer, db.ForeignKey('journal_entry.id'), primary_key=True)
)

class JournalEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    tags = db.relationship('Tag', secondary=tags, backref=db.backref('entries', lazy='dynamic'))
    visible = db.Column(db.Boolean, default=True)

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, index=True)
    user = db.Column(db.String(50), nullable=False)
    last_used = db.Column(db.DateTime, server_default=db.func.now())
    hidden = db.Column(db.Boolean, default=False,index=True)
    __table_args__ = (db.UniqueConstraint('name', 'user', name='_user_tag_uc'),)

    # Method to check if a tag is orphaned
    def is_orphaned(self):
        return not self.entries.count()