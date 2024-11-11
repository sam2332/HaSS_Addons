from datetime import datetime
import random


from CONST.IMPORTANT_DATES import IMPORTANT_DATES
from CONST.MOOD_COLORS import MOOD_COLORS
from CONST.WRITING_PROMPTS import WRITING_PROMPTS
from CONST.SAYINGS import SAYINGS
from CONST.INSPIRATIONAL_QUOTES import INSPIRATIONAL_QUOTES
from CONST.PAST_SAYINGS import PAST_SAYINGS




def get_mood_colors():
    return MOOD_COLORS


class WritingPromptGenerator:
    def __init__(self, existing_content=None):
        self.existing_content = existing_content
        if self.existing_content is None:
            self.existing_content = ""
        self.original_prompts = WRITING_PROMPTS.copy()
        self.prompts = WRITING_PROMPTS.copy()
        random.shuffle(self.prompts)
    def _get_next_prompt(self):
        if len(self.prompts) == 0:
            self.prompts = self.original_prompts.copy()
            random.shuffle(self.prompts)
        return self.prompts.pop()
    def get_next_prompt(self):
        tries = 15
        while tries > 0:
            prompt = self._get_next_prompt()
            if prompt not in self.existing_content:
                break
            tries -= 1
            
        prompt = prompt[0].upper() + prompt[1:]
        
        return prompt




def get_important_date(date=None):
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    for event, event_date in IMPORTANT_DATES.items():
        if event_date == date:
            return event
    return None

#functions to get random sayings/quotes
def get_random_saying():
    return random.choice(SAYINGS)

def get_random_inspirational_quote():
    return random.choice(INSPIRATIONAL_QUOTES)

def get_random_past_saying():
    return random.choice(PAST_SAYINGS)

