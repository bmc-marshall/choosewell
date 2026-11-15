"""Choosewell showcase (not part of the skill): eight options-appraisal slides in the plum-and-coral family palette, one per method.
Built with Slidewell's slidekit. Every organisation and figure is invented."""
import math
import sys
from pathlib import Path

import os  # noqa: E402
# Needs Slidewell's build library (slidekit.py). Point SLIDEWELL_SCRIPTS at slidewell/scripts, or keep the two
# repos side by side (choosewell/ and slidewell/ in the same folder).
sys.path.insert(0, os.environ.get("SLIDEWELL_SCRIPTS", str(Path(__file__).resolve().parents[3] / "slidewell" / "slidewell" / "scripts")))
from lxml import etree  # noqa: E402
from slidekit import Kit, CategoryChartData, rgb  # noqa: E402
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION  # noqa: E402
from pptx.enum.dml import MSO_LINE_DASH_STYLE  # noqa: E402
from pptx.enum.shapes import MSO_SHAPE  # noqa: E402
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN  # noqa: E402
from pptx.util import Inches, Pt  # noqa: E402

A = "http://schemas.openxmlformats.org/drawingml/2006/main"
PLUM_D, PLUM, PLUM_M, LAV, LAV_P = rgb("2B1B3F"), rgb("5B3A8C"), rgb("8A6BBE"), rgb("C9B8E3"), rgb("F3EEF9")
CORAL, CORAL_L, INK, GREY, LINE = rgb("E0613F"), rgb("FBE3DA"), rgb("231A2E"), rgb("6B6475"), rgb("D9D3E0")
WHITE = rgb("FFFFFF")
RAG = {"Good": (rgb("DCEBD9"), rgb("2F6B2F")), "Fair": (rgb("F6E7C8"), rgb("8A6212")), "Poor": (rgb("F3D9D4"), rgb("9A3324"))}
kit = Kit(dict(body="Arial", main="2B1B3F", accent="E0613F", ink="231A2E", grey="6B6475", light="D9D3E0"))
T, W, H = kit.T, kit.T["W"], kit.T["H"]
C, L, R = PP_ALIGN.CENTER, PP_ALIGN.LEFT, PP_ALIGN.RIGHT
MID, TOP_, BOT = MSO_ANCHOR.MIDDLE, MSO_ANCHOR.TOP, MSO_ANCHOR.BOTTOM


def txt(s, x, y, w, h, t, pt, color, bold=False, align=L, anchor=TOP_, smart=True):
    return kit.text(s, x, y, w, h, t, pt, color, bold=bold, align=align, anchor=anchor, smart=smart)


def frame(n, method, headline, source=None):
    s = kit.new_slide()
    txt(s, 0.6, 0.38, 8, 0.3, method.upper(), 13, CORAL, bold=True, smart=False)
    kit.text(s, 0.6, 0.68, 12.1, 1.0, headline, 26, PLUM_D, bold=True, headline=True)
    if source:
        txt(s, 0.6, 6.95, 10.5, 0.3, source, 10, GREY, anchor=BOT)
    txt(s, W - 1.2, 6.95, 0.6, 0.3, str(n), 10, GREY, align=R, anchor=BOT, smart=False)
    return s


def pill(s, x, y, w, h, fill, t, pt, color, line=None, bold=True):
    b = kit.shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, fill, line=line, lw=1.25); b.adjustments[0] = 0.5
    txt(s, x, y, w, h, t, pt, color, bold=bold, align=C, anchor=MID, smart=False)
    return b


def freeform(s, pts, fill=None, line=None, lw=1.0, closed=True):
    fb = s.shapes.build_freeform(Inches(pts[0][0]), Inches(pts[0][1]), scale=1.0)
    fb.add_line_segments([(Inches(x), Inches(y)) for x, y in pts[1:]], close=closed)
    shp = fb.convert_to_shape()
    if fill is None:
        shp.fill.background()
    else:
        shp.fill.solid(); shp.fill.fore_color.rgb = fill
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line; shp.line.width = Pt(lw)
    kit.no_effects(shp)
    return shp


def alpha(shp, a):
    for clr in shp._element.spPr.iter(f"{{{A}}}srgbClr"):
        etree.SubElement(clr, f"{{{A}}}alpha").set("val", str(int(a * 100000)))
        break


def strike(tb):
    for p in tb.text_frame.paragraphs:
        for r in p.runs:
            r._r.get_or_add_rPr().set("strike", "sngStrike")


