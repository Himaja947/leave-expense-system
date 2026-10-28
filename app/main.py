
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import date, datetime, timedelta
from pathlib import Path
import pandas as pd
import sqlite3
import uuid


# ---------------------------------------
# 1. CREATE FASTAPI APPLICATION
# ---------------------------------------

app = FastAPI(
    title="Leave & Expense Management System",
    version="1.0.0"
)


# ---------------------------------------
# 2. DATASET PATHS
# ---------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "input"
DB_PATH = BASE_DIR / "leave_expense.db"


# ---------------------------------------
# 3. LOAD DATASETS
# ---------------------------------------

employees = pd.read_csv(DATA_DIR / "employee.csv")
leave_requests = pd.read_csv(DATA_DIR / "leave_request.csv")
expense_claims = pd.read_csv(DATA_DIR / "expense_claim.csv")
leave_balances = pd.read_csv(DATA_DIR / "leave_balance.csv")


# Convert ID columns to strings for consistent matching
employees["employee_id"] = employees["employee_id"].astype(str)

leave_requests["employee_id"] = (
    leave_requests["employee_id"].astype(str)
)

leave_balances["employee_id"] = (
    leave_balances["employee_id"].astype(str)
)

leave_balances["leave_policy_id"] = (
    leave_balances["leave_policy_id"].astype(str)
)


# ---------------------------------------
# 4. DATABASE SETUP
# ---------------------------------------

def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    return conn

def create_expense_table():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expense_submissions (
                expense_claim_id TEXT PRIMARY KEY,
                employee_id TEXT NOT NULL,
                submitted_date TEXT NOT NULL,
                country TEXT NOT NULL,
                cost_center_id TEXT NOT NULL,
                expense_policy_id TEXT NOT NULL,
                total_amount REAL NOT NULL,
                currency TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'PENDING',
                issue_type TEXT DEFAULT '',
                ground_truth TEXT DEFAULT 'NORMAL',
                created_at TEXT NOT NULL
            )
        """)


def add_manager_column():
    with get_connection() as conn:
        columns = [
            row["name"]
            for row in conn.execute(
                "PRAGMA table_info(leave_submissions)"
            ).fetchall()
        ]

        if "manager_id" not in columns:
            conn.execute("""
                ALTER TABLE leave_submissions
                ADD COLUMN manager_id TEXT
            """)



def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS leave_submissions (
                request_id TEXT PRIMARY KEY,
                employee_id TEXT NOT NULL,
                leave_policy_id TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                requested_days INTEGER NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                decision_by TEXT,
                decision_note TEXT,
                decided_at TEXT,
                manager_id TEXT
            )
        """)

        # Add columns if the table was created earlier
        columns = {
            row["name"]
            for row in conn.execute(
                "PRAGMA table_info(leave_submissions)"
            ).fetchall()
        }

        if "decision_by" not in columns:
            conn.execute(
                "ALTER TABLE leave_submissions "
                "ADD COLUMN decision_by TEXT"
            )

        if "decision_note" not in columns:
            conn.execute(
                "ALTER TABLE leave_submissions "
                "ADD COLUMN decision_note TEXT"
            )

        if "decided_at" not in columns:
            conn.execute(
                "ALTER TABLE leave_submissions "
                "ADD COLUMN decided_at TEXT"
            )
        if "manager_id" not in columns:
            conn.execute(
                "ALTER TABLE leave_submissions "
                "ADD COLUMN manager_id TEXT"
            )

init_db()
create_expense_table()



# ---------------------------------------
# 5. REQUEST MODEL
# ---------------------------------------

class LeaveRequestInput(BaseModel):
    employee_id: str
    leave_policy_id: str
    start_date: date
    end_date: date


class ApprovalDecision(BaseModel):
    decision: str
    manager_id: str
    comment: str = ""

class ExpenseDecisionInput(BaseModel):
    decision: str
    manager_id: str
    comment: str = ""


class ExpenseRequestInput(BaseModel):
    employee_id: str
    submitted_date: date
    country: str
    cost_center_id: str
    expense_policy_id: str
    total_amount: float
    currency: str


# ---------------------------------------
# 6. HOME API
# ---------------------------------------

