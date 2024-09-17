import csv
import random

class DiscoverEngine:
    def __init__(self):
        self.csv_file = "/app/Discovery.csv"
        self.possible_suggestions = []
        self.categories = set()
        self.load()

    def load(self):
        with open(self.csv_file, newline='') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip header row if it exists
            for row in reader:
                if len(row) >= 2:
                    category = row[0]
                    item = row[1]
                    self.possible_suggestions.append({'category': category, 'item': item})
                    self.categories.add(category)

    def discover(self, count=15, todo_list=[], category=None):
        # Filter suggestions based on the single category if provided
        if category:
            filtered_suggestions = [
                s for s in self.possible_suggestions if s['category'] == category
            ]
        else:
            filtered_suggestions = self.possible_suggestions

        # Exclude items already in the todo list
        available_suggestions = [
            s for s in filtered_suggestions if s['item'] not in todo_list
        ]

        # Select a random sample of available suggestions
        suggestions = random.sample(
            available_suggestions, min(count, len(available_suggestions))
        )

        # Sort the selected suggestions alphabetically by 'item' before returning
        sorted_suggestions = sorted(suggestions, key=lambda x: x['item'])

        # Return list of sorted items
        return [s['item'] for s in sorted_suggestions]

    def get_categories(self):
        return sorted(self.categories)

    def get_suggestion_count(self):
        return len(self.possible_suggestions)
    
    def lookup_category(self, item):
        for suggestion in self.possible_suggestions:
            if suggestion['item'] == item:
                return suggestion['category']
        return None