# ============================================================================ 1. options framework filter
s = frame(1, "Options framework", "Testing 20 choices against the critical success factors leaves one preferred "
          "route on each dimension", "Note: options framework filter, five dimensions, assessed against four critical success factors (fictional)")
dims = [("Scope", "What is covered?", [("National", "D"), ("Three regions", "C"), ("Two regions", "P"), ("One city", "C")]),
        ("Solution", "How is it done?", [("New build", "D"), ("Refurbish", "P"), ("Lease", "C"), ("Digital only", "D")]),
        ("Delivery", "Who does it?", [("In-house", "C"), ("Joint venture", "P"), ("Outsource", "C"), ("Charity partner", "D")]),
        ("Timing", "When, and how fast?", [("Big bang 2027", "D"), ("Phased, 3 years", "P"), ("Pilot then decide", "C"), ("Defer to 2030", "D")]),
        ("Funding", "Who pays?", [("Public capital", "C"), ("Private finance", "D"), ("Blended", "P"), ("User charges", "D")])]
y0, rh = 2.15, 0.83
cw, cg = 1.68, 0.12
cx0 = 2.75
txt(s, cx0, 1.78, 4 * cw + 3 * cg, 0.3, "Long list", 14, PLUM, bold=True, smart=False)
for i, (dim, q, opts) in enumerate(dims):
    y = y0 + i * rh
    kit.shape(s, MSO_SHAPE.RECTANGLE, 0.6, y, 9.2, rh - 0.1, LAV_P if i % 2 == 0 else WHITE)
    txt(s, 0.75, y + 0.06, 1.95, 0.35, dim, 17, PLUM_D, bold=True, smart=False)
    txt(s, 0.75, y + 0.39, 1.95, 0.3, q, 12, GREY, smart=False)
    for j, (o, st) in enumerate(opts):
        x = cx0 + j * (cw + cg); yy = y + (rh - 0.1 - 0.5) / 2
        if st == "P":
            pill(s, x, yy, cw, 0.5, CORAL, o, 13, WHITE)
        elif st == "C":
            pill(s, x, yy, cw, 0.5, WHITE, o, 13, PLUM, line=PLUM, bold=False)
        else:
            b = kit.shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, yy, cw, 0.5, rgb("EEECF1")); b.adjustments[0] = 0.5
            strike(txt(s, x, yy, cw, 0.5, o, 13, rgb("9C95A6"), align=C, anchor=MID, smart=False))
counts = {k: sum(st == k for _, _, os_ in dims for _, st in os_) for k in "PCD"}
assert counts == {"P": 5, "C": 7, "D": 8}
lx = 0.6
for k_, (lab, fill, col, line) in enumerate([("Preferred", CORAL, WHITE, None), ("Carried forward", WHITE, PLUM, PLUM), ("Discounted", rgb("EEECF1"), rgb("9C95A6"), None)]):
    b = kit.shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, 2.75 + k_ * 2.3, 6.42, 0.42, 0.24, fill, line=line, lw=1.25); b.adjustments[0] = 0.5
    txt(s, 2.75 + k_ * 2.3 + 0.52, 6.39, 1.7, 0.3, lab, 12, GREY, smart=False)
px = 10.15; pw_ = W - 0.6 - px
kit.shape(s, MSO_SHAPE.RECTANGLE, px, 1.78, pw_, 4.85, PLUM_D)
txt(s, px + 0.25, 1.95, pw_ - 0.5, 0.35, "Short list", 18, WHITE, bold=True, smart=False)
for k_, (lab, sub, hot) in enumerate([("Do minimum", "Benchmark for value", False), ("Preferred route", "All five preferred choices", True),
                                      ("Less ambitious", "One city, in-house", False), ("More ambitious", "Three regions, refurbish", False)]):
    yy = 2.5 + k_ * 0.98
    kit.shape(s, MSO_SHAPE.OVAL, px + 0.25, yy + 0.06, 0.4, 0.4, CORAL if hot else rgb("4A3566"))
    txt(s, px + 0.25, yy + 0.06, 0.4, 0.4, str(k_ + 1), 14, WHITE, bold=True, align=C, anchor=MID, smart=False)
    txt(s, px + 0.8, yy, pw_ - 0.95, 0.35, lab, 15, CORAL_L if hot else WHITE, bold=True, smart=False)
    txt(s, px + 0.8, yy + 0.36, pw_ - 0.95, 0.3, sub, 12, LAV, smart=False)

# ============================================================================ 2. swing weighting
crit = [("Benefit to residents", "None → 4,000 helped", 35), ("Cost", "£40M → £10M", 25), ("Deliverability", "Untested → proven", 20),
        ("Risk", "High → low", 12), ("Strategic fit", "Weak → strong", 8)]
