-- Trial balance: every journal must balance across all lines.
SELECT journal_id, ROUND(SUM(debit),2) AS debits,
       ROUND(SUM(credit),2) AS credits,
       ROUND(SUM(debit-credit),2) AS difference
FROM financial_ledger GROUP BY journal_id;

-- P&L by account.
SELECT a.account_name, a.account_type,
       SUM(l.credit-l.debit) AS signed_balance
FROM financial_ledger l JOIN accounts a USING(account_id)
WHERE a.account_type IN ('Revenue','Expense')
GROUP BY a.account_id, a.account_name, a.account_type;

-- Expense budget vs actual by month and department.
SELECT b.month, d.department_name, b.budget_amount,
       SUM(CASE WHEN a.account_type='Expense' THEN l.debit-l.credit ELSE 0 END) AS actual_expense,
       b.budget_amount -
       SUM(CASE WHEN a.account_type='Expense' THEN l.debit-l.credit ELSE 0 END) AS favourable_variance
FROM budget b
JOIN departments d USING(department_id)
LEFT JOIN financial_ledger l
  ON l.department_id=b.department_id
 AND substr(l.transaction_date,1,7)=b.month
LEFT JOIN accounts a USING(account_id)
GROUP BY b.month,d.department_name,b.budget_amount;
