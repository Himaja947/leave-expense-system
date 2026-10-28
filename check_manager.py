
import sqlite3
from pathlib import Path

db_path = Path(__file__).resolve().parent / "leave_expense.db"

conn = sqlite3.connect(db_path)

columns = conn.execute(
    "PRAGMA table_info(leave_submissions)"
).fetchall()

print("Leave submission columns:")

for column in columns:
    print(column[1])

conn.close()
