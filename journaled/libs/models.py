from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class JournalEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    tags = db.relationship('Tag', backref='entry', lazy=True)

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    user = db.Column(db.String(50), nullable=False)
    entry_id = db.Column(db.Integer, db.ForeignKey('journal_entry.id'), nullable=False)
