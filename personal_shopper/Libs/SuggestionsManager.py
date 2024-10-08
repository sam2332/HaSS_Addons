import sqlite3
import os
import re
from Libs.CategoryEngine import CategoryEngine


class SuggestionsManager:
    def __init__(self,db_file):
        self.db_file = db_file
        needs_setup = False
        if not os.path.exists(db_file):
            needs_setup = True
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        if needs_setup:
            self.create_table()
        else:
            self.add_delayed_to_database()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS lists (
                item TEXT PRIMARY KEY,
                last_completed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                times_completed INTEGER DEFAULT 0,
                delayed_until TIMESTAMP,
                category TEXT
            )
        ''')
        self.conn.commit()
        
    def add_delayed_to_database(self):
        # check if column exists
        self.cursor.execute('''PRAGMA table_info(lists)''')
        columns = self.cursor.fetchall()
        for column in columns:
            if column[1] == 'delayed_until':
                return
            
        # add column to database
        self.cursor.execute('''
            ALTER TABLE lists
            ADD COLUMN delayed_until TIMESTAMP
        ''')
        self.conn.commit()
        
    def delay_item(self, item_name, delay_days):
        item_name = self.normalize_name(item_name)
        self.cursor.execute('''
            UPDATE lists
            SET delayed_until = datetime('now', ? || ' days')
            WHERE item = ?
        ''', (delay_days, item_name))
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

    def suggest_items(self, existing_items, max_items, category=None, cooldown_days=None, respect_delayed=True):
        """
        Suggest items not in existing_items, optionally filtered by category and cooldown period,
        ordered by times_completed descending and last_completed descending.
        
        :param existing_items: List of items to exclude from suggestions.
        :param max_items: Maximum number of items to suggest.
        :param category: (Optional) Category to filter suggestions.
        :param cooldown_days: (Optional) Minimum number of days since last_completed.
        :return: List of suggested item names.
        """
        # Normalize existing items before querying
        existing_items = [self.normalize_name(item) for item in existing_items]
        
        query_conditions = []
        params = []

        if existing_items:
            placeholders = ', '.join('?' for _ in existing_items)
            query_conditions.append(f"item NOT IN ({placeholders})")
            params.extend(existing_items)
        
        if category:
            query_conditions.append("category = ?")
            params.append(category)
        
        if respect_delayed:
            query_conditions.append("delayed_until IS NULL OR delayed_until <= CURRENT_TIMESTAMP")
            
        if cooldown_days is not None:
            query_conditions.append("last_completed <= datetime('now', ?)")
            params.append(f'-{cooldown_days} days')
        
        where_clause = "WHERE " + " AND ".join(query_conditions) if query_conditions else ""
        
        query = f'''
            SELECT item FROM lists
            {where_clause}
            ORDER BY times_completed DESC, last_completed DESC
            LIMIT ?
        '''
        params.append(max_items)
        
        self.cursor.execute(query, params)
        return [row[0] for row in self.cursor.fetchall()]
        
    def get_categories(self,existing_items, cooldown_days,respect_delayed=True):
        """
        Retrieve a list of unique categories that have available items,
        optionally excluding delayed items.
        
        :param respect_delayed: (Optional) Whether to exclude delayed items.
        :return: List of unique category names.
        """
        # Normalize existing items before querying
        existing_items = [self.normalize_name(item) for item in existing_items]
        
        query_conditions = []
        params = []

        if existing_items:
            placeholders = ', '.join('?' for _ in existing_items)
            query_conditions.append(f"item NOT IN ({placeholders})")
            params.extend(existing_items)
        
        if respect_delayed:
            # Condition to exclude delayed items
            # This ensures that only items not delayed are considered
            query_conditions.append("delayed_until IS NULL OR delayed_until <= CURRENT_TIMESTAMP")
        
        if cooldown_days is not None:
            query_conditions.append("last_completed <= datetime('now', ?)")
            params.append(f'-{cooldown_days} days')
            
        where_clause = "WHERE " + " AND ".join(query_conditions) if query_conditions else ""
        
        query = f'''
            SELECT DISTINCT category FROM lists
            {where_clause}
            ORDER BY category ASC
        '''
        
        try:
            self.cursor.execute(query, params)
            categories = [row[0] for row in self.cursor.fetchall() if row[0]]
            return categories
        except sqlite3.Error as e:
            # Handle potential database errors
            print(f"Database error in get_categories: {e}")
            return []

    def get_all_items(self):
        self.cursor.execute('SELECT item FROM lists')
        return [row[0] for row in self.cursor.fetchall()]
    
    def update_category(self, item_name, category):
        item_name = self.normalize_name(item_name)
        self.cursor.execute('UPDATE lists SET category = ? WHERE item = ?', (category, item_name))
        self.conn.commit()

    def close(self):
        self.conn.close()