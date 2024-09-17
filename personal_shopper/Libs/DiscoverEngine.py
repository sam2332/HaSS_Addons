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

        # Return a random sample of the available suggestions
        suggestions = random.sample(
            available_suggestions, min(count, len(available_suggestions))
        )

        # Return list of items
        return [s['item'] for s in suggestions]

    def get_categories(self):
        return sorted(self.categories)