assert sum(w for _, _, w in crit) == 100
opts2 = {"Phased joint venture": [80, 70, 75, 70, 90], "Organic growth": [55, 80, 60, 75, 60],
         "Licensing": [45, 85, 80, 60, 40], "Acquisition": [90, 30, 50, 40, 85]}
tot = {k: sum(w * sc / 100 for (_, _, w), sc in zip(crit, v)) for k, v in opts2.items()}
order = sorted(tot, key=tot.get, reverse=True)
lead = tot[order[0]] - tot[order[1]]
assert order[0] == "Phased joint venture" and round(lead) == 11
s = frame(2, "Swing weighting", f"Once the criteria are weighted, the phased joint venture leads the next option by "
          f"{round(lead)} points", "Note: weights from a facilitated swing-weighting session with the steering group; scores 0–100 (fictional)")
txt(s, 0.6, 1.85, 4.6, 0.3, "Swing weights", 16, CORAL, bold=True, smart=False)
txt(s, 0.6, 2.15, 4.6, 0.3, "How much does moving from worst to best matter?", 12, GREY, smart=False)
for i, (nm, rng, w) in enumerate(crit):
    y = 2.65 + i * 0.78
    txt(s, 0.6, y, 2.6, 0.32, nm, 15, PLUM_D, bold=True, smart=False)
    txt(s, 0.6, y + 0.32, 2.6, 0.28, rng, 12, GREY, smart=False)
    bw = 1.75 * w / 35
    kit.shape(s, MSO_SHAPE.RECTANGLE, 3.25, y + 0.1, bw, 0.36, PLUM)
    txt(s, 3.25 + bw + 0.08, y + 0.08, 0.6, 0.4, str(w), 15, PLUM_D, bold=True, anchor=MID, smart=False)
kit.line(s, 5.75, 1.9, 5.75, 6.55, LINE, 1)
shades = [PLUM_D, PLUM, PLUM_M, rgb("B49CDA"), rgb("DCCFF0")]
cd = CategoryChartData(); cd.categories = list(reversed(order))
for (nm, _, w), j in zip(crit, range(5)):
    cd.add_series(nm, [round(w * opts2[o][j] / 100, 1) for o in reversed(order)])
cx_, cy_, cw_, ch_ = 6.05, 2.25, 6.0, 3.95
txt(s, cx_, 1.85, 6.4, 0.3, "Weighted score, out of 100", 16, CORAL, bold=True, smart=False)
gf = s.shapes.add_chart(XL_CHART_TYPE.BAR_STACKED, Inches(cx_), Inches(cy_), Inches(cw_), Inches(ch_), cd)
ch = gf.chart; kit.style_chart(ch, pt=13); kit.transparent_chart(ch)
PX, PY, PW, PH = 0.37, 0.02, 0.6, 0.8
kit.plot_layout(ch, PX, PY, PW, PH)
pl = ch.plots[0]; pl.gap_width = 55; pl.overlap = 100
for ser, col in zip(pl.series, shades):
    ser.format.fill.solid(); ser.format.fill.fore_color.rgb = col; ser.format.line.color.rgb = WHITE; ser.format.line.width = Pt(0.75)
va = ch.value_axis; va.minimum_scale = 0; va.maximum_scale = 100; va.major_unit = 25; va.has_major_gridlines = False
kit.axis(va, None, pt=12); ch.category_axis.tick_labels.font.size = Pt(14)
ch.has_legend = False
kit.alt(gf, "Stacked bars of weighted scores out of 100: " + ", ".join(f"{o} {tot[o]:.0f}" for o in order) + ".")
n_ = len(order)
for i, o in enumerate(order):          # bar charts draw the last category at the top
    yy = cy_ + (PY + PH * (i + 0.5) / n_) * ch_
    xx = cx_ + (PX + PW * tot[o] / 100) * cw_
    txt(s, xx + 0.1, yy - 0.2, 0.7, 0.4, f"{tot[o]:.0f}", 17, CORAL if o == order[0] else PLUM_D, bold=True, anchor=MID, smart=False)
