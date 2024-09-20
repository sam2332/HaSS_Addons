# GUESS CATEGORIES, BASED ON THE ITEM_NAME
# LOAD CATEGORIES REGEX FROM THE CSV FILE 
import csv, re

class CategoryEngine:
    def __init__(self):
        self.categories = []
        with open(f'/app/Data/categories_regex.csv') as f:
            reader = csv.reader(f)
            for row in reader:
                self.categories.append(row)

    def guess(self, item_name):
        for regex,category in self.categories:
            if re.search(regex, item_name, re.IGNORECASE):
                return category
        return None