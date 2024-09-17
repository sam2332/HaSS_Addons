import sqlite3
import os
import re
from Libs.CategoryEngine import CategoryEngine


class SuggestionsManager:
    def __init__(self, db_file):
        self.db_file = db_file
        needs_setup = False
        if not os.path.exists(db_file):
            needs_setup = True
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        if needs_setup:
            self.create_table()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS lists (
                item TEXT PRIMARY KEY,
                last_completed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                times_completed INTEGER DEFAULT 0,
                category TEXT
            )
        ''')
        self.conn.commit()

    def normalize_name(self, name):
        """Normalize item name by stripping whitespace and replacing multiple spaces."""
        return re.sub(r'\s+', ' ', name).strip()
    
    def remove_item(self, item_name):
        """Remove an item by name."""
        item_name = self.normalize_name(item_name)
        self.cursor.execute('DELETE FROM lists WHERE item = ?', (item_name,))
        self.conn.commit()
        
    def touch_items(self, item_names):
        category_engine = CategoryEngine()
        """Update or insert multiple items in a transaction with name normalization."""
        # Normalize all item names
        item_names = [self.normalize_name(name) for name in item_names]
        
        if not item_names:
            return  # Exit early if there are no items to process

        with self.conn:
            # First update the items that already exist
            placeholders = ', '.join('?' for _ in item_names)
            query = f'''
                UPDATE lists
                SET times_completed = times_completed + 1,
                    last_completed = CURRENT_TIMESTAMP
                WHERE item IN ({placeholders})
            '''
            self.cursor.execute(query, item_names)
            
            # Generate categories for each item
            categories = [category_engine.guess(item_name) for item_name in item_names]
            
            # Prepare parameters for executemany
            params = list(zip(item_names, categories))

            # Insert only the items that don't already exist
            self.cursor.executemany('''
                INSERT INTO lists (item, times_completed, last_completed, category)
                VALUES (?, 1, CURRENT_TIMESTAMP, ?)
                ON CONFLICT(item) DO NOTHING
            ''', params)

    def suggest_items(self, existing_items, max_items, category=None):
        """Suggest items not in existing_items, filtered by category (optional), and ordered by times_completed."""
        # Normalize existing items before querying
        existing_items = [self.normalize_name(item) for item in existing_items]
        
        placeholders = ', '.join('?' for _ in existing_items)
        query = f'''
            SELECT item FROM lists
            WHERE item NOT IN ({placeholders})
            {f"AND category = ?" if category else ""}
            ORDER BY times_completed DESC, last_completed DESC
            LIMIT ?
        '''
        params = existing_items + ([category] if category else []) + [max_items]
        self.cursor.execute(query, params)
        return [row[0] for row in self.cursor.fetchall()]
    
    def get_categories(self):
        self.cursor.execute('SELECT DISTINCT category FROM lists')
        return [row[0] for row in self.cursor.fetchall() if row[0]]
    
    def get_all_items(self):
        self.cursor.execute('SELECT item FROM lists')
        return [row[0] for row in self.cursor.fetchall()]
    
    def update_category(self, item_name, category):
        item_name = self.normalize_name(item_name)
        self.cursor.execute('UPDATE lists SET category = ? WHERE item = ?', (category, item_name))
        self.conn.commit()

    def close(self):
        self.conn.close()