for j, (nm, _, _) in enumerate(crit):
    x = cx_ + 0.2 + (j % 3) * 2.0; y = 6.3 + (j // 3) * 0.28
    kit.shape(s, MSO_SHAPE.RECTANGLE, x, y + 0.05, 0.2, 0.17, shades[j])
    txt(s, x + 0.28, y, 1.75, 0.26, nm, 11, GREY, smart=False)

# ============================================================================ 3. sensitivity tornado
base = 12
vars_ = [("Take-up", "40% to 80%", -4, 24), ("Fee level", "£18 to £26", 5, 18), ("Build cost", "+30% to −10%", 6, 15),
         ("Delay", "12 months to none", 7, 13), ("Staff costs", "+15% to −5%", 9, 14)]
s = frame(3, "Sensitivity analysis", "Only take-up could turn the net present value negative, and it would have "
          "to fall below 58%", "Note: one-way sensitivity, each input moved across its plausible range with all others at base case (fictional)")
lx0, px0, pw_ = 0.6, 3.6, 6.4
X = lambda v: px0 + (v + 10) / 40 * pw_
ty0, rh = 2.35, 0.78
for v in range(-10, 31, 10):
    txt(s, X(v) - 0.5, ty0 - 0.45, 1.0, 0.3, f"£{v}M" if v else "0", 12, GREY, align=C, smart=False)
for i, (nm, rng, lo, hi) in enumerate(vars_):
    y = ty0 + i * rh
    txt(s, lx0, y + 0.02, 2.9, 0.32, nm, 16, PLUM_D, bold=True, smart=False)
    txt(s, lx0, y + 0.33, 2.9, 0.28, rng, 12, GREY, smart=False)
    bh = 0.46; yb = y + (rh - 0.1 - bh) / 2
    if lo < 0:
        kit.shape(s, MSO_SHAPE.RECTANGLE, X(lo), yb, X(0) - X(lo), bh, CORAL)
        kit.shape(s, MSO_SHAPE.RECTANGLE, X(0), yb, X(base) - X(0), bh, LAV)
    else:
        kit.shape(s, MSO_SHAPE.RECTANGLE, X(lo), yb, X(base) - X(lo), bh, LAV)
    kit.shape(s, MSO_SHAPE.RECTANGLE, X(base), yb, X(hi) - X(base), bh, PLUM)
kit.line(s, X(0), ty0 - 0.1, X(0), ty0 + 5 * rh, INK, 1.5)
kit.line(s, X(base), ty0 - 0.1, X(base), ty0 + 5 * rh, PLUM_D, 1.25, dash=MSO_LINE_DASH_STYLE.DASH)
txt(s, X(base) - 1.2, ty0 + 5 * rh + 0.05, 2.4, 0.3, "Base case £12M", 13, PLUM_D, bold=True, align=C, smart=False)
for k_, (lab, col) in enumerate([("Downside", LAV), ("Upside", PLUM), ("Value below zero", CORAL)]):
    y = 5.2 + k_ * 0.36
    kit.shape(s, MSO_SHAPE.RECTANGLE, 10.45, y + 0.05, 0.25, 0.2, col)
    txt(s, 10.8, y, 1.9, 0.3, lab, 12, GREY, smart=False)
bx = 10.45
kit.shape(s, MSO_SHAPE.RECTANGLE, bx, 2.3, W - 0.6 - bx, 2.6, CORAL_L)
txt(s, bx + 0.22, 2.45, 2.0, 0.3, "Switching value", 14, CORAL, bold=True, smart=False)
txt(s, bx + 0.22, 2.78, 2.0, 0.8, "58%", 46, CORAL, bold=True, smart=False)
txt(s, bx + 0.22, 3.6, 1.85, 1.2, "take-up at which the scheme stops paying back (base case 70%)", 13, INK)

# ============================================================================ 4. decision tree and value of information
ev_now = 0.6 * 20 + 0.4 * -6
ev_pilot = 0.6 * 19.5 + 0.4 * -0.5
ev_perfect = 0.6 * 20 + 0.4 * 0
assert (round(ev_now, 1), round(ev_pilot, 1), round(ev_perfect - ev_now, 1)) == (9.6, 11.5, 2.4)
s = frame(4, "Decision tree and value of information", "Piloting first is worth £1.9M more than launching now, "
          "nearly four times what the pilot costs", "Note: probabilities from the market study; payoffs are net present values in £M (fictional)")


def branch(x1, y1, x2, y2, label, col=None, w=1.75):
    col = col or rgb("8C8496")
    kit.line(s, x1, y1, x1 + 0.45, y2, col, w); kit.line(s, x1 + 0.45, y2, x2, y2, col, w)
    txt(s, x1 + 0.55, y2 - 0.36, x2 - x1 - 0.6, 0.32, label, 13, PLUM_D if col == CORAL else GREY, bold=col == CORAL, smart=False)


def end(x, y, val, col=None):
    freeform(s, [(x, y), (x + 0.24, y - 0.15), (x + 0.24, y + 0.15)], fill=col or rgb("8C8496"))
    txt(s, x + 0.34, y - 0.2, 1.1, 0.4, val, 15, CORAL if col == CORAL else PLUM_D, bold=True, anchor=MID, smart=False)


dx, dy = 1.5, 4.45
kit.shape(s, MSO_SHAPE.RECTANGLE, dx - 0.22, dy - 0.22, 0.44, 0.44, PLUM_D)
cy_now, cy_pil, cy_no = 3.05, 4.95, 6.3
branch(dx + 0.22, dy, 3.6, cy_now, "Launch now")
branch(dx + 0.22, dy, 3.6, cy_pil, "Pilot (£0.5M)", CORAL, 3)
branch(dx + 0.22, dy, 3.6, cy_no, "Do nothing")
end(3.6, cy_no, "£0M")
for cy, col, ev in [(cy_now, rgb("8C8496"), ev_now), (cy_pil, CORAL, ev_pilot)]:
    kit.shape(s, MSO_SHAPE.OVAL, 3.6, cy - 0.21, 0.42, 0.42, col)
    pill(s, 3.25, cy + 0.32, 1.15, 0.32, CORAL_L if col == CORAL else rgb("EEECF1"), f"EV £{ev:.1f}M", 12, CORAL if col == CORAL else PLUM_D)
branch(4.02, cy_now, 7.6, cy_now - 0.48, "High demand  60%")
branch(4.02, cy_now, 7.6, cy_now + 0.48, "Low demand  40%")
end(7.6, cy_now - 0.48, "£20M"); end(7.6, cy_now + 0.48, "−£6M")
branch(4.02, cy_pil, 7.6, cy_pil - 0.48, "High: then launch  60%", CORAL, 3)
branch(4.02, cy_pil, 7.6, cy_pil + 0.48, "Low: then stop  40%", CORAL, 3)
end(7.6, cy_pil - 0.48, "£19.5M", CORAL); end(7.6, cy_pil + 0.48, "−£0.5M", CORAL)
txt(s, 0.55, dy - 0.33, dx - 0.22 - 0.1 - 0.55, 0.66, "EV\v£11.5M", 13, CORAL, bold=True, align=R, anchor=MID, smart=False)
px = 9.7; pw_ = W - 0.6 - px
kit.shape(s, MSO_SHAPE.RECTANGLE, px, 1.95, pw_, 4.6, PLUM_D)
txt(s, px + 0.28, 2.1, pw_ - 0.5, 0.35, "Value of information", 16, WHITE, bold=True, smart=False)
for k_, (big, cap, col) in enumerate([(f"£{ev_perfect - ev_now:.1f}M", "most that perfect market information could be worth", LAV),
                                       (f"£{ev_pilot - ev_now:.1f}M", "captured by the pilot", CORAL_L),
                                       ("£0.5M", "cost of the pilot", LAV)]):
    yy = 2.65 + k_ * 1.25
    txt(s, px + 0.28, yy, pw_ - 0.5, 0.6, big, 30, col, bold=True, smart=False)
    txt(s, px + 0.28, yy + 0.58, pw_ - 0.5, 0.55, cap, 13, rgb("E2D8EE"))

# ============================================================================ 5. NPSV, BCR and optimism bias
ops = ["Phased JV", "Acquisition", "Organic", "Licensing"]
before = [24.0, 31.0, 14.0, 9.0]; after = [18.4, 15.5, 11.2, 7.2]; cost = [11.5, 30.0, 9.0, 6.0]
bcr = [round((a + c) / c, 1) for a, c in zip(after, cost)]
assert bcr == [2.6, 1.5, 2.2, 2.2]
assert round(before[1] - after[1], 1) == 15.5 and round(before[0] - after[0], 1) == 5.6
vfm = ["High" if b >= 2 else ("Medium" if b >= 1.5 else "Low") for b in bcr]
s = frame(5, "Economic case: value for money", "After optimism bias, the phased joint venture offers the best value for money, "
          "with a benefit-cost ratio of 2.6", "Note: net present social value over 30 years at 3.5%; optimism bias applied to capital costs (fictional)")
cd = CategoryChartData(); cd.categories = ops
cd.add_series("Before optimism bias", before); cd.add_series("After optimism bias", after)
cx_, cy_, cw_, ch_ = 0.6, 1.95, 8.2, 3.6
gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(cx_), Inches(cy_), Inches(cw_), Inches(ch_), cd)
ch = gf.chart; kit.style_chart(ch, pt=13); kit.transparent_chart(ch)
PX, PY, PW, PH = 0.09, 0.1, 0.91, 0.78
kit.plot_layout(ch, PX, PY, PW, PH)
pl = ch.plots[0]; pl.gap_width = 70; pl.overlap = 100
s1, s2 = pl.series
s1.format.fill.solid(); s1.format.fill.fore_color.rgb = rgb("E7DFF3"); s1.format.line.color.rgb = LAV; s1.format.line.width = Pt(1)
s1.format.line.dash_style = MSO_LINE_DASH_STYLE.DASH
s2.format.fill.solid(); s2.format.fill.fore_color.rgb = PLUM
p0 = s2.points[0]; p0.format.fill.solid(); p0.format.fill.fore_color.rgb = CORAL
dl = s2.data_labels; dl.show_value = True; dl.number_format = '"£"0.0"M"'; dl.number_format_is_linked = False
dl.position = XL_LABEL_POSITION.INSIDE_END; dl.font.size = Pt(14); dl.font.bold = True; dl.font.color.rgb = WHITE
va = ch.value_axis; va.minimum_scale = 0; va.maximum_scale = 35; va.major_unit = 10; va.has_major_gridlines = False
kit.axis(va, "Net present social value (£M)", pt=12); ch.category_axis.tick_labels.font.size = Pt(14)
kit.alt(gf, "Net present social value before and after optimism bias: " + "; ".join(f"{o} £{b}M to £{a}M" for o, b, a in zip(ops, before, after)) + ".")
Xc = lambda i: cx_ + (PX + PW * (i + 0.5) / 4) * cw_
Yv = lambda v: cy_ + (PY + PH) * ch_ - v / 35 * PH * ch_
txt(s, Xc(1) - 0.9, Yv(31) - 0.36, 1.8, 0.3, "£31.0M before", 12, PLUM_M, align=C, smart=False)
txt(s, 0.6, 5.72, 1.0, 0.36, "BCR", 14, PLUM_D, bold=True, anchor=MID, smart=False)
txt(s, 0.6, 6.2, 1.2, 0.36, "Value", 14, PLUM_D, bold=True, anchor=MID, smart=False)
for i, (b, v) in enumerate(zip(bcr, vfm)):
    txt(s, Xc(i) - 0.7, 5.72, 1.4, 0.36, f"{b:.1f}", 18, CORAL if i == 0 else PLUM_D, bold=True, align=C, anchor=MID, smart=False)
    f_, c_ = (CORAL, WHITE) if v == "High" and i == 0 else ((LAV_P, PLUM) if v == "High" else (rgb("F6E7C8"), rgb("8A6212")))
    pill(s, Xc(i) - 0.7, 6.22, 1.4, 0.34, f_, v, 12, c_)
