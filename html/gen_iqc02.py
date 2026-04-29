"""
Generate 14 individual IQC-02 HTML forms (one per unique GRN Doc.No.)
Run: python gen_iqc02.py
Output: IQC02_001.html … IQC02_014.html in the same directory
"""
import os, textwrap

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# Source data  (serial, date, doc_no, lines[(mat_code, description, qty, uom, batch)])
# ---------------------------------------------------------------------------
RECORDS = [
    ("001", "06-Aug-25", "2425603614", [
        ("2966563", "CAN-M_TIN-PLT @AP Trugrip 1 Lt",             "10,200", "PC", "—"),
    ]),
    ("002", "09-Aug-25", "2425603773", [
        ("2593962", "LOCTITE BONDACE DS SR1170TF 170kg",           "4,080",  "KG", "5151531460"),
    ]),
    ("003", "19-Aug-25", "2425603992", [
        ("2966562", "CAN-M_TIN-PLT @AP TrueGrip 500ml",           "10,500", "PC", "—"),
    ]),
    ("004", "22-Aug-25", "2425604125", [
        ("2979767", "SAL_PR @AP TGXTREME CL 0.5 L/1Ltr",          "90,000", "PC", "—"),
    ]),
    ("005", "29-Aug-25", "2425604258", [
        ("2966564", "CAN-M_TIN-PLT @AP Trugrip 4 Lt",             "3,114",  "PC", "—"),
    ]),
    ("006", "10-Nov-25", "2425606262", [
        ("2962930", "LOCTITE BONDACE 856LTF PSFG -165KG",         "1,815",  "KG", "5154434840"),
    ]),
    ("007", "17-Nov-25", "2425606525", [
        ("2593962", "LOCTITE BONDACE DS SR1170TF 170kg",           "4,250",  "KG", "5154581928"),
    ]),
    ("008", "02-Dec-25", "2425607003", [
        ("2593962", "LOCTITE BONDACE DS SR1170TF 170kg",           "5,440",  "KG", "5154794069"),
    ]),
    ("009", "02-Dec-25", "2425607002", [
        ("2966567", "SHIP_BORD-S @AP Trugrip 500ml",              "2,475",  "PC", "—"),
    ]),
    ("010", "04-Dec-25", "2425607057", [
        ("2966564", "CAN-M_TIN-PLT @AP Trugrip 4 Lt",             "2,124",  "PC", "—"),
    ]),
    ("011", "11-Dec-25", "2425607293", [
        ("2966562", "CAN-M_TIN-PLT @AP TrueGrip 500ml",           "20,625", "PC", "—"),
    ]),
    ("012", "12-Dec-25", "2425607361", [
        ("2979789", "SAL_PR @AP TG XTREME Box 100 X",             "10,000", "PC", "—"),
    ]),
    ("013", "17-Dec-25", "2425607492", [
        ("1712442", "JERR_PE @ 1.2 LTR Milky Rect. Jerry Can",    "4,200",  "PC", "—"),
        ("3092039", "LOCTITE BONDACE 007 PSFG",                   "825",    "KG", "5155065626"),
        ("1706617", "SAL_PP @ SAP label 125x90mm",                "300",    "PC", "—"),
    ]),
    ("014", "24-Dec-25", "2425607731", [
        ("3044894", "LOCTITE BONDACE 956LTF PSFG",                "1,815",  "KG", "5155170470"),
    ]),
]

# Standard checklist parameters (no COA)
CHECKS = [
    ("Quantity Received",    "As per Purchase Order / GRN",       "Match PO Qty"),
    ("Packaging Condition",  "Intact, undamaged, no leakage",      "Visual check"),
    ("Label / Marking",      "Correct material, batch, supplier",  "Visual check"),
    ("Batch / Lot Number",   "As per delivery challan",            "Cross-verify DC"),
    ("Visual / Physical",    "No damage, contamination, deformation","Visual check"),
]

