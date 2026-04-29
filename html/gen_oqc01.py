"""
Generate 15 OQC-01 HTML forms (one per invoice) combined into a single HTML file.
Run: python gen_oqc01.py
Output: OQC01_ALL.html in the same directory
"""
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# (serial, inv_ref, date, mat_code, batch, description, qty, uom, vehicle, cust_po)
RECORDS = [
    ("001", "INV25227", "14-Aug-2025", "2967583", "P056080801", "LOCTITE BONDACE AP TRUEGRIP 500ML",    "7,048",  "CON", "MH43BX4855", "4593246373"),
    ("002", "INV25228", "17-Aug-2025", "2967598", "P057120802", "LOCTITE BONDACE AP TRUEGRIP 1L",       "4,476",  "CON", "MH43U9389",  "4593246373"),
    ("003", "INV25234", "21-Aug-2025", "2967583", "P861200801", "LOCTITE BONDACE AP TRUEGRIP 500ML",    "4,640",  "CON", "MH43Y8044",  "4593246373"),
    ("004", "INV25257", "28-Aug-2025", "2967583", "P111260801", "LOCTITE BONDACE AP TRUEGRIP 500ML",    "8,960",  "CON", "MH43U0974",  "4593246373"),
    ("005", "INV25416", "05-Nov-2025", "3050437", "P225291001", "LOCTITE HEAT PRO200 8 X 500 ML IN",    "8,496",  "CON", "MH43E6764",  "4593323707"),
    ("006", "INV25419", "07-Nov-2025", "2967598", "P592041102", "LOCTITE BONDACE AP TRUEGRIP 1L",       "4,662",  "CON", "MH04GC9314", "4593344692"),
    ("007", "INV25422", "08-Nov-2025", "2967598", "P593051102", "LOCTITE BONDACE AP TRUEGRIP 1L",       "3,978",  "CON", "MH11M4956",  "4593344692"),
    ("008", "INV25439", "13-Nov-2025", "2967619", "P929131103", "LOCTITE BONDACE AP TRUEGRIP 4L",       "1,116",  "CON", "MH11BL7867", "4593344692"),
    ("009", "INV25440", "14-Nov-2025", "2967619", "P930131103", "LOCTITE BONDACE AP TRUEGRIP 4L",       "1,160",  "CON", "MH43U0974",  "4593344692"),
    ("010", "INV25479", "27-Nov-2025", "2967583", "P476261101", "LOCTITE BONDACE AP TRUEGRIP 500ML",    "11,088", "CON", "MH04GC9314", "4593344692"),
    ("011", "INV25503", "04-Dec-2025", "2967619", "P069031203", "LOCTITE BONDACE AP TRUEGRIP 4L",       "1,440",  "CON", "MH43Y8045",  "4593366030"),
    ("012", "INV25513", "08-Dec-2025", "2967583", "P068071201", "LOCTITE BONDACE AP TRUEGRIP 500ML",    "7,056",  "CON", "MH43U9389",  "4593366030"),
    ("013", "INV25519", "13-Dec-2025", "2967583", "P475131201", "LOCTITE BONDACE AP TRUEGRIP 500ML",    "6,172",  "CON", "MH11M4956",  "4593366030"),
    ("014", "INV25551", "26-Dec-2025", "2967598", "P125211202", "LOCTITE BONDACE AP TRUEGRIP 1L",       "4,476",  "CON", "MH43U0974",  "4593366030"),
    ("015", "INV25559", "29-Dec-2025", "2967598", "P046291202", "LOCTITE BONDACE AP TRUEGRIP 1L",       "4,188",  "CON", "MH43BX4856", "4593366030"),
]

