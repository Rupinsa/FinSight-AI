-- SQLite tables are created from CSVs by src/database.py.
-- Reference schema for a production SQL implementation.
CREATE TABLE accounts (
  account_id INTEGER PRIMARY KEY,
  account_name TEXT NOT NULL,
  account_type TEXT NOT NULL CHECK(account_type IN
    ('Asset','Liability','Equity','Revenue','Expense'))
);
CREATE TABLE departments (
  department_id INTEGER PRIMARY KEY,
  department_name TEXT NOT NULL
);
CREATE TABLE financial_ledger (
  journal_id INTEGER NOT NULL,
  transaction_date TEXT NOT NULL,
  account_id INTEGER NOT NULL REFERENCES accounts(account_id),
  debit REAL NOT NULL DEFAULT 0,
  credit REAL NOT NULL DEFAULT 0,
  department_id INTEGER REFERENCES departments(department_id),
  description TEXT,
  CHECK(debit >= 0 AND credit >= 0),
  CHECK(NOT (debit > 0 AND credit > 0))
);
CREATE TABLE budget (
  month TEXT NOT NULL,
  department_id INTEGER REFERENCES departments(department_id),
  budget_amount REAL NOT NULL
);
