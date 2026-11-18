# Data dictionary

## financial_ledger.csv
- journal_id: journal entry identifier
- transaction_date: ISO date YYYY-MM-DD
- account_id: chart-of-accounts key
- debit / credit: non-negative transaction amount; one side per row
- department_id: department key
- description: transaction description

## accounts.csv
- account_id: unique account key
- account_name: readable account label
- account_type: Asset, Liability, Equity, Revenue, Expense

## budget.csv
- month: YYYY-MM period
- department_id: department key
- budget_amount: monthly expense budget in illustrative currency units

## loans_synthetic.csv
- loan_id: synthetic loan identifier
- loan_amnt: requested loan amount
- annual_inc: annual income
- dti: debt-to-income ratio in percent
- int_rate: annual interest rate in percent
- emp_length: employment length in years (synthetic)
- default: synthetic binary target (1 default, 0 non-default)

Synthetic loan data is for software demonstration only and must not be represented as real customer or LendingClub data.