CSS = """\
@page{size:A4 portrait;margin:10mm 10mm 10mm 14mm}
body{font-family:"Inter","Segoe UI",Arial,sans-serif;font-size:8.5pt;color:#222;margin:0;padding:0;background:#fff}
.ir{max-width:190mm;margin:0 auto;padding:5mm 7mm;page-break-after:always}
.ir:last-child{page-break-after:avoid}
.ir-hdr{display:flex;align-items:center;gap:8px;border-bottom:2px solid #1a3a4a;padding-bottom:4px;margin-bottom:5px}
.ir-hdr-mid{flex:1}
.ir-hdr-mid h2{font-size:11pt;font-weight:700;color:#1a3a4a;margin:0 0 1px 0}
.ir-meta{display:flex;gap:12px;font-size:6.5pt;color:#555;flex-wrap:wrap}
.ir-meta span{white-space:nowrap}
.ir-lbl{font-size:7pt;font-weight:700;text-transform:uppercase;letter-spacing:.05em;color:#1a3a4a;margin:6px 0 2px;padding-bottom:1px;border-bottom:1px solid #ccc}
.ir-g2{display:grid;grid-template-columns:1fr 1fr;border:1px solid #bbb;border-radius:2px;margin-bottom:5px}
.f{display:flex;align-items:baseline;padding:2px 5px;border-bottom:1px solid #ddd;border-right:1px solid #ddd;font-size:7.5pt}
.f:nth-child(2n){border-right:none}
.fl{font-weight:600;color:#444;font-size:6pt;text-transform:uppercase;min-width:85px;white-space:nowrap;margin-right:4px}
.fv{flex:1;border-bottom:1px dotted #aaa;min-height:1em;font-size:7.5pt}
table{width:100%;border-collapse:collapse;margin-bottom:5px}
thead th{background:#1a3a4a;color:#fff;font-size:6pt;font-weight:700;text-transform:uppercase;padding:3px 4px;border:1px solid #0f2530;text-align:center}
thead th.left{text-align:left}
tbody tr:nth-child(even){background:#f4f7f9}
tbody td{padding:2.5px 4px;border:1px solid #c5d2d8;font-size:7.5pt;vertical-align:middle}
tbody td.n{text-align:center;width:16px;color:#888;font-size:7pt}
tbody td.ctr{text-align:center}
.ccp{font-size:5pt;font-weight:700;color:#c0392b;background:#fde8e8;padding:0 2px;border-radius:1px;margin-left:2px;vertical-align:middle}
.badge{display:inline-block;padding:0 5px;border-radius:2px;font-size:6pt;font-weight:700;letter-spacing:.04em}
.ok{background:#d4edda;color:#155724;border:1px solid #b8dfc3}
.na{background:#e9ecef;color:#555;border:1px solid #ccc}
.clr{background:#cce5ff;color:#004085;border:1px solid #99caff}
.disp{border:1px solid #c5d2d8;border-radius:2px;padding:3px 6px;margin-bottom:5px;font-size:7.5pt}
.disp-row{display:flex;gap:6px;align-items:baseline;margin:2px 0}
.disp-row b{font-size:6pt;text-transform:uppercase;color:#444;min-width:80px}
.bl{flex:1;border-bottom:1px dotted #aaa;min-height:.9em}
.ir-sig{display:grid;grid-template-columns:1fr 1fr 1fr;border:1px solid #bbb;border-radius:2px;margin-top:6px}
.ir-sc{padding:3px 6px;border-right:1px solid #ddd}
.ir-sc:last-child{border-right:none}
.ir-sc-r{font-size:6pt;font-weight:700;text-transform:uppercase;color:#1a3a4a;margin-bottom:1px}
.ir-sc-n{font-size:8pt;color:#333;border-bottom:1px dotted #999;padding-bottom:8px;margin-bottom:2px}
.ir-sc-l{font-size:6.5pt;color:#555;display:flex;gap:4px;align-items:baseline;margin-top:2px}
.ir-sc-l span{flex:1;border-bottom:1px dotted #999;min-height:.9em}
@media print{body,html{margin:0;padding:0}.ir{padding:3mm 5mm}}
"""

