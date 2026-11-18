from pathlib import Path
import sqlite3
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "finsight.db"

REQUIRED_TABLES = {
    "accounts",
    "departments",
    "financial_ledger",
    "budget",
    "loans_synthetic",
}


def get_connection():
    DB.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB)


def existing_tables():
    if not DB.exists():
        return set()

    with get_connection() as conn:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()

    return {row[0] for row in rows}


def load_csv_tables():
    raw = ROOT / "data" / "raw"

    required_files = [
        "accounts.csv",
        "departments.csv",
        "financial_ledger.csv",
        "budget.csv",
        "loans_synthetic.csv",
    ]

    missing = [
        name for name in required_files
        if not (raw / name).exists()
    ]

    if missing:
        raise FileNotFoundError(
            f"Missing CSV files in {raw}: {', '.join(missing)}. "
            "Run python run.py setup from the project root."
        )

    with get_connection() as conn:
        for name in [
            "accounts",
            "departments",
            "financial_ledger",
            "budget",
            "loans_synthetic",
        ]:
            df = pd.read_csv(raw / f"{name}.csv")
            df.to_sql(name, conn, if_exists="replace", index=False)

    return DB


def ensure_database():
    """Initialize the database if required tables are missing."""
    tables = existing_tables()

    if not REQUIRED_TABLES.issubset(tables):
        load_csv_tables()
        tables = existing_tables()

    missing = REQUIRED_TABLES - tables

    if missing:
        raise RuntimeError(
            "Database initialization failed. Missing tables: "
            + ", ".join(sorted(missing))
        )

    return DB


def read_query(sql, params=None):
    ensure_database()

    with get_connection() as conn:
        return pd.read_sql_query(sql, conn, params=params or ())