CSS = """\
@page{size:A4 portrait;margin:10mm 10mm 10mm 14mm}
body{font-family:"Inter","Segoe UI",Arial,sans-serif;font-size:8.5pt;color:#222;margin:0;padding:0;background:#fff}
.ir{max-width:190mm;margin:0 auto;padding:5mm 7mm}
.ir-hdr{display:flex;align-items:center;gap:8px;border-bottom:2px solid #1a3a4a;padding-bottom:4px;margin-bottom:5px}
.ir-hdr-mid{flex:1}
.ir-hdr-mid h2{font-size:11pt;font-weight:700;color:#1a3a4a;margin:0 0 1px 0}
.ir-meta{display:flex;gap:12px;font-size:6.5pt;color:#555;flex-wrap:wrap}
.ir-meta span{white-space:nowrap}
.ir-lbl{font-size:7pt;font-weight:700;text-transform:uppercase;letter-spacing:.05em;color:#1a3a4a;margin:6px 0 2px;padding-bottom:1px;border-bottom:1px solid #ccc}
.ir-g2{display:grid;grid-template-columns:1fr 1fr;border:1px solid #bbb;border-radius:2px;margin-bottom:5px}
.f{display:flex;align-items:baseline;padding:2px 5px;border-bottom:1px solid #ddd;border-right:1px solid #ddd;font-size:7.5pt}
.f:nth-child(2n){border-right:none}
.fl{font-weight:600;color:#444;font-size:6pt;text-transform:uppercase;min-width:80px;white-space:nowrap;margin-right:4px}
.fv{flex:1;border-bottom:1px dotted #aaa;min-height:1em;font-size:7.5pt}
/* Material table */
.mt{width:100%;border-collapse:collapse;margin-bottom:5px}
.mt th{background:#eef3f5;color:#1a3a4a;font-size:6pt;font-weight:700;text-transform:uppercase;padding:2px 4px;border:1px solid #aaa;text-align:center}
.mt th.left{text-align:left}
.mt td{padding:2.5px 4px;border:1px solid #c5d2d8;font-size:7.5pt;vertical-align:middle}
.mt td.ctr{text-align:center}
.mt td.num{text-align:right;font-variant-numeric:tabular-nums}
/* Checklist table */
.ct{width:100%;border-collapse:collapse;margin-bottom:5px}
.ct th{background:#1a3a4a;color:#fff;font-size:6pt;font-weight:700;text-transform:uppercase;padding:3px 4px;border:1px solid #0f2530;text-align:center}
.ct th.left{text-align:left}
.ct td{padding:2.5px 4px;border:1px solid #c5d2d8;font-size:7.5pt;vertical-align:middle}
.ct td.n{text-align:center;width:16px;color:#888;font-size:7pt}
.ct td.ctr{text-align:center}
.ct tr:nth-child(even){background:#f4f7f9}
.badge{display:inline-block;padding:0 5px;border-radius:2px;font-size:6pt;font-weight:700;letter-spacing:.04em}
.ok{background:#d4edda;color:#155724;border:1px solid #b8dfc3}
.acc{background:#cce5ff;color:#004085;border:1px solid #99caff}
/* Disposition */
.disp{border:1px solid #c5d2d8;border-radius:2px;padding:3px 6px;margin-bottom:5px;font-size:7.5pt}
.disp-row{display:flex;gap:6px;align-items:baseline;margin:1px 0}
.disp-row b{font-size:6pt;text-transform:uppercase;color:#444;min-width:70px}
.bl{flex:1;border-bottom:1px dotted #aaa;min-height:.9em}
/* Signatures */
.ir-sig{display:grid;grid-template-columns:1fr 1fr 1fr;border:1px solid #bbb;border-radius:2px;margin-top:6px}
.ir-sc{padding:3px 6px;border-right:1px solid #ddd}
.ir-sc:last-child{border-right:none}
.ir-sc-r{font-size:6pt;font-weight:700;text-transform:uppercase;color:#1a3a4a;margin-bottom:1px}
.ir-sc-n{font-size:8pt;color:#333;border-bottom:1px dotted #999;padding-bottom:8px;margin-bottom:2px}
.ir-sc-l{font-size:6.5pt;color:#555;display:flex;gap:4px;align-items:baseline;margin-top:2px}
.ir-sc-l span{flex:1;border-bottom:1px dotted #999;min-height:.9em}
@media print{body,html{margin:0;padding:0}.ir{padding:3mm 5mm}}
"""

def material_rows(lines):
    rows = ""
    for mat, desc, qty, uom, batch in lines:
        rows += f"""
      <tr>
        <td class="ctr">{mat}</td>
        <td>{desc}</td>
        <td class="num">{qty}</td>
        <td class="ctr">{uom}</td>
        <td class="ctr">{batch}</td>
      </tr>"""
    return rows

def checklist_rows():
    rows = ""
    for i, (param, spec, method) in enumerate(CHECKS, 1):
        rows += f"""
      <tr>
        <td class="n">{i}</td>
        <td class="ct-param">{param}</td>
        <td>{spec}</td>
        <td>{method}</td>
        <td class="ctr">—</td>
        <td class="ctr"><span class="badge ok">OK</span></td>
        <td></td>
      </tr>"""
    return rows

def build_html(serial, date, doc_no, lines):
    iqc_no = f"IQC/2025-26/{serial}"
    mat_rows = material_rows(lines)
    chk_rows = checklist_rows()
    # first material description for header field
    first_desc = lines[0][1] if len(lines) == 1 else f"{len(lines)} materials (see below)"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>IQC Record {iqc_no} — PM/FRM/IQC-02</title>