kit.line(s, 0.6, 6.12, 8.8, 6.12, LINE, 0.75)
px = 9.3; pw_ = W - 0.6 - px
kit.shape(s, MSO_SHAPE.RECTANGLE, px, 1.95, pw_, 4.6, LAV_P)
txt(s, px + 0.25, 2.1, pw_ - 0.5, 0.35, "What changed", 16, CORAL, bold=True, smart=False)
txt(s, px + 0.25, 2.55, pw_ - 0.45, 3.9, [
    [("The acquisition", True, PLUM_D), (" led before adjustment, but its large capital cost attracts the biggest uplift: £15.5M of its value falls away.", False, INK)],
    [("The phased JV", True, PLUM_D), (" loses only £5.6M, because most of its cost is operating, not capital.", False, INK)]], 14, INK)
for k_, (lab, fill, line) in enumerate([("Before optimism bias", rgb("E7DFF3"), LAV), ("After", PLUM, None)]):
    x = 0.6 + 0.9 + k_ * 2.6
    kit.shape(s, MSO_SHAPE.RECTANGLE, x, 1.98, 0.25, 0.2, fill, line=line)
    txt(s, x + 0.33, 1.93, 2.2, 0.3, lab, 12, GREY, smart=False)

# ============================================================================ 6. Monte Carlo
def pdf(x, m, sd):
    return math.exp(-0.5 * ((x - m) / sd) ** 2) / (sd * math.sqrt(2 * math.pi))


