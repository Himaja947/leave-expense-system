
import sqlite3

conn = sqlite3.connect("leave_expense.db")
conn.row_factory = sqlite3.Row

rows = conn.execute("""
    SELECT
        request_id,
        employee_id,
        status,
        manager_id
    FROM leave_submissions
    ORDER BY created_at DESC
""").fetchall()

for row in rows:
    print(dict(row))

conn.close()