def build_form(serial, inv, date, mat, batch, desc, qty, uom, vehicle, po):
    oqc_no = f"OQC/2025-26/{serial}"
    return f"""<div class="ir">
  <div class="ir-hdr">
    <div class="ir-hdr-mid">
      <h2>Outgoing / Dispatch Inspection Record</h2>
      <div class="ir-meta">
        <span><b>Doc No:</b> PM/FRM/OQC-01</span>
        <span><b>Ver:</b> 1.1</span>
        <span><b>Clause:</b> ISO 9001:2015 §8.6</span>
        <span><b>Eff. Date:</b> 01-Jul-2025</span>
        <span><b>OQC Serial:</b> <b style="color:#1a3a4a">{oqc_no}</b></span>
      </div>
    </div>
  </div>

  <div class="ir-lbl">Dispatch Details</div>
  <div class="ir-g2">
    <div class="f"><span class="fl">Invoice / Ref No.</span><span class="fv">{inv}</span></div>
    <div class="f"><span class="fl">Dispatch Date</span><span class="fv">{date}</span></div>
    <div class="f"><span class="fl">Customer Name</span><span class="fv">Henkel / AP</span></div>
    <div class="f"><span class="fl">Customer PO</span><span class="fv">{po}</span></div>
    <div class="f"><span class="fl">Product Description</span><span class="fv">{desc}</span></div>
    <div class="f"><span class="fl">Material Code</span><span class="fv">{mat}</span></div>
    <div class="f"><span class="fl">Batch / Prod. Order</span><span class="fv">{batch}</span></div>
    <div class="f"><span class="fl">Qty Dispatched</span><span class="fv">{qty} {uom}</span></div>
    <div class="f"><span class="fl">Vehicle No.</span><span class="fv">{vehicle}</span></div>
    <div class="f"><span class="fl">Transporter</span><span class="fv"></span></div>
  </div>

  <div class="ir-lbl">Dispatch Inspection Checklist</div>
  <table>
    <thead>
      <tr>
        <th style="width:16px">#</th>
        <th class="left" style="width:28%">Parameter</th>
        <th class="left" style="width:30%">Acceptance Criteria</th>
        <th style="width:16%">Actual / Observed</th>
        <th style="width:10%">Result</th>
        <th class="left">Remarks</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td class="n">1</td>
        <td>Quantity Matches Order <span class="ccp">CCP</span></td>
        <td>As per PO / DO</td>
        <td class="ctr">{qty} {uom}</td>
        <td class="ctr"><span class="badge ok">OK</span></td>
        <td></td>
      </tr>
      <tr>
        <td class="n">2</td>
        <td>Label Correct (Product, Batch) <span class="ccp">CCP</span></td>
        <td>Matches spec &amp; customer req.</td>
        <td class="ctr">Verified</td>
        <td class="ctr"><span class="badge ok">OK</span></td>
        <td></td>
      </tr>
      <tr>
        <td class="n">3</td>
        <td>Packaging Intact &amp; Sealed <span class="ccp">CCP</span></td>
        <td>No damage / leaks / open cartons</td>
        <td class="ctr">Visual</td>
        <td class="ctr"><span class="badge ok">OK</span></td>
        <td></td>
      </tr>
      <tr>
        <td class="n">4</td>
        <td>Cleanliness — No Contamination <span class="ccp">CCP</span></td>
        <td>Clean, no foreign matter / stains</td>
        <td class="ctr">Visual</td>
        <td class="ctr"><span class="badge ok">OK</span></td>
        <td></td>
      </tr>
      <tr>
        <td class="n">5</td>
        <td>Weight Verification (Random)</td>
        <td>Within ±2% of declared weight</td>
        <td class="ctr">—</td>
        <td class="ctr"><span class="badge ok">OK</span></td>
        <td></td>
      </tr>
      <tr>
        <td class="n">6</td>
        <td>COC / COA Attached <span class="ccp">CCP</span></td>
        <td>Enclosed</td>
        <td class="ctr">—</td>
        <td class="ctr"><span class="badge na">N/A</span></td>
        <td>Not required</td>
      </tr>
      <tr>
        <td class="n">7</td>
        <td>MSDS Enclosed (if hazmat)</td>
        <td>If applicable</td>
        <td class="ctr">—</td>
        <td class="ctr"><span class="badge na">N/A</span></td>
        <td>Not required</td>
      </tr>
      <tr>
        <td class="n">8</td>
        <td>Customer-Specific Requirements <span class="ccp">CCP</span></td>
        <td>Per PO / SOW</td>
        <td class="ctr">Verified</td>
        <td class="ctr"><span class="badge ok">OK</span></td>
        <td></td>
      </tr>
    </tbody>
  </table>

  <div class="ir-lbl">Disposition</div>
  <div class="disp">
    <div class="disp-row">
      <b>Decision</b>
      <span><span class="badge clr" style="font-size:7pt;padding:1px 8px">CLEARED FOR DISPATCH</span></span>
      &nbsp;&nbsp;
      <span style="font-size:7pt;color:#555">&#9744; Hold &nbsp; &#9744; Reject &nbsp; &#9744; Re-inspect</span>
    </div>
    <div class="disp-row" style="margin-top:3px"><b>NCR Ref.</b><span class="bl"></span></div>
    <div class="disp-row"><b>Remarks</b><span class="bl"></span></div>
  </div>

  <div class="ir-sig">
    <div class="ir-sc">
      <div class="ir-sc-r">Inspected By (QC Inspector)</div>
      <div class="ir-sc-n">&nbsp;</div>
      <div class="ir-sc-l">Sign: <span></span></div>
      <div class="ir-sc-l" style="margin-top:2px">Date: <span></span></div>
    </div>
    <div class="ir-sc">
      <div class="ir-sc-r">Verified By (Dispatch In-Charge)</div>
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
</div>"""

forms = "\n".join(build_form(*r) for r in RECORDS)

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>OQC-01 Records — OQC/2025-26/001 to 015 — PM/FRM/OQC-01</title>
<style>{CSS}</style>
</head>
<body>
{forms}
</body>
</html>"""

out = os.path.join(OUT_DIR, "OQC01_ALL.html")
with open(out, "w", encoding="utf-8") as f:
    f.write(html)
print(f"Written: OQC01_ALL.html — {len(RECORDS)} forms")
