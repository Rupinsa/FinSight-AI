from pathlib import Path
import json

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from src.database import load_csv_tables, ensure_database
from src.financial.reports import profit_and_loss, balance_sheet, budget_vs_actual
from src.credit_risk.model import train_model, score_customers
from src.reports import build_board_pdf
from src.data.export_excel import export_workbook

ROOT = Path(__file__).resolve().parent
st.set_page_config(
    page_title="FinSight AI | Intelligence Console",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Futuristic visual system ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');

:root {
  --bg: #070B14;
  --panel: rgba(16, 25, 43, .82);
  --panel2: rgba(21, 34, 55, .72);
  --line: rgba(117, 151, 194, .18);
  --text: #EAF2FF;
  --muted: #91A4BF;
  --cyan: #42E8E0;
  --blue: #6B8CFF;
  --violet: #B28CFF;
  --green: #56E3A5;
}
html, body, [data-testid="stAppViewContainer"] {
  background:
    radial-gradient(ellipse at 12% 0%, rgba(42, 102, 180, .18), transparent 34%),
    radial-gradient(ellipse at 88% 10%, rgba(110, 69, 190, .16), transparent 30%),
    linear-gradient(145deg, #070B14 0%, #0A1220 52%, #080D18 100%);
  color: var(--text);
  font-family: 'Manrope', sans-serif;
}
[data-testid="stHeader"] { background: rgba(7,11,20,.55); }
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, rgba(12,20,35,.98), rgba(8,13,24,.98));
  border-right: 1px solid var(--line);
}
[data-testid="stSidebar"] * { color: var(--text); }
.block-container { padding-top: 1.7rem; padding-bottom: 3rem; max-width: 1600px; }
h1,h2,h3,h4 { color: var(--text) !important; letter-spacing: -.035em; }
p, label, .stCaption { color: var(--muted); }
div[data-testid="stMetric"] {
  background: linear-gradient(145deg, rgba(20,34,57,.94), rgba(11,20,35,.94));
  border: 1px solid var(--line);
  border-radius: 18px;
  padding: 18px 20px;
  box-shadow: 0 12px 35px rgba(0,0,0,.18);
  min-height: 118px;
}
div[data-testid="stMetricLabel"] { color: #9FB2CE !important; font-size: .78rem; text-transform: uppercase; letter-spacing: .12em; }
div[data-testid="stMetricValue"] { color: #F3F8FF !important; font-weight: 800; font-size: 1.8rem; }
div[data-testid="stMetricDelta"] { font-family: 'DM Mono', monospace; }
.stButton > button, .stDownloadButton > button {
  background: linear-gradient(100deg, #35D8D0, #6586FF);
  color: #06111D !important;
  border: 0;
  border-radius: 11px;
  font-weight: 800;
  padding: .62rem 1rem;
  box-shadow: 0 7px 24px rgba(65, 180, 220, .18);
}
.stButton > button:hover, .stDownloadButton > button:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 28px rgba(65, 180, 220, .30);
}
div[data-testid="stTabs"] button {
  color: #A9B9D1;
  font-weight: 700;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
  color: var(--cyan) !important;
  border-bottom-color: var(--cyan) !important;
}
[data-testid="stDataFrame"], [data-testid="stTable"] {
  border: 1px solid var(--line);
  border-radius: 14px;
  overflow: hidden;
}
[data-testid="stExpander"] {
  border: 1px solid var(--line);
  border-radius: 14px;
  background: rgba(15,25,42,.62);
}
hr { border-color: var(--line); }
.hero {
  padding: 25px 28px;
  border: 1px solid rgba(100,180,220,.24);
  border-radius: 22px;
  background:
    linear-gradient(110deg, rgba(22,52,78,.88), rgba(24,27,57,.75)),
    radial-gradient(circle at 85% 50%, rgba(66,232,224,.15), transparent 30%);
  box-shadow: 0 18px 55px rgba(0,0,0,.22);
  margin-bottom: 22px;
}
.eyebrow {
  color: #6EECE4; font-family: 'DM Mono', monospace;
  font-size: .72rem; letter-spacing: .19em; text-transform: uppercase;
}
.hero-title { font-size: clamp(2rem, 4vw, 3.15rem); font-weight: 800; letter-spacing: -.06em; margin: 5px 0 4px; color: #F5FAFF; }
.hero-copy { color: #A9BCD5; font-size: .94rem; margin: 0; }
.section-kicker {
  color: #6EECE4; font-family: 'DM Mono', monospace; text-transform: uppercase;
  letter-spacing: .16em; font-size: .7rem; margin-bottom: 5px;
}
.panel {
  background: linear-gradient(145deg, rgba(18,30,49,.88), rgba(10,18,32,.88));
  border: 1px solid var(--line); border-radius: 18px;
  padding: 18px 20px; margin-bottom: 12px;
}
.status-dot {
  display:inline-block; width:8px; height:8px; border-radius:50%;
  background:#56E3A5; box-shadow:0 0 12px #56E3A5; margin-right:8px;
}
.small-muted { color: #91A4BF; font-size: .78rem; }
div[data-baseweb="select"] > div, div[data-baseweb="input"] > div {
  background: #101B2D; border-color: var(--line); border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

PLOT_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Manrope, sans-serif", color="#B9C9DF"),
    margin=dict(l=15, r=15, t=48, b=15),
    legend=dict(orientation="h", y=1.12, x=0),
)

def money(value):
    return f"₹{value:,.0f}"

def panel_title(kicker, title, subtitle=None):
    st.markdown(f'<div class="section-kicker">{kicker}</div><h3 style="margin-top:0">{title}</h3>', unsafe_allow_html=True)
    if subtitle:
        st.caption(subtitle)

def make_donut(series, title):
    fig = px.pie(
        names=series.index.astype(str), values=series.values,
        hole=.72, title=title,
        color_discrete_sequence=["#42E8E0", "#6B8CFF", "#B28CFF", "#F4B860", "#FF7F9D"]
    )
    fig.update_traces(textposition="outside", textinfo="percent+label",
                      marker=dict(line=dict(color="#0B1220", width=3)))
    fig.update_layout(**PLOT_LAYOUT, showlegend=False, height=330)
    return fig

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("""
    <div style="padding:8px 4px 20px">
      <div style="font-family:'DM Mono';letter-spacing:.2em;color:#6EECE4;font-size:.72rem">FINANCIAL INTELLIGENCE</div>
      <div style="font-size:1.65rem;font-weight:800;letter-spacing:-.06em;color:#F1F7FF">◈ FinSight<span style="color:#42E8E0"> AI</span></div>
      <div class="small-muted">EXECUTIVE CONTROL CENTER</div>
    </div>
    """, unsafe_allow_html=True)
    page = st.radio(
        "NAVIGATION",
        ["Command Center", "Financial Statements", "Budget Intelligence", "Credit Risk Lab", "Board Reports"],
        label_visibility="visible",
    )
    st.markdown("---")
    st.markdown('<span class="status-dot"></span><span style="font-size:.8rem">Analytics engine online</span>', unsafe_allow_html=True)
    st.caption("DEMO ENVIRONMENT · FY2025")
    if st.button("↻  Refresh database", use_container_width=True):
        load_csv_tables()
        st.success("Database refreshed.")
        st.rerun()

# Always verify database tables, not merely whether the .db file exists.
# An empty SQLite file can exist without any application tables.
try:
    ensure_database()
except Exception as exc:
    st.error("FinSight AI could not initialize its database.")
    st.exception(exc)
    st.info(
        "Open the project root in VS Code, activate your virtual environment, "
        "and run: python run.py setup"
    )
    st.stop()

pnl_detail, pnl = profit_and_loss()
_, bs = balance_sheet()
variance = budget_vs_actual()
total_assets = bs.get("Total Assets", 0)
total_liabilities_equity = bs.get("Total Liabilities and Equity", 0)
margin = (pnl["net_profit"] / pnl["revenue"] * 100) if pnl["revenue"] else 0
budget_total = variance["budget_amount"].sum()
actual_total = variance["actual_expense"].sum()
favourable = budget_total - actual_total

# ---------- Hero ----------
st.markdown(f"""
<div class="hero">
  <div class="eyebrow">◈ FINANCIAL INTELLIGENCE PLATFORM · FY2025</div>
  <div class="hero-title">{page}</div>
  <p class="hero-copy">A unified view of financial performance, operating variance and portfolio risk.</p>
</div>
""", unsafe_allow_html=True)

# ---------- Command Center ----------
if page == "Command Center":
    panel_title("LIVE SNAPSHOT", "Executive performance overview", "Illustrative synthetic company data · Reporting period: January–December 2025")
    m1,m2,m3,m4 = st.columns(4)
    m1.metric("Total revenue", money(pnl["revenue"]))
    m2.metric("Total expenses", money(pnl["expenses"]))
    m3.metric("Net profit", money(pnl["net_profit"]), f"{margin:.1f}% margin")
    m4.metric("Total assets", money(total_assets))
    st.markdown("")
    left,right = st.columns([1.35,1])
    with left:
        panel_title("PERFORMANCE MIX", "Revenue and expense accounts")
        fig = px.bar(
            pnl_detail, x="account_name", y="signed_balance", color="account_type",
            barmode="group", color_discrete_map={"Revenue":"#42E8E0","Expense":"#B28CFF"}
        )
        fig.update_layout(**PLOT_LAYOUT, height=370, xaxis_title="", yaxis_title="Amount (₹)")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        panel_title("COST STRUCTURE", "Expense composition")
        expense_rows = pnl_detail[pnl_detail.account_type == "Expense"].copy()
        expense_rows["display_amount"] = -expense_rows["signed_balance"]
        if not expense_rows.empty:
            st.plotly_chart(make_donut(expense_rows.set_index("account_name")["display_amount"], "Expense share"), use_container_width=True)
    st.markdown("")
    left,right = st.columns([1,1])
    with left:
        panel_title("BUDGET CONTROL", "Budget vs actual spend")
        grouped = variance.groupby("department_name")[["budget_amount","actual_expense"]].sum().reset_index()
        fig = go.Figure()
        fig.add_bar(x=grouped.department_name, y=grouped.budget_amount, name="Budget", marker_color="#6B8CFF")
        fig.add_bar(x=grouped.department_name, y=grouped.actual_expense, name="Actual", marker_color="#42E8E0")
        fig.update_layout(**PLOT_LAYOUT, barmode="group", height=320, yaxis_title="Amount (₹)")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        panel_title("BALANCE SHEET CHECK", "Accounting equation")
        fig = go.Figure(go.Indicator(
            mode="number+delta", value=total_assets,
            number={"prefix":"₹","valueformat":",.0f"},
            delta={"reference":total_liabilities_equity,"relative":False},
            title={"text":"Assets compared with liabilities + equity"},
            gauge={"shape":"bullet","axis":{"visible":False},"bar":{"color":"#42E8E0"},
                   "bgcolor":"rgba(255,255,255,.08)"}
        ))
        fig.update_layout(**PLOT_LAYOUT, height=320)
        st.plotly_chart(fig, use_container_width=True)
        st.caption(f"Reconciliation difference: {money(total_assets-total_liabilities_equity)}")

# ---------- Financial Statements ----------
elif page == "Financial Statements":
    panel_title("GENERAL LEDGER", "Profit & Loss statement", "Account-level balances from the double-entry ledger.")
    a,b,c = st.columns(3)
    a.metric("Revenue", money(pnl["revenue"]))
    b.metric("Expenses", money(pnl["expenses"]))
    c.metric("Net profit", money(pnl["net_profit"]))
    display_pnl = pnl_detail.copy()
    display_pnl["reported_amount"] = display_pnl.apply(
        lambda r: r.signed_balance if r.account_type == "Revenue" else -r.signed_balance, axis=1
    )
    st.dataframe(display_pnl[["account_name","account_type","reported_amount"]].rename(
        columns={"account_name":"Account","account_type":"Type","reported_amount":"Amount (₹)"}
    ), use_container_width=True, hide_index=True)
    st.markdown("---")
    panel_title("FINANCIAL POSITION", "Balance Sheet summary", "Period-end demonstration view. See metric definitions for assumptions.")
    bs_df = pd.DataFrame([
        ["Total assets", bs.get("Total Assets",0)],
        ["Total liabilities", bs.get("Liability",0)],
        ["Equity including current-period profit", bs.get("Equity",0)],
        ["Liabilities + equity", bs.get("Total Liabilities and Equity",0)],
    ], columns=["Metric","Amount (₹)"])
    st.dataframe(bs_df, use_container_width=True, hide_index=True)
    # ---------- Balance Sheet validation ----------
    difference = total_assets - total_liabilities_equity
    tolerance = 0.01
    ok = abs(difference) <= tolerance

    if ok:
        st.success(
            "Balance Sheet reconciles: Assets = Liabilities + Equity"
        )
    else:
        st.error(
            "Balance Sheet does not reconcile. "
            "Investigate ledger and closing entries."
        )
        st.warning(f"Reconciliation difference: ₹{difference:,.2f}")
    with st.expander("View account-level balance sheet balances"):
        _, bs_detail = balance_sheet()
        st.dataframe(bs_detail, use_container_width=True, hide_index=True)

# ---------- Budget Intelligence ----------
elif page == "Budget Intelligence":
    panel_title("SPEND GOVERNANCE", "Budget vs actual intelligence", "Positive expense variance means spending is below budget (favourable).")
    a,b,c = st.columns(3)
    a.metric("Total budget", money(budget_total))
    b.metric("Actual expenses", money(actual_total))
    c.metric("Favourable variance", money(favourable), f"{(favourable/budget_total*100 if budget_total else 0):.1f}% of budget")
    monthly = variance.groupby("month")[["budget_amount","actual_expense"]].sum().reset_index()
    fig = go.Figure()
    fig.add_scatter(x=monthly.month, y=monthly.budget_amount, name="Budget", mode="lines+markers", line=dict(color="#6B8CFF",width=3))
    fig.add_scatter(x=monthly.month, y=monthly.actual_expense, name="Actual", mode="lines+markers", line=dict(color="#42E8E0",width=3))
    fig.update_layout(**PLOT_LAYOUT, height=370, yaxis_title="Amount (₹)", xaxis_title="Month")
    st.plotly_chart(fig, use_container_width=True)
    dept = variance.groupby("department_name")[["budget_amount","actual_expense","variance"]].sum().reset_index()
    fig = px.bar(dept, x="department_name", y="variance", color="variance",
                 color_continuous_scale=["#FF7F9D","#F4B860","#42E8E0"],
                 title="Favourable / unfavourable variance by department")
    fig.update_layout(**PLOT_LAYOUT, height=340, xaxis_title="", yaxis_title="Budget - actual (₹)")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(variance, use_container_width=True, hide_index=True)
    st.download_button("Download variance CSV", variance.to_csv(index=False).encode(), "budget_variance.csv", "text/csv")

# ---------- Credit Risk Lab ----------
elif page == "Credit Risk Lab":
    panel_title("PORTFOLIO MONITORING", "Credit risk intelligence lab", "Demonstration model trained on synthetic loan outcomes. Not for real lending decisions.")
    model_path = ROOT / "models/credit_risk_model.joblib"
    if st.button("Train / retrain model"):
        with st.spinner("Training logistic regression model..."):
            _, metrics = train_model()
        st.success(f"Model trained · ROC-AUC {metrics['roc_auc']:.3f}")
    if model_path.exists():
        from src.credit_risk.model import FEATURES
        loans = pd.read_csv(ROOT / "data/raw/loans_synthetic.csv")
        scored = score_customers(loans[FEATURES].head(500))
        metrics_file = ROOT / "reports/model_metrics.json"
        metrics = json.loads(metrics_file.read_text()) if metrics_file.exists() else {}
        a,b,c,d = st.columns(4)
        a.metric("Loans scored", f"{len(scored):,}")
        b.metric("Average PD", f"{scored.default_probability.mean()*100:.1f}%")
        c.metric("ROC-AUC", f"{metrics.get('roc_auc',0):.3f}")
        d.metric("High-risk share", f"{(scored.risk_band=='High').mean()*100:.1f}%")
        left,right = st.columns([1,1])
        with left:
            counts = scored.risk_band.value_counts().reindex(["Low","Medium","High"]).fillna(0)
            st.plotly_chart(make_donut(counts, "Risk band distribution"), use_container_width=True)
        with right:
            fig = px.histogram(scored, x="default_probability", nbins=28,
                               color_discrete_sequence=["#42E8E0"], title="Predicted default probability")
            fig.update_layout(**PLOT_LAYOUT, height=330, xaxis_title="Probability of default", yaxis_title="Loan count")
            st.plotly_chart(fig, use_container_width=True)
        st.dataframe(scored.head(100), use_container_width=True, hide_index=True)
        st.download_button("Download scored loans", scored.to_csv(index=False).encode(), "credit_risk_scores.csv", "text/csv")
        woe_path = ROOT / "reports/woe_iv_analysis.csv"
        if woe_path.exists():
            with st.expander("Weight of Evidence / Information Value diagnostics"):
                st.dataframe(pd.read_csv(woe_path), use_container_width=True, hide_index=True)
        with st.expander("Model evaluation details"):
            st.json(metrics)
    else:
        st.info("No trained model found. Select **Train / retrain model** to begin.")

# ---------- Board Reports ----------
elif page == "Board Reports":
    panel_title("REPORTING OPERATIONS", "Monthly board pack", "Generate downloadable finance reports for review.")
    st.markdown('<div class="panel"><span class="eyebrow">REPORTING PERIOD</span><h3 style="margin:6px 0">FY2025 · Demonstration close</h3><span class="small-muted">Synthetic data · Illustrative currency in INR</span></div>', unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1:
        st.markdown("#### Financial workbook")
        st.caption("P&L summary and detail, Balance Sheet, budget vs actual.")
        if st.button("Generate Excel workbook", use_container_width=True):
            path = export_workbook()
            st.download_button("⬇ Download Excel workbook", path.read_bytes(), path.name,
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                               use_container_width=True)
    with c2:
        st.markdown("#### PDF board pack")
        st.caption("Executive summary, financial position and department variance.")
        if st.button("Generate PDF board pack", use_container_width=True):
            path = build_board_pdf()
            st.download_button("⬇ Download PDF board pack", path.read_bytes(), path.name,
                               mime="application/pdf", use_container_width=True)
    st.markdown("---")
    st.markdown("#### Key reporting controls")
    checks = [
        ("Ledger journal balance", "All journal entries should have equal debit and credit totals."),
        ("Balance Sheet reconciliation", f"Difference currently {money(total_assets-total_liabilities_equity)}."),
        ("Metric definitions", "Review docs/metric_definitions.md before distributing reports."),
        ("Data provenance", "Synthetic demo data; replace and reconcile before business use."),
    ]
    for label, desc in checks:
        st.markdown(f'<div class="panel"><b>{label}</b><br><span class="small-muted">{desc}</span></div>', unsafe_allow_html=True)

st.markdown("---")
st.markdown('<div style="display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;color:#7186A3;font-family:DM Mono;font-size:.68rem;letter-spacing:.08em"><span>FINSIGHT AI · FINANCIAL INTELLIGENCE</span><span>DEMO BUILD 2.0 · DATA IS SYNTHETIC</span></div>', unsafe_allow_html=True)