@app.get("/")
def home():
    return {
        "message": "Leave & Expense Management API is running"
    }


# ---------------------------------------
# 7. HEALTH API
# ---------------------------------------

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# ---------------------------------------
# 8. GET ALL EMPLOYEES
# ---------------------------------------

@app.get("/employees")
def get_employees():
    return employees.fillna("").to_dict(orient="records")


# ---------------------------------------
# 9. GET ALL LEAVE REQUESTS
# ---------------------------------------

@app.get("/leave-requests")
def get_leave_requests():
    return leave_requests.fillna("").to_dict(orient="records")


# ---------------------------------------
# 10. GET ALL EXPENSE CLAIMS
# ---------------------------------------

@app.get("/expense-claims")
def get_expense_claims():
    return expense_claims.fillna("").to_dict(orient="records")

# SUBMIT EXPENSE CLAIM

@app.post("/expense-claims")
def submit_expense_claim(request: ExpenseRequestInput):

    # 1. Validate employee
    employee = employees[
        employees["employee_id"] == request.employee_id
    ]

    if employee.empty:
        return {"message": "Employee not found"}

    # 2. Validate active status
    active = str(employee.iloc[0]["active"]).strip().lower()

    if active not in ["true", "1", "yes", "active"]:
        return {"message": "Employee is inactive"}

    # 3. Validate amount
    if request.total_amount <= 0:
        return {"message": "Amount must be greater than zero"}

    # 4. Generate claim ID
    claim_id = "EXP-SUB-" + str(uuid.uuid4())

    created_time = datetime.now().isoformat()

    # 5. Save expense claim
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO expense_submissions (
                expense_claim_id,
                employee_id,
                submitted_date,
                country,
                cost_center_id,
                expense_policy_id,
                total_amount,
                currency,
                status,
                issue_type,
                ground_truth,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            claim_id,
            request.employee_id,
            request.submitted_date.isoformat(),
            request.country,
            request.cost_center_id,
            request.expense_policy_id,
            request.total_amount,
            request.currency,
            "PENDING",
            "",
            "NORMAL",
            created_time
        ))

    return {
        "message": "Expense claim submitted successfully",
        "expense_claim_id": claim_id,
        "employee_id": request.employee_id,
        "total_amount": request.total_amount,
        "currency": request.currency,
        "status": "PENDING"
    }

# VIEW SAVED EXPENSE CLAIMS

