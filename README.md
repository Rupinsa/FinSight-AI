# FinSight AI
Automated Financial Reporting & Credit Risk Intelligence

A portfolio-grade demonstration combining synthetic company accounting data, SQL, Python, a credit-risk model, Excel exports, a Streamlit dashboard, and a documented Qlik Sense / Power Automate integration path.

> This is a demo project. Synthetic data and model outputs are not suitable for real financial statements, lending decisions, or regulatory reporting without professional validation.

## Features
- Generates balanced synthetic double-entry financial ledger data.
- Loads CSV data into SQLite.
- Calculates P&L, a simplified balance sheet, and expense budget variance.
- Trains a logistic regression credit-risk classifier and produces training-sample WoE / IV diagnostics.
- Produces customer risk probabilities, bands, and scores.
- Exports Excel workbook and PDF board pack.
- Provides a Streamlit dashboard.
- Includes Qlik Sense load-script template and Power Automate workflow instructions.

## Requirements
- macOS, Python 3.11–3.12 recommended
- VS Code
- Internet connection for package installation
- Optional: Qlik Cloud account and Microsoft 365 / Power Automate access

## Setup on Mac
```bash
git clone YOUR_REPOSITORY_URL
cd FinSight-AI
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Generate data, load database, and train
```bash
python run.py setup
python run.py train
python run.py report
```


## Live Application

**FinSight AI Dashboard:**  
https://finsight-ai-9.streamlit.app/

The application is deployed using Streamlit Community Cloud.

Explore the five modules:
- Command Center
- Financial Statements
- Budget Intelligence
- Credit Risk Lab
- Board Reports


## Launch dashboard
```bash
streamlit run app.py
```
Open the local URL shown by Streamlit, usually http://localhost:8501.

## Run tests
```bash
pytest -q
```

## Data sources
The project generates synthetic financial and loan datasets for immediate reproducibility. To use LendingClub:
1. Download an appropriate public LendingClub CSV from Kaggle.
2. Put it in `data/raw/`.
3. Inspect its column names and target status definitions.
4. Create a version-specific preprocessing script mapping verified columns to `loan_amnt`, `annual_inc`, `dti`, `int_rate`, `emp_length`, and a resolved binary default target.
5. Never treat current or unresolved loans as non-defaults.

## Reporting logic
See `docs/metric_definitions.md` and `docs/data_dictionary.md`. The current balance sheet is a simplified illustrative presentation. A production system needs opening balances, period close entries, tax, depreciation, receivable/payable settlements, retained earnings roll-forward, and accounting-policy review.

## Credit risk / WoE
`python run.py train` saves `reports/woe_iv_analysis.csv` with feature bins, Weight of Evidence, and Information Value components. WoE is an explanatory diagnostic in this starter; the fitted baseline classifier uses scaled raw features. A production scorecard should validate binning, monotonicity, calibration, stability, fairness, and cutoffs before use.\n\n## Excel\nRun `python run.py report` and open `reports/financial_report.xlsx` in Excel. The workbook contains P&L summary/detail, balance-sheet summary/detail, and budget-vs-actual sheets. Power Pivot authoring is not included in the Mac workflow; full Power Pivot features require supported Windows Excel.

## Qlik Sense
1. Upload the CSV files to a Qlik-accessible data connection.
2. Create a connection named `FinSightData` or adjust the `lib://` paths in `qlik/FinSight_Load_Script.qvs`.
3. Load the script and build KPI objects, trend charts, department variance charts, and risk-band charts.
4. See `qlik/FinSight_Load_Script.qvs`.

## Power Automate
See `power_automate/README.md`. A cloud flow requires a hosted reporting job or a supported gateway/desktop flow; a Mac-local script cannot be run directly by a cloud recurrence trigger.

## Suggested dashboard pages
1. Executive overview: revenue, expenses, net profit, assets, liabilities.
2. Budget performance: department budget, actual expense, favourable variance.
3. Credit risk: predicted default probabilities, risk bands, ROC-AUC and confusion matrix.
4. Board pack: PDF and Excel exports.

## Repository structure
```text
FinSight-AI/
├── app.py
├── run.py
├── requirements.txt
├── data/raw/
├── src/data/
├── src/financial/
├── src/credit_risk/
├── sql/
├── qlik/
├── power_automate/
├── docs/
├── tests/
└── reports/
```

## Limitations and responsible use
- Synthetic loan labels are generated from a known formula and do not demonstrate real-world predictive performance.
- Risk cutoffs are illustrative and require validation, calibration, fairness review, and business approval.
- Financial reports are educational outputs, not audited statements.
- Do not upload sensitive customer data to public repositories.


## Futuristic dashboard theme
The Streamlit dashboard uses a dark navy glass-style theme, cyan/blue/violet accents, Plotly charts, sidebar navigation, executive KPI cards, and separate command-center, financial-statement, budget, credit-risk, and board-report pages. Install the updated requirements and restart Streamlit after replacing app.py.