def cdf(x, m, sd):
    return 0.5 * (1 + math.erf((x - m) / (sd * math.sqrt(2))))


p_jv, p_acq = 1 - cdf(0, 12, 8.5), 1 - cdf(0, 18, 32)
assert (round(p_jv * 100), round(p_acq * 100)) == (92, 71)
s = frame(6, "Risk analysis: Monte Carlo", "The acquisition could earn more, but the joint venture is far more likely "
          "to pay off at all", "Note: 10,000 simulations of net present value, varying take-up, prices, costs and timing together (fictional)")
gx0, gx1, gy0, gy1 = 0.9, 9.0, 2.15, 5.85
vmin, vmax = -60, 90
XM = lambda v: gx0 + (v - vmin) / (vmax - vmin) * (gx1 - gx0)
peak = pdf(12, 12, 8.5)
YM = lambda d: gy1 - d / peak * (gy1 - gy0) * 0.92
xs = [vmin + i * (vmax - vmin) / 150 for i in range(151)]
acq = [(XM(x), YM(pdf(x, 18, 32))) for x in xs]
jv = [(XM(x), YM(pdf(x, 12, 8.5))) for x in xs]
shp = freeform(s, [(XM(vmin), gy1)] + acq + [(XM(vmax), gy1)], fill=LAV); alpha(shp, 0.75)
loss = [(XM(x), YM(pdf(x, 18, 32))) for x in xs if x <= 0]
shp = freeform(s, [(XM(vmin), gy1)] + loss + [(XM(0), gy1)], fill=CORAL); alpha(shp, 0.85)
shp = freeform(s, [(XM(vmin), gy1)] + jv + [(XM(vmax), gy1)], fill=PLUM); alpha(shp, 0.85)
kit.line(s, gx0, gy1, gx1, gy1, INK, 1.25)
for v in range(-60, 91, 30):
    kit.line(s, XM(v), gy1, XM(v), gy1 + 0.07, INK, 1)
    txt(s, XM(v) - 0.5, gy1 + 0.1, 1.0, 0.3, f"£{v}M" if v else "0", 12, GREY, align=C, smart=False)
