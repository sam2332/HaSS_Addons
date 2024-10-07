from libs.models import Tag
from libs.utils import get_remote_user
class HashTagAdder():
    def __init__(self):
        self.user = get_remote_user()
        self.tags = self.get_tags()
        self.tag_word_sequences = self.process_tags()

    def get_tags(self):
        try:
            return Tag.query.filter_by(user=self.user).all()
        except Exception as e:
            # Log the exception
            return []


    def process_tags(self):
        # Build tag word sequences and index
        tag_word_sequences = {}
        for tag_obj in self.tags:
            tag = tag_obj.name  # Get the tag name
            words = tag.replace('_', ' ').lower().split()
            if words:
                first_word = words[0]
                if first_word not in tag_word_sequences:
                    tag_word_sequences[first_word] = []
                tag_word_sequences[first_word].append((words, tag))
        return tag_word_sequences

    def add_hashtags(self, text):
        lines = text.splitlines()
        out = []
        for words in lines:
            words = words.split()
            n = len(words)
            i = 0
            result = []
            while i < n:
                word = words[i]
                word_lower = word.lower()
                longest_match = None
                longest_match_length = 0
                if word_lower in self.tag_word_sequences:
                    for tag_words, tag in self.tag_word_sequences[word_lower]:
                        match_length = len(tag_words)
                        if i + match_length <= n:
                            words_to_compare = [w.lower() for w in words[i:i+match_length]]
                            if words_to_compare == tag_words:
                                if match_length > longest_match_length:
                                    longest_match = tag
                                    longest_match_length = match_length
                    if longest_match:
                        result.append('#' + longest_match)
                        i += longest_match_length
                        continue
                result.append(words[i])
                i += 1
            out.append(' '.join(result))
        return '\n'.join(out)