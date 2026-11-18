import pandas as pd
from src.database import read_query

def profit_and_loss():
    sql = """
    SELECT a.account_name, a.account_type,
           SUM(l.credit - l.debit) AS signed_balance
    FROM financial_ledger l
    JOIN accounts a USING(account_id)
    WHERE a.account_type IN ('Revenue','Expense')
    GROUP BY a.account_id, a.account_name, a.account_type
    ORDER BY a.account_type, a.account_name
    """
    df = read_query(sql)
    revenue = df.loc[df.account_type == "Revenue", "signed_balance"].sum()
    expenses = -df.loc[df.account_type == "Expense", "signed_balance"].sum()
    return df, {"revenue": revenue, "expenses": expenses, "net_profit": revenue-expenses}

def balance_sheet(as_of="2025-12-31"):
    sql = """
    SELECT a.account_name, a.account_type,
           SUM(l.debit - l.credit) AS debit_balance
    FROM financial_ledger l
    JOIN accounts a USING(account_id)
    WHERE l.transaction_date <= ?
      AND a.account_type IN ('Asset','Liability','Equity')
    GROUP BY a.account_id, a.account_name, a.account_type
    """
    df = read_query(sql, (as_of,))
    # Convert credit-nature balances to positive presentation.
    df["balance"] = df.apply(
        lambda r: r.debit_balance if r.account_type == "Asset" else -r.debit_balance,
        axis=1
    )
    totals = df.groupby("account_type")["balance"].sum().to_dict()
    # Net income is included in equity for a simple period-end presentation.
    _, pnl = profit_and_loss()
    totals["Equity"] = totals.get("Equity", 0) + pnl["net_profit"]
    totals["Total Liabilities and Equity"] = totals.get("Liability", 0) + totals["Equity"]
    totals["Total Assets"] = totals.get("Asset", 0)
    return df, totals

def budget_vs_actual():
    sql = """
    SELECT b.month, d.department_name, b.budget_amount,
           COALESCE(SUM(CASE WHEN a.account_type='Expense'
               THEN l.debit-l.credit ELSE 0 END),0) AS actual_expense
    FROM budget b
    JOIN departments d USING(department_id)
    LEFT JOIN financial_ledger l
      ON l.department_id=b.department_id
      AND substr(l.transaction_date,1,7)=b.month
    LEFT JOIN accounts a USING(account_id)
    GROUP BY b.month, d.department_name, b.budget_amount
    ORDER BY b.month, d.department_name
    """
    df = read_query(sql)
    df["variance"] = df["budget_amount"] - df["actual_expense"]
    df["variance_pct"] = (df["variance"] / df["budget_amount"].replace(0, pd.NA))*100
    return df
