
import sqlite3
import os

db_path = os.path.abspath("leave_expense.db")
conn = sqlite3.connect(db_path)

columns = [
    row[1]
    for row in conn.execute(
        "PRAGMA table_info(expense_submissions)"
    ).fetchall()
]

new_columns = {
    "decision_by": "TEXT",
    "decision_note": "TEXT",
    "decided_at": "TEXT"
}

for column, data_type in new_columns.items():
    if column not in columns:
        conn.execute(
            f"ALTER TABLE expense_submissions "
            f"ADD COLUMN {column} {data_type}"
        )
        print(f"Added: {column}")
    else:
        print(f"Already exists: {column}")

conn.commit()
conn.close()

print("Expense approval columns are ready.")