kit.line(s, XM(0), gy0 - 0.1, XM(0), gy1, INK, 1.25, dash=MSO_LINE_DASH_STYLE.DASH)
txt(s, gx0, gy1 + 0.42, gx1 - gx0, 0.3, "Net present value", 13, GREY, align=C, smart=False)
txt(s, XM(14) + 0.35, YM(pdf(12, 12, 8.5)) + 0.05, 2.2, 0.3, "Phased joint venture", 14, PLUM, bold=True, smart=False)
txt(s, XM(40), YM(pdf(40, 18, 32)) - 0.45, 1.8, 0.3, "Acquisition", 14, PLUM_M, bold=True, smart=False)
txt(s, XM(-55), YM(pdf(-25, 18, 32)) - 0.75, 2.4, 0.6, "Loses money", 14, CORAL, bold=True, smart=False)
px = 9.75; pw_ = W - 0.6 - px
for k_, (big, cap, col, fill) in enumerate([(f"{p_jv:.0%}", "chance the joint venture pays back", PLUM, LAV_P),
                                             (f"{p_acq:.0%}", "chance the acquisition pays back, with a much wider range", CORAL, CORAL_L)]):
    yy = 2.1 + k_ * 2.0
    kit.shape(s, MSO_SHAPE.RECTANGLE, px, yy, pw_, 1.8, fill)
    txt(s, px + 0.22, yy + 0.12, pw_ - 0.4, 0.75, big, 40, col, bold=True, smart=False)
    txt(s, px + 0.22, yy + 0.92, pw_ - 0.4, 0.8, cap, 13, INK)

# ============================================================================ 7. robustness across scenarios
scen = ["Strong growth", "Steady", "Downturn", "Policy shock"]
npv = {"Phased JV": [22, 15, 6, 8], "Acquisition": [34, 16, -9, 2], "Organic": [18, 13, 7, 4], "Licensing": [10, 9, 5, 9]}
best = [max(v[j] for v in npv.values()) for j in range(4)]
regret = {k: [best[j] - v[j] for j in range(4)] for k, v in npv.items()}
worst = {k: max(v) for k, v in regret.items()}
assert min(worst, key=worst.get) == "Phased JV" and worst["Phased JV"] == 12
s = frame(7, "Robustness: minimax regret", "Whatever the future, the phased joint venture never trails the best option "
          "by more than £12M, the smallest worst case", "Note: net present value in £M under each scenario; regret = shortfall against the best option in that scenario (fictional)")
gx, cwid, rh = 2.75, 1.65, 0.95
ty = 2.25
for j, sc in enumerate(scen):
    txt(s, gx + j * cwid, ty - 0.42, cwid, 0.35, sc, 14, PLUM, bold=True, align=C, smart=False)
