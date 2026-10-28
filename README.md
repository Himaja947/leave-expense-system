# Leave & Expense Management System

## 1. About the Project

This is a Leave and Expense Management API built with **Python** and
**FastAPI**.

Employees can submit leave requests and expense claims. Managers can
approve or reject requests. The project uses **SQLite** to save data.

### Data Source
This project can use synthetic sample data for employees, leave requests, expense claims, and approval workflows.

No external dataset is required for the basic working of this project.

### Data Privacy
- Use sample or synthetic employee details for testing.
- Do not use confidential or personal employee information.
- Do not collect data without permission.
- Do not bypass access controls.

### External Data
If any external dataset is used, record:
- Source URL
- Dataset name and version
- Retrieval date
- License or usage terms
- Required attribution
- Data transformations
- Fields removed or discarded

Use only datasets that are legally permitted for the intended use and redistribution. If the license or suitability is unclear, use synthetic data instead.

Public reference data may be used only for schema inspiration when appropriate.


## 2. Main Features

### Leave Management

-   Submit a leave request.
-   Check leave balance.
-   View leave request data.
-   View saved leave requests.
-   Approve or reject a leave request.
-   Save the manager ID, decision note, and decision time.
-   Update leave balance after leave approval.
-   Stop a request from being decided more than once.

### Expense Management

-   Submit an expense claim.
-   View expense claim data.
-   View saved expense claims.
-   Approve or reject an expense claim.
-   Save the manager ID, decision note, and decision time.
-   Stop a claim from being decided more than once.

## 3. Technologies Used

-   **Python** -- programming language
-   **FastAPI** -- builds the API
-   **SQLite** -- stores data
-   **Pandas** -- works with data files
-   **Uvicorn** -- runs the API
-   **Swagger UI** -- tests the API

## 4. Project Folder Structure

The folders and files below are based on the project view. Some folders
may contain more files.

``` text
leave-expense-system/
├── app/
│   ├── __pycache__/
│   ├── api/
│   ├── models/
│   ├── rules/
│   ├── schemas/
│   ├── services/
│   ├── database.py
│   └── main.py
├── data/
│   ├── ground_truth/
│   ├── input/
│   └── output/
├── scripts/
├── tests/
├── venv/
├── .env
├── check_balance.py
├── check_manager.py
├── check_pending.py
├── check_tables.py
├── import_balance.py
├── leave_expense.db
├── README.md
├── requirements.txt
└── test_dataset.py
```

## 5. How to Run the Project

1.  Open the project folder in VS Code.

2.  Open the terminal in VS Code.

3.  Activate the virtual environment:

    ``` powershell
    .\venv\Scripts\Activate.ps1
    ```

    If the terminal already shows `(venv)`, skip this step.

4.  Install the required packages:

    ``` powershell
    pip install -r requirements.txt
    ```

5.  Start the API:

    ``` powershell
    uvicorn app.main:app --reload
    ```

6.  Open these links in your browser:

    -   Home page: http://127.0.0.1:8000/
    -   API testing page: http://127.0.0.1:8000/docs

## 6. Main API Endpoints

  -----------------------------------------------------------------------------------------------
  Method                  Endpoint                                        Purpose
  ----------------------- ----------------------------------------------- -----------------------
  GET                     `/`                                             Check the home page

  GET                     `/health`                                       Check if the API is
                                                                          working

  GET                     `/employees`                                    View employee details

  GET                     `/leave-requests`                               View leave request data

  POST                    `/leave-requests`                               Submit a leave request

  GET                     `/saved-leave-requests`                         View saved leave
                                                                          requests

  POST                    `/saved-leave-requests/{request_id}/decision`   Approve or reject leave

  GET                     `/pending-approvals`                            View pending leave
                                                                          requests

  GET                     `/pending-approvals/{manager_id}`               View pending leave
                                                                          requests for a manager

  GET                     `/leave-balance/{employee_id}`                  Check leave balance

  GET                     `/expense-claims`                               View expense claim data

  POST                    `/expense-claims`                               Submit an expense claim

  GET                     `/saved-expense-claims`                         View saved expense
                                                                          claims

  POST                    `/saved-expense-claims/{claim_id}/decision`     Approve or reject an
                                                                          expense claim
  -----------------------------------------------------------------------------------------------

## 7. Example: Submit an Expense Claim

Use `POST /expense-claims` with this example:

``` json
{
  "employee_id": "EMP-000161",
  "submitted_date": "2026-10-28",
  "country": "IN",
  "cost_center_id": "CC-ENG",
  "expense_policy_id": "EXPP-001",
  "total_amount": 500,
  "currency": "INR"
}
```

If the request is accepted, the API returns an expense claim ID and its
status.

## 8. Example: Approve or Reject an Expense Claim

Use `POST /saved-expense-claims/{claim_id}/decision`.

Replace `{claim_id}` with the ID returned after submitting the claim.

``` json
{
  "decision": "APPROVED",
  "manager_id": "MGR-001",
  "comment": "Approved for project testing"
}
```

To reject a claim, use `"REJECTED"` as the decision.

## 9. Example: Approve or Reject a Leave Request

Use `POST /saved-leave-requests/{request_id}/decision`.

Replace `{request_id}` with the ID returned after submitting the leave
request.

``` json
{
  "decision": "APPROVED",
  "manager_id": "MGR-001",
  "comment": "Approved for project testing"
}
```

## 10. Basic Workflow

1.  An employee submits a leave request or expense claim.
2.  The system checks the request and saves it.
3.  The request starts with **PENDING** status.
4.  A manager approves or rejects it.
5.  The system saves the decision details.
6.  If leave is approved, the system updates the leave balance.

## 11. Important Notes

-   This is a project/demo version.
-   New leave requests currently use `MGR-001` as a temporary manager
    for testing.
-   A manager ID is not proof of identity. A real system needs login and
    access checks.
-   Expense approval saves the decision. It does not mean the money has
    been paid.
-   Back up `leave_expense.db` before major changes.
-   Use test data while testing approval and rejection.

## 12. What I Learned

-   Building APIs with FastAPI.
-   Saving and reading data with SQLite.
-   Checking user input.
-   Building approval and rejection steps.
-   Preventing duplicate decisions.
-   Testing APIs using Swagger UI.