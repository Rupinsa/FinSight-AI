from src.data.generate_data import ROOT
from src.database import load_csv_tables, read_query
from src.financial.reports import profit_and_loss, balance_sheet

def test_journals_balance():
    load_csv_tables()
    df = read_query("""
      SELECT journal_id, SUM(debit) d, SUM(credit) c
      FROM financial_ledger GROUP BY journal_id
    """)
    assert ((df.d - df.c).abs() < .01).all()

def test_profit_loss_components():
    load_csv_tables()
    _, pnl = profit_and_loss()
    assert pnl["revenue"] > 0
    assert pnl["expenses"] > 0

def test_balance_sheet_equation():
    load_csv_tables()
    _, bs = balance_sheet()
    assert abs(bs["Total Assets"] - bs["Total Liabilities and Equity"]) < 1.0