txt(s, gx + 4 * cwid + 0.35, ty - 0.42, 3.0, 0.35, "Worst regret", 14, CORAL, bold=True, smart=False)
mx = max(worst.values())
for i, (o, vals) in enumerate(npv.items()):
    y = ty + i * (rh + 0.1)
    hot = o == "Phased JV"
    kit.shape(s, MSO_SHAPE.RECTANGLE, 0.6, y, gx + 4 * cwid - 0.6, rh, LAV_P if i % 2 == 0 else WHITE)
    txt(s, 0.75, y, 1.95, rh, o, 16, CORAL if hot else PLUM_D, bold=True, anchor=MID, smart=False)
    for j, v in enumerate(vals):
        x = gx + j * cwid
        isbest = v == best[j]
        if isbest:
            kit.shape(s, MSO_SHAPE.RECTANGLE, x + 0.12, y + 0.08, cwid - 0.24, rh - 0.16, None, line=PLUM, lw=2)
        txt(s, x, y + 0.1, cwid, 0.45, f"£{v}M" if v >= 0 else f"−£{-v}M", 18, PLUM_D if v >= 0 else CORAL, bold=True, align=C, anchor=MID, smart=False)
        txt(s, x, y + 0.53, cwid, 0.3, "best" if isbest else f"regret {regret[o][j]}", 11, PLUM if isbest else GREY, align=C, smart=False)
    bx = gx + 4 * cwid + 0.35
    bw = 2.6 * worst[o] / mx
    kit.shape(s, MSO_SHAPE.RECTANGLE, bx, y + 0.27, bw, rh - 0.54, CORAL if hot else LAV)
    txt(s, bx + bw + 0.1, y, 0.8, rh, f"£{worst[o]}M", 16, CORAL if hot else PLUM_D, bold=True, anchor=MID, smart=False)
kit.shape(s, MSO_SHAPE.RECTANGLE, gx + 0.12, 6.44, 0.3, 0.2, None, line=PLUM, lw=2)
txt(s, gx + 0.52, 6.39, 3.5, 0.3, "Best option in that scenario", 12, GREY, smart=False)

# ============================================================================ 8. five case model readiness
s = frame(8, "Five Case Model", "The business case is ready on four of the five cases; the commercial case still "
          "needs firm supplier quotes", "Note: readiness assessed against HM Treasury Green Book guidance (fictional)")
cases = [("compass", "Strategic", "Ready", "Clear case for change, backed by demand data in all three regions"),
         ("scale", "Economic", "Ready", "Preferred option has the best value for money: BCR 2.6"),
         ("handshake", "Commercial", "Needs work", "Only one indicative quote; procurement route not yet agreed"),
         ("coins", "Financial", "Ready", "Affordable within the capital envelope, with £1.2M headroom"),
         ("users", "Management", "Ready", "Programme board, plan and benefits owner in place")]
cw5, cg5 = (W - 1.2 - 4 * 0.2) / 5, 0.2
for k_, (ic, nm, st, note) in enumerate(cases):
    x = 0.6 + k_ * (cw5 + cg5)
    hot = st != "Ready"
    kit.shape(s, MSO_SHAPE.RECTANGLE, x, 2.0, cw5, 4.1, CORAL_L if hot else LAV_P)
    kit.shape(s, MSO_SHAPE.RECTANGLE, x, 2.0, cw5, 0.09, CORAL if hot else PLUM)
    kit.icon(s, ic, x + cw5 / 2 - 0.42, 2.35, 0.84, circle=CORAL if hot else PLUM)
    txt(s, x + 0.1, 3.38, cw5 - 0.2, 0.4, nm, 19, PLUM_D, bold=True, align=C, smart=False)
    txt(s, x + 0.1, 3.73, cw5 - 0.2, 0.3, "case", 13, GREY, align=C, smart=False)
    pill(s, x + cw5 / 2 - 0.75, 4.15, 1.5, 0.38, CORAL if hot else WHITE, st, 13, WHITE if hot else PLUM, line=None if hot else PLUM)
    txt(s, x + 0.2, 4.75, cw5 - 0.4, 1.3, note, 14, INK, align=C)
kit.shape(s, MSO_SHAPE.RECTANGLE, 0.6, 6.27, W - 1.2, 0.5, PLUM_D)
txt(s, 0.85, 6.27, W - 1.7, 0.5, [[("Next step: ", True, CORAL_L), ("request quotes from three suppliers by 30 January, then submit the full business case", False, WHITE)]],
    15, WHITE, anchor=MID)

out = Path(__file__).with_name("choosewell-showcase.pptx")
kit.save(str(out), title="Choosewell showcase")
print(out)
