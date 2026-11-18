
from pathlib import Path

import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.utils import get_column_letter

from src.financial.reports import (
    profit_and_loss,
    balance_sheet,
    budget_vs_actual,
)


ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = ROOT / "reports"
OUTPUT_FILE = REPORTS_DIR / "financial_report.xlsx"


# ==========================================
# EXCEL FORMATTING
# ==========================================

def format_workbook(path):
    """Apply consistent professional formatting to every worksheet."""

    workbook = load_workbook(path)

    header_fill = PatternFill(
        fill_type="solid",
        fgColor="203B56"
    )

    header_font = Font(
        name="Arial",
        bold=True,
        color="FFFFFF",
        size=11
    )

    title_font = Font(
        name="Arial",
        bold=True,
        color="FFFFFF",
        size=14
    )

    thin_border = Border(
        bottom=Side(style="thin", color="D9E2F3")
    )

    currency_format = '#,##0.00;[Red](#,##0.00);-'
    percentage_format = '0.00%;[Red](0.00%);-'

    for worksheet in workbook.worksheets:

        worksheet.freeze_panes = "A2"
        worksheet.sheet_view.showGridLines = False

        # Format header row
        for cell in worksheet[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(
                horizontal="center",
                vertical="center"
            )

        worksheet.row_dimensions[1].height = 25

        # Format data rows and numeric values
        for row in worksheet.iter_rows(min_row=2):

            for cell in row:
                cell.border = thin_border
                cell.alignment = Alignment(
                    vertical="center"
                )

                if isinstance(cell.value, (int, float)):
                    cell.number_format = currency_format

        # Adjust column widths based on contents
        for column_cells in worksheet.columns:

            column_letter = get_column_letter(
                column_cells[0].column
            )

            max_length = 0

            for cell in column_cells:
                if cell.value is not None:
                    max_length = max(
                        max_length,
                        len(str(cell.value))
                    )

            worksheet.column_dimensions[
                column_letter
            ].width = min(max(max_length + 4, 15), 40)

        # Apply percentage formatting to percentage columns
        for column_cells in worksheet.columns:

            heading = str(column_cells[0].value or "").lower()

            if "percent" in heading or "variance %" in heading:
                for cell in column_cells[1:]:
                    cell.number_format = percentage_format

        # Enable filters
        if worksheet.max_row >= 1 and worksheet.max_column >= 1:
            worksheet.auto_filter.ref = worksheet.dimensions

    # Set workbook properties
    workbook.properties.title = "FinSight AI Financial Report"
    workbook.properties.subject = (
        "Financial Statements and Budget Intelligence"
    )
    workbook.properties.creator = "FinSight AI"

    workbook.save(path)


# ==========================================
# SUMMARY DATA PREPARATION
# ==========================================

def create_pnl_summary(pnl):
    """Create a clean Profit & Loss summary."""

    return pd.DataFrame([
        ["Revenue", pnl.get("revenue", 0)],
        ["Expenses", pnl.get("expenses", 0)],
        ["Net Profit", pnl.get("net_profit", 0)],
    ], columns=["Metric", "Amount (INR)"])


def create_balance_sheet_summary(bs):
    """Create a clean Balance Sheet summary."""

    return pd.DataFrame([
        ["Total Assets", bs.get("Total Assets", 0)],
        ["Total Liabilities", bs.get("Liability", 0)],
        ["Equity", bs.get("Equity", 0)],
        [
            "Total Liabilities and Equity",
            bs.get("Total Liabilities and Equity", 0)
        ],
    ], columns=["Metric", "Amount (INR)"])


# ==========================================
# BUDGET SUMMARY
# ==========================================

def create_budget_summary(variance):
    """
    Create department-level budget summary.

    Positive variance means spending is below budget.
    Negative variance means spending is above budget.
    """

    if variance.empty:
        return pd.DataFrame(columns=[
            "Department",
            "Budget",
            "Actual",
            "Variance",
            "Variance %",
        ])

    if "department_name" not in variance.columns:
        return variance.copy()

    summary = (
        variance.groupby("department_name", as_index=False)[
            ["budget_amount", "actual_expense"]
        ]
        .sum()
    )

    summary["variance"] = (
        summary["budget_amount"] - summary["actual_expense"]
    )

    summary["variance_pct"] = (
        summary["variance"]
        .div(summary["budget_amount"].replace(0, pd.NA))
        .fillna(0)
    )

    summary = summary.rename(columns={
        "department_name": "Department",
        "budget_amount": "Budget (INR)",
        "actual_expense": "Actual (INR)",
        "variance": "Variance (INR)",
        "variance_pct": "Variance %",
    })

    return summary


# ==========================================
# MAIN EXCEL EXPORT FUNCTION
# ==========================================

def export_workbook():

    # Create reports directory if it does not exist
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    # Fetch financial data
    pnl_detail, pnl = profit_and_loss()

    bs_detail, bs = balance_sheet()

    variance = budget_vs_actual()

    # Prepare summary worksheets
    pnl_summary = create_pnl_summary(pnl)

    bs_summary = create_balance_sheet_summary(bs)

    budget_summary = create_budget_summary(variance)

    # Export all worksheets
    with pd.ExcelWriter(
        OUTPUT_FILE,
        engine="openpyxl"
    ) as writer:

        pnl_summary.to_excel(
            writer,
            sheet_name="P&L Summary",
            index=False
        )

        pnl_detail.to_excel(
            writer,
            sheet_name="P&L Detail",
            index=False
        )

        bs_summary.to_excel(
            writer,
            sheet_name="Balance Sheet",
            index=False
        )

        bs_detail.to_excel(
            writer,
            sheet_name="BS Detail",
            index=False
        )

        budget_summary.to_excel(
            writer,
            sheet_name="Budget vs Actual",
            index=False
        )

        variance.to_excel(
            writer,
            sheet_name="Budget Detail",
            index=False
        )

    # Apply formatting
    format_workbook(OUTPUT_FILE)

    return OUTPUT_FILE


# ==========================================
# RUN DIRECTLY
# ==========================================

if __name__ == "__main__":

    try:
        generated_file = export_workbook()

        print("\nExcel report generated successfully!")
        print(f"File location: {generated_file}")

    except Exception as error:

        print("\nExcel report generation failed.")
        print(f"Error: {error}")

        raise