@app.get("/saved-expense-claims")
def get_saved_expense_claims():
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT *
            FROM expense_submissions
            ORDER BY created_at DESC
        """).fetchall()

    return [dict(row) for row in rows]

# EXPENSE CLAIM APPROVAL / REJECTION

@app.post("/saved-expense-claims/{claim_id}/decision")
def decide_expense_claim(
    claim_id: str,
    request: ExpenseDecisionInput
):
    decision = request.decision.strip().upper()

    if decision not in ["APPROVED", "REJECTED"]:
        return {"message": "Invalid decision"}

    if not request.manager_id.strip():
        return {"message": "Manager ID is required"}

    with get_connection() as conn:

        # 1. Find expense claim
        claim = conn.execute(
            """
            SELECT *
            FROM expense_submissions
            WHERE expense_claim_id = ?
            """,
            (claim_id,)
        ).fetchone()

        if claim is None:
            return {"message": "Expense claim not found"}

        # 2. Prevent duplicate decisions
        if claim["status"] != "PENDING":
            return {
                "message": "This claim has already been decided",
                "current_status": claim["status"]
            }

        # 3. Save decision
        cursor = conn.execute(
            """
            UPDATE expense_submissions
            SET status = ?,
                decision_by = ?,
                decision_note = ?,
                decided_at = CURRENT_TIMESTAMP
            WHERE expense_claim_id = ?
              AND status = 'PENDING'
            """,
            (
                decision,
                request.manager_id.strip(),
                request.comment,
                claim_id
            )
        )

        if cursor.rowcount != 1:
            return {
                "message": "Decision was not recorded. Please retry."
            }

        # 4. Return updated claim
        updated_claim = conn.execute(
            """
            SELECT *
            FROM expense_submissions
            WHERE expense_claim_id = ?
            """,
            (claim_id,)
        ).fetchone()

        return {
            "message": "Expense decision recorded successfully",
            "claim": dict(updated_claim)
        }



# ---------------------------------------
# 11. GET EMPLOYEE LEAVE BALANCE
# ---------------------------------------


@app.get("/leave-balance/{employee_id}")
def get_leave_balance(employee_id: str):

    with get_connection() as conn:
        rows = conn.execute("""
            SELECT *
            FROM leave_balance
            WHERE employee_id = ?
            ORDER BY leave_policy_id
        """, (employee_id,)).fetchall()

        if not rows:
            return {
                "message": "Employee leave balance not found"
            }

        return [dict(row) for row in rows]



# ---------------------------------------
# 12. SUBMIT LEAVE REQUEST
# ---------------------------------------

@app.post("/leave-requests")
def submit_leave_request(request: LeaveRequestInput):

    # 1. Check employee
    employee = employees[
        employees["employee_id"] == request.employee_id
    ]

    if employee.empty:
        return {"message": "Employee not found"}

    # 2. Check active status
    active = str(employee.iloc[0]["active"]).strip().lower()

    if active not in ["true", "1", "yes", "active"]:
        return {"message": "Employee is inactive"}

    # 3. Validate dates
    if request.end_date < request.start_date:
        return {
            "message": "End date cannot be before start date"
        }

    # 4. Calculate weekdays
    business_days = sum(
        1
        for day_offset in range(
            (request.end_date - request.start_date).days + 1
        )
        if (
            request.start_date + timedelta(days=day_offset)
        ).weekday() < 5
    )

    if business_days == 0:
        return {
            "message": "No business days in selected dates"
        }

    
    # 5. Check leave balance record from SQLite
    period_year = request.start_date.year

    with get_connection() as conn:
        balance = conn.execute("""
            SELECT available_days
            FROM leave_balance
            WHERE employee_id = ?
              AND leave_policy_id = ?
              AND period_year = ?
        """, (
            request.employee_id,
            request.leave_policy_id,
            period_year
        )).fetchone()

    if balance is None:
        return {
            "message": "Leave balance not found"
        }

    available = float(balance["available_days"])

    if business_days > available:
        return {
            "message": "Insufficient leave balance",
            "available_days": available,
            "requested_days": business_days
        }


    # 6. Check overlapping requests from dataset
    existing = leave_requests[
        (leave_requests["employee_id"] == request.employee_id)
        & (
            leave_requests["status"]
            .astype(str)
            .str.upper()
            .isin(["APPROVED", "PENDING"])
        )
    ]

    for _, row in existing.iterrows():

        old_start = pd.to_datetime(
            row["start_date"]
        ).date()

        old_end = pd.to_datetime(
            row["end_date"]
        ).date()

        if (
            request.start_date <= old_end
            and request.end_date >= old_start
        ):
            return {
                "message": "Overlapping leave request exists"
            }

    # Assign manager
    manager_id = "MGR-001"  # Temporary manager for testing
    # 7. Save request in SQLite
    request_id = str(uuid.uuid4())

    with get_connection() as conn:
        # Check overlapping saved submissions
        saved = conn.execute("""
            SELECT request_id, start_date, end_date
            FROM leave_submissions
            WHERE employee_id = ?
              AND status IN ('PENDING', 'APPROVED')
              AND start_date <= ?
              AND end_date >= ?
        """, (
            request.employee_id,
            request.end_date.isoformat(),
            request.start_date.isoformat()
        )).fetchone()

        if saved:
            return {
                "message": "Overlapping saved leave request exists"
            }

        conn.execute("""
            INSERT INTO leave_submissions (
                request_id,
                employee_id,
                leave_policy_id,
                start_date,
                end_date,
                requested_days,
                status,
                created_at,
                manager_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            request_id,
            request.employee_id,
            request.leave_policy_id,
            request.start_date.isoformat(),
            request.end_date.isoformat(),
            business_days,
            "PENDING",
            datetime.now().isoformat(),
            manager_id
        ))

    # Return must align with "with", not with "conn.execute"
    return {
        "message": "Leave request saved successfully",
        "request_id": request_id,
        "employee_id": request.employee_id,
        "leave_policy_id": request.leave_policy_id,
        "requested_days": business_days,
        "status": "PENDING"
    }