<style>{CSS}</style>
</head>
<body>
<div class="ir">

  <!-- Header -->
  <div class="ir-hdr">
    <div class="ir-hdr-mid">
      <h2>Incoming Material Inspection Record</h2>
      <div class="ir-meta">
        <span><b>Doc No:</b> PM/FRM/IQC-02</span>
        <span><b>Ver:</b> 1.1</span>
        <span><b>Clause:</b> ISO 9001:2015 §8.4.2</span>
        <span><b>Eff. Date:</b> 01-Jul-2025</span>
        <span><b>IQC Serial:</b> <b style="color:#1a3a4a">{iqc_no}</b></span>
      </div>
    </div>
  </div>

  <!-- Record details -->
  <div class="ir-lbl">Receipt Details</div>
  <div class="ir-g2">
    <div class="f"><span class="fl">Date Received</span><span class="fv">{date}</span></div>
    <div class="f"><span class="fl">GRN / Doc No.</span><span class="fv">{doc_no}</span></div>
    <div class="f"><span class="fl">Supplier Name</span><span class="fv">Henkel / AP</span></div>
    <div class="f"><span class="fl">PO Reference</span><span class="fv"></span></div>
    <div class="f"><span class="fl">Material</span><span class="fv">{first_desc}</span></div>
    <div class="f"><span class="fl">Invoice No.</span><span class="fv"></span></div>
    <div class="f"><span class="fl">Qty Received</span><span class="fv">{lines[0][2]} {lines[0][3]}{" (+ " + str(len(lines)-1) + " more lines)" if len(lines) > 1 else ""}</span></div>
    <div class="f"><span class="fl">Batch / Lot No.</span><span class="fv">{lines[0][4]}{" / see table" if len(lines) > 1 else ""}</span></div>
  </div>

  <!-- Material lines table (shown when >1 line or always for clarity) -->
  <div class="ir-lbl">Material Line(s)</div>
  <table class="mt">
    <thead>
      <tr>
        <th>Material Code</th>
        <th class="left" style="width:55%">Material Description</th>
        <th>Qty</th>
        <th>UOM</th>
        <th>Batch / Lot No.</th>
      </tr>
    </thead>
    <tbody>{mat_rows}
    </tbody>
  </table>

  <!-- Inspection checklist -->
  <div class="ir-lbl">Inspection Checklist</div>
  <table class="ct">
    <thead>
      <tr>
        <th style="width:16px">#</th>
        <th class="left" style="width:22%">Parameter</th>
        <th class="left" style="width:28%">Specification / Acceptance Criteria</th>
        <th class="left" style="width:18%">Inspection Method</th>
        <th style="width:14%">Actual / Observed</th>
        <th style="width:10%">Result</th>
        <th class="left" style="width:12%">Remarks</th>
      </tr>
    </thead>
    <tbody>{chk_rows}
    </tbody>
  </table>

  <!-- Disposition -->
  <div class="ir-lbl">Disposition</div>
  <div class="disp">
    <div class="disp-row">
      <b>Decision</b>
      <span><span class="badge acc">ACCEPTED</span></span>
      &nbsp;&nbsp;
      <span style="font-size:7pt;color:#555">&#9744; Reject &nbsp; &#9744; Hold / Re-inspect &nbsp; &#9744; Conditional Accept</span>
    </div>
    <div class="disp-row" style="margin-top:3px"><b>NCR Ref.</b><span class="bl"></span></div>
    <div class="disp-row"><b>Remarks</b><span class="bl"></span></div>
  </div>

  <!-- Signatures -->
  <div class="ir-sig">
    <div class="ir-sc">
      <div class="ir-sc-r">Inspected By (QC Inspector)</div>
      <div class="ir-sc-n">&nbsp;</div>
      <div class="ir-sc-l">Sign: <span></span></div>
      <div class="ir-sc-l" style="margin-top:2px">Date: <span></span></div>
    </div>
    <div class="ir-sc">
      <div class="ir-sc-r">Verified By (Store In-Charge)</div>
      <div class="ir-sc-n">&nbsp;</div>
      <div class="ir-sc-l">Sign: <span></span></div>
      <div class="ir-sc-l" style="margin-top:2px">Date: <span></span></div>
    </div>
    <div class="ir-sc">
      <div class="ir-sc-r">Approved By (QA Manager)</div>
      <div class="ir-sc-n">AZAD Rajbhar</div>
      <div class="ir-sc-l">Sign: <span></span></div>
      <div class="ir-sc-l" style="margin-top:2px">Date: <span></span></div>
    </div>
  </div>

</div>
</body>
</html>
"""

# ---------------------------------------------------------------------------
# Generate files
# ---------------------------------------------------------------------------
for serial, date, doc_no, lines in RECORDS:
    html = build_html(serial, date, doc_no, lines)
    fname = os.path.join(OUT_DIR, f"IQC02_{serial}.html")
    with open(fname, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  Written: IQC02_{serial}.html  ({date}  GRN {doc_no})")

print(f"\nDone — {len(RECORDS)} files generated in:\n  {OUT_DIR}")
