import sqlite3
import os

CONFIG_PATH = '/config'
ADDON_FILES_DIR_PATH = os.path.join(CONFIG_PATH,"Journal")
DB_PATH = os.path.join(ADDON_FILES_DIR_PATH, "app.db")

# Use context manager for automatic closing of resources
try:
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()

        # Compact and repair
        c.execute("VACUUM")
        c.execute("REINDEX")
        conn.commit()

        # Get dictionary of tables: table columns
        c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = c.fetchall()
        print("Tables:", tables)

        table_columns = {}
        for table in tables:
            c.execute(f"PRAGMA table_info({table[0]})")
            table_columns[table[0]] = c.fetchall()

        print("Table Columns:", table_columns)

    
    
    
    
    
    
        # Check and add "mood" column if missing
        if "journal_entry" in table_columns and "mood" not in [col[1] for col in table_columns['journal_entry']]:
            c.execute("ALTER TABLE journal_entry ADD COLUMN mood TEXT")
            conn.commit()
            print("Added 'mood' column to 'journal_entry' table.")







        print("done")

except sqlite3.Error as e:
    print(f"SQLite error: {e}")
