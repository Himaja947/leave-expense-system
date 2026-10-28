
import pandas as pd

file_path = "data/input/leave_balance.csv"

df = pd.read_csv(file_path)

print("Column names:")
print(df.columns.tolist())

print("\nFirst 5 rows:")
print(df.head().to_string(index=False))

print("\nTotal balance records:", len(df))
