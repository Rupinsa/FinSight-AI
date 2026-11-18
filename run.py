import sys
from src.data.generate_data import ROOT
from src.data.generate_data import *
from src.database import load_csv_tables
from src.credit_risk.model import train_model
from src.reports import build_board_pdf
from src.data.export_excel import export_workbook

def main():
    command = sys.argv[1] if len(sys.argv) > 1 else "help"
    if command == "setup":
        # Importing generator creates the reproducible demo data.
        load_csv_tables()
        print("Demo datasets generated and loaded into SQLite.")
    elif command == "train":
        _, metrics = train_model()
        print("ROC-AUC:", round(metrics["roc_auc"], 4))
    elif command == "report":
        print("PDF:", build_board_pdf())
        print("Excel:", export_workbook())
    elif command == "all":
        load_csv_tables()
        _, metrics = train_model()
        print("ROC-AUC:", round(metrics["roc_auc"], 4))
        print("PDF:", build_board_pdf())
        print("Excel:", export_workbook())
    else:
        print("Commands: setup | train | report | all")

if __name__ == "__main__":
    main()
