
import sqlite3
import pandas as pd
from pathlib import Path

# Project folder
BASE_DIR = Path(__file__).resolve().parent

# File paths
csv_path = BASE_DIR / "data" / "input" / "leave_balance.csv"
db_path = BASE_DIR / "leave_expense.db"

# Check CSV
if not csv_path.exists():
    raise FileNotFoundError(f"CSV not found: {csv_path}")

# Read CSV
df = pd.read_csv(csv_path)

print("CSV records:", len(df))
print("CSV columns:", df.columns.tolist())

# Import into existing database
conn = sqlite3.connect(str(db_path))

try:
    df.to_sql(
        "leave_balance",
        conn,
        if_exists="fail",
        index=False
    )
    print("Leave balance table imported successfully!")

except ValueError:
    print("Table leave_balance already exists.")
    print("No table was replaced.")

finally:
    conn.close()
