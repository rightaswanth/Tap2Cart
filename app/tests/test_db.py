import sqlite3
from pathlib import Path

current_file = Path(__file__).resolve()
project_dir = current_file.parents[2]
db_path = project_dir / "restaurant.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(cursor.fetchall())