import sqlite3
import os


backup_delete_dryrun = False
backup_delete_duplicates = True


CONFIG_PATH = '/config'
ADDON_FILES_DIR_PATH = os.path.join(CONFIG_PATH,"Journald")
DB_PATH = os.path.join(ADDON_FILES_DIR_PATH, "app.db")

#do a dated backup of the db
import shutil
import datetime
backup_path = os.path.join(ADDON_FILES_DIR_PATH, "backups")
if not os.path.exists(backup_path):
    os.makedirs(backup_path)
backup_file = os.path.join(backup_path, "app.db." + datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
shutil.copyfile(DB_PATH, backup_file)
print("Backed up database to", backup_file)

#old db cleanup (only keep last 10)
files = os.listdir(backup_path)
files.sort()
for file in files[:-10]:
    if backup_delete_dryrun:
        print("DRYRUN - Removed old backup", file)
    else:
        os.remove(os.path.join(backup_path, file))
        print("DRYRUN - Removed old backup", file)


if backup_delete_duplicates:
    #if new backup is the same as the last one, remove it
    if os.path.exists(backup_file):
        with open(backup_file, 'rb') as f:
            new = f.read()
        with open(os.path.join(backup_path, files[-1]), 'rb') as f:
            old = f.read()
        if new == old:
            if backup_delete_dryrun:
                print("DRYRUN - Removed unchanged backup", backup_file)
            else:
                os.remove(backup_file)
                print("Removed unchanged backup", backup_file)


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
