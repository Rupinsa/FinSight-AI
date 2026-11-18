from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from src.financial.reports import profit_and_loss, balance_sheet, budget_vs_actual

ROOT = Path(__file__).resolve().parents[1]
def build_board_pdf():
    (ROOT / "reports").mkdir(exist_ok=True)
    _, pnl = profit_and_loss()
    _, bs = balance_sheet()
    variance = budget_vs_actual()
    path = ROOT / "reports/monthly_board_pack.pdf"
    doc = SimpleDocTemplate(str(path), pagesize=A4)
    styles = getSampleStyleSheet()
    story = [Paragraph("FinSight AI – Monthly Board Pack", styles["Title"]),
             Paragraph("Illustrative synthetic company data | FY2025", styles["Normal"]),
             Spacer(1, 18), Paragraph("Profit & Loss Summary", styles["Heading2"])]
    data = [["Metric", "Amount"]] + [[k.replace("_"," ").title(), f"{v:,.2f}"] for k,v in pnl.items()]
    t = Table(data, hAlign="LEFT")
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#243B53")),
                           ("TEXTCOLOR",(0,0),(-1,0),colors.white),
                           ("GRID",(0,0),(-1,-1),.4,colors.grey),
                           ("PADDING",(0,0),(-1,-1),7)]))
    story += [t, Spacer(1,18), Paragraph("Balance Sheet Summary", styles["Heading2"])]
    bdata = [["Metric","Amount"]] + [[k, f"{v:,.2f}"] for k,v in bs.items()]
    bt = Table(bdata, hAlign="LEFT")
    bt.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#243B53")),
                            ("TEXTCOLOR",(0,0),(-1,0),colors.white),
                            ("GRID",(0,0),(-1,-1),.4,colors.grey),
                            ("PADDING",(0,0),(-1,-1),7)]))
    story += [bt, Spacer(1,18), Paragraph("Budget vs Actual – Department Summary", styles["Heading2"])]
    grouped = variance.groupby("department_name")[["budget_amount","actual_expense","variance"]].sum().reset_index()
    vdata = [["Department","Budget","Actual","Variance"]]
    for _, r in grouped.iterrows():
        vdata.append([r.department_name, f"{r.budget_amount:,.0f}",
                      f"{r.actual_expense:,.0f}", f"{r.variance:,.0f}"])
    vt = Table(vdata, repeatRows=1)
    vt.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#243B53")),
                            ("TEXTCOLOR",(0,0),(-1,0),colors.white),
                            ("GRID",(0,0),(-1,-1),.4,colors.grey),
                            ("PADDING",(0,0),(-1,-1),6)]))
    story.append(vt)
    story.append(Spacer(1,16))
    story.append(Paragraph("Note: Demonstration report only. Validate source data, accounting policy and period close before business use.", styles["Italic"]))
    doc.build(story)
    return path

if __name__ == "__main__":
    print(build_board_pdf())
