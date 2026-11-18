from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(42)

accounts = pd.DataFrame([
    (1000, "Cash", "Asset"), (1100, "Accounts Receivable", "Asset"),
    (1200, "Inventory", "Asset"), (1500, "Equipment", "Asset"),
    (2000, "Accounts Payable", "Liability"), (2100, "Bank Loan", "Liability"),
    (3000, "Share Capital", "Equity"), (3100, "Retained Earnings", "Equity"),
    (4000, "Product Revenue", "Revenue"), (4100, "Service Revenue", "Revenue"),
    (5000, "Cost of Goods Sold", "Expense"), (5100, "Salary Expense", "Expense"),
    (5200, "Marketing Expense", "Expense"), (5300, "Rent Expense", "Expense"),
    (5400, "Utilities Expense", "Expense"), (5500, "Depreciation Expense", "Expense"),
], columns=["account_id", "account_name", "account_type"])
accounts.to_csv(RAW / "accounts.csv", index=False)

departments = pd.DataFrame([
    (1, "Sales"), (2, "Marketing"), (3, "Operations"), (4, "Finance")
], columns=["department_id", "department_name"])
departments.to_csv(RAW / "departments.csv", index=False)

rows, jid = [], 1
def post(date, debit_acct, credit_acct, amount, dept, desc):
    global jid
    amount = round(float(amount), 2)
    rows.append((jid, date, debit_acct, amount, 0.0, dept, desc))
    rows.append((jid, date, credit_acct, 0.0, amount, dept, desc))
    jid += 1

# Opening balances: assets 250k = liabilities 80k + equity 170k
post("2025-01-01", 1000, 3000, 170000, 4, "Opening cash capital")
post("2025-01-01", 1200, 3000, 40000, 4, "Opening inventory capital")
post("2025-01-01", 1000, 2100, 80000, 4, "Opening bank loan")
# monthly operations and expenses
for month in range(1, 13):
    date = pd.Timestamp(2025, month, 15).strftime("%Y-%m-%d")
    dept = 1
    revenue = rng.uniform(65000, 105000)
    cogs = revenue * rng.uniform(.35, .48)
    salaries = rng.uniform(15000, 23000)
    marketing = rng.uniform(5000, 12000)
    rent = 6000
    utilities = rng.uniform(1000, 2500)
    # Cash sales and corresponding COGS/inventory movements
    post(date, 1000, 4000, revenue * .7, dept, "Product sales - cash")
    post(date, 1100, 4100, revenue * .3, dept, "Service sales - receivable")
    post(date, 1200, 2000, cogs * 1.25, 3, "Inventory purchases on credit")
    post(date, 5000, 1200, cogs, 3, "Cost of goods sold")
    post(date, 5100, 1000, salaries, 3, "Payroll")
    post(date, 5200, 1000, marketing, 2, "Marketing campaign")
    post(date, 5300, 1000, rent, 3, "Office rent")
    post(date, 5400, 1000, utilities, 3, "Utilities")
    # Collect part of receivables and pay down payables
    post(date, 1000, 1100, revenue * .15, 1, "Receivable collection")
    post(date, 2000, 1000, cogs * .15, 3, "Supplier payment")
    # Equipment purchase, balanced
    if month in (1, 7):
        post(date, 1500, 1000, 12000, 4, "Equipment purchase")

ledger = pd.DataFrame(rows, columns=[
    "journal_id", "transaction_date", "account_id", "debit", "credit",
    "department_id", "description"
])
ledger.to_csv(RAW / "financial_ledger.csv", index=False)

budget_rows = []
for month in range(1, 13):
    for dept_id, base in [(1, 90000), (2, 9000), (3, 30000), (4, 7000)]:
        budget_rows.append((f"2025-{month:02d}", dept_id,
                            round(base * rng.uniform(.92, 1.08), 2)))
pd.DataFrame(budget_rows, columns=["month", "department_id", "budget_amount"]).to_csv(
    RAW / "budget.csv", index=False
)

# Synthetic lending data for a reproducible demo; replace with public LendingClub data later.
n = 5000
income = rng.lognormal(11.0, .55, n).clip(18000, 250000)
loan = rng.uniform(1000, 35000, n)
dti = rng.uniform(0, 45, n)
int_rate = rng.uniform(5, 30, n)
emp = rng.integers(0, 11, n)
logit = -3.2 + .055*dti + .075*int_rate + .000025*loan - .000008*income - .06*emp
prob = 1 / (1 + np.exp(-logit))
default = rng.binomial(1, prob)
loans = pd.DataFrame({
    "loan_id": np.arange(1, n+1),
    "loan_amnt": loan.round(2),
    "annual_inc": income.round(2),
    "dti": dti.round(2),
    "int_rate": int_rate.round(2),
    "emp_length": emp,
    "default": default
})
loans.to_csv(RAW / "loans_synthetic.csv", index=False)
print(f"Generated {len(ledger)} ledger lines, {len(budget_rows)} budgets, {len(loans)} loans.")
