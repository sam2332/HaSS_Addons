from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from collections import defaultdict

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
    mood = db.Column(db.String(50))
    visible = db.Column(db.Boolean, default=True)
    def get_mood(self):
        if self.mood:
            if self.mood != "" and self.mood != "None":
                return self.mood
        return None
class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, index=True)
    user = db.Column(db.String(50), nullable=False)
    last_used = db.Column(db.DateTime, server_default=db.func.now())
    hidden = db.Column(db.Boolean, default=False,index=True)
    __table_args__ = (db.UniqueConstraint('name', 'user', name='_user_tag_uc'),)

    def is_orphaned(self, when_removing=None):
        query = self.entries
        if when_removing:
            # Assuming `when_removing` is an instance of JournalEntry
            query = query.filter(JournalEntry.id != when_removing.id)
        return query.count() == 0
    def get_most_common_mood(self):
        moods = defaultdict(int)
        for entry in self.entries:
            if entry.mood:
                if entry.mood != "" and entry.mood != "None":
                    moods[entry.mood] += 1
        #if all moods are same level of commonality, return None
        if len(moods) > 1 and len(set(moods.values())) == 1:
            return None
        if moods:
            return max(moods, key=moods.get)
        
        
        return None
    def get_mood_counts(self):
        moods = defaultdict(int)
        for entry in self.entries:
            if entry.mood:
                if entry.mood != "" and entry.mood != "None":
                    moods[entry.mood] += 1
        moods = sorted(moods.items(), key=lambda x: x[1], reverse=True)
        return dict(moods)
    