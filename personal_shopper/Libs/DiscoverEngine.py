import csv
import random

class DiscoverEngine:
    def __init__(self):
        self.csv_file = "/app/Discovery.csv"
        self.load()

    def load(self):
        self.possible_suggestions = []
        with open(self.csv_file, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                self.possible_suggestions.append(row[0])

    def discover(self, count=15, todo_list=[]):
        # Exclude items already in the todo list
        available_suggestions = set(self.possible_suggestions) - set(todo_list)
        # Return a random sample of the available suggestions
        return random.sample(
            available_suggestions, min(count, len(available_suggestions))
        )