# ---------------------------------------
# 13. VIEW SAVED LEAVE REQUESTS
# ---------------------------------------


# ---------------------------------------
# PENDING LEAVE APPROVALS API
# ---------------------------------------


@app.get("/pending-approvals/{manager_id}")
def get_pending_approvals(manager_id: str):

    with get_connection() as conn:
        rows = conn.execute("""
            SELECT
                request_id,
                employee_id,
                leave_policy_id,
                start_date,
                end_date,
                requested_days,
                status,
                created_at,
                manager_id
            FROM leave_submissions
            WHERE status = 'PENDING'
              AND manager_id = ?
            ORDER BY created_at ASC
        """, (manager_id,)).fetchall()

    pending_requests = [dict(row) for row in rows]

    return {
        "manager_id": manager_id,
        "total_pending": len(pending_requests),
        "pending_approvals": pending_requests
    }



# ---------------------------------------
# MANAGER APPROVAL API
# ---------------------------------------


@app.post("/saved-leave-requests/{request_id}/decision")
def decide_leave_request(
    request_id: str,
    decision: ApprovalDecision
):
    action = decision.decision.strip().upper()

    if action not in ["APPROVED", "REJECTED"]:
        return {
            "message": "Decision must be APPROVED or REJECTED"
        }

    if not decision.manager_id.strip():
        return {"message": "Manager ID is required"}

    decided_time = datetime.now().isoformat()

    with get_connection() as conn:
        # Lock the SQLite write transaction
        conn.execute("BEGIN IMMEDIATE")

        request = conn.execute("""
            SELECT *
            FROM leave_submissions
            WHERE request_id = ?
        """, (request_id,)).fetchone()

        if request is None:
            return {"message": "Leave request not found"}

        if request["status"] != "PENDING":
            return {
                "message": "Request already decided or not pending",
                "current_status": request["status"]
            }

        # Deduct balance only when approving
        if action == "APPROVED":

            year = date.fromisoformat(
                request["start_date"]
            ).year

            balance = conn.execute("""
                SELECT *
                FROM leave_balance
                WHERE employee_id = ?
                  AND leave_policy_id = ?
                  AND period_year = ?
            """, (
                request["employee_id"],
                request["leave_policy_id"],
                year
            )).fetchone()

            if balance is None:
                return {
                    "message": "Leave balance not found"
                }

            days = int(request["requested_days"])
            available = float(balance["available_days"])

            if days > available:
                return {
                    "message": "Insufficient leave balance",
                    "available_days": available,
                    "requested_days": days
                }

            # Deduct leave exactly once, inside transaction
            cursor = conn.execute("""
                UPDATE leave_balance
                SET used_days = used_days + ?,
                    available_days = available_days - ?
                WHERE leave_balance_id = ?
                  AND available_days >= ?
            """, (
                days,
                days,
                balance["leave_balance_id"],
                days
            ))

            if cursor.rowcount != 1:
                return {
                    "message": "Balance update failed"
                }

        # Record final decision
        cursor = conn.execute("""
            UPDATE leave_submissions
            SET status = ?,
                decision_by = ?,
                decision_note = ?,
                decided_at = ?
            WHERE request_id = ?
              AND status = 'PENDING'
        """, (
            action,
            decision.manager_id.strip(),
            decision.comment,
            decided_time,
            request_id
        ))

        if cursor.rowcount != 1:
            # Raising an error rolls back the transaction
            raise RuntimeError("Could not record decision")

        result = conn.execute("""
            SELECT *
            FROM leave_submissions
            WHERE request_id = ?
        """, (request_id,)).fetchone()

        balance_result = None

        if action == "APPROVED":
            balance_result = conn.execute("""
                SELECT available_days, used_days
                FROM leave_balance
                WHERE employee_id = ?
                  AND leave_policy_id = ?
                  AND period_year = ?
            """, (
                request["employee_id"],
                request["leave_policy_id"],
                date.fromisoformat(
                    request["start_date"]
                ).year
            )).fetchone()

        response = {
            "message": "Decision recorded successfully",
            "request": dict(result)
        }

        if balance_result:
            response["updated_balance"] = dict(balance_result)

        return response
