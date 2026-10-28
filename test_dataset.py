import pandas as pd

employees = pd.read_csv("data/input/employee.csv")
leave_requests = pd.read_csv("data/input/leave_request.csv")
expense_claims = pd.read_csv("data/input/expense_claim.csv")

print("Total employees:", len(employees))
print("Total leave requests:", len(leave_requests))
print("Total expense claims:", len(expense_claims))
