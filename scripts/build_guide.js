// build_guide.js - rebuilds assets/choosewell-guide.docx (the offline guide).
// Needs: npm install docx. Diagrams: assets/guide/*.mmd (re-render with mmdc -i X.mmd -o X.png).
// Usage: node scripts/build_guide.js [out.docx]
const fs = require("fs");
const D = require("docx");
const path = require("path");
const G = path.join(__dirname, "..", "assets", "guide");
const OUT = process.argv[2] || path.join(__dirname, "..", "assets", "choosewell-guide.docx");
const { Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell, WidthType, ShadingType,
  AlignmentType, LevelFormat, ImageRun, PageBreak, TableOfContents, Footer, PageNumber, BorderStyle, Bookmark, InternalHyperlink } = D;

const FONT = "Arial", NAVY = "1F3A5F", LINKC = "1F5FA8";
const W = 9360;
const out = [];
const anchors = new Set(), used = new Set();

// text with **bold** and [[label|anchor]] links
function runs(t, base = {}) {
  return String(t).split(/(\*\*[^*]+\*\*|\[\[[^\]]+\]\])/g).filter(Boolean).map(s => {
    if (s.startsWith("**")) return new TextRun({ text: s.slice(2, -2), bold: true, font: FONT, ...base });
    if (s.startsWith("[[")) {
      const [label, anchor] = s.slice(2, -2).split("|"); used.add(anchor);
      return new InternalHyperlink({ anchor, children: [new TextRun({ text: label, font: FONT, color: LINKC, underline: {}, ...base })] });
    }
    return new TextRun({ text: s, font: FONT, ...base });
  });
}
const P = (t, o = {}) => out.push(new Paragraph({ children: runs(t), spacing: { after: 110 }, ...o }));
function H(lvl, t, anchor, brk = false) {
  const child = new TextRun({ text: t });
  if (anchor) anchors.add(anchor);
  out.push(new Paragraph({ heading: lvl, pageBreakBefore: brk, children: anchor ? [new Bookmark({ id: anchor, children: [child] })] : [child] }));
}
const H1 = (t, a, brk = true) => H(HeadingLevel.HEADING_1, t, a, brk);
const H2 = (t, a, brk = false) => H(HeadingLevel.HEADING_2, t, a, brk);
const H3 = (t, a) => H(HeadingLevel.HEADING_3, t, a);
const B = items => items.forEach(t => out.push(new Paragraph({ numbering: { reference: "bul", level: 0 }, children: runs(t), spacing: { after: 60 } })));
let nc = 0;
const N = items => { const r = "num" + (++nc); items.forEach(t => out.push(new Paragraph({ numbering: { reference: r, level: 0 }, children: runs(t), spacing: { after: 60 } }))); };
function T(headers, rows, widths, opts = {}) {
  const tot = widths.reduce((a, b) => a + b, 0);
  const ws = widths.map(w => Math.round(w / tot * W)); ws[ws.length - 1] += W - ws.reduce((a, b) => a + b, 0);
  const cell = (t, i, head, firstCol) => new TableCell({
    width: { size: ws[i], type: WidthType.DXA }, margins: { top: 60, bottom: 60, left: 90, right: 90 },
    shading: head ? { type: ShadingType.CLEAR, fill: NAVY, color: "auto" } : (firstCol && opts.shadeFirst ? { type: ShadingType.CLEAR, fill: "EEF3F8", color: "auto" } : undefined),
    children: String(t).split("\n").map(line => new Paragraph({ spacing: { after: 20 },
      children: head ? [new TextRun({ text: line, bold: true, color: "FFFFFF", font: FONT, size: 18 })] : runs(line, firstCol && opts.shadeFirst ? { bold: true } : {}) }))
  });
  const rows_ = rows.map(r => new TableRow({ cantSplit: true, children: r.map((c, i) => cell(c, i, false, i === 0)) }));
  out.push(new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: ws,
    rows: headers ? [new TableRow({ tableHeader: true, children: headers.map((h, i) => cell(h, i, true)) }), ...rows_] : rows_ }));
  out.push(new Paragraph({ children: [], spacing: { after: 80 } }));
}
function IMG(file, w, h, maxH, maxW = 600) {
  let width = maxW, height = Math.round(h * maxW / w);
  if (height > maxH) { height = maxH; width = Math.round(w * maxH / h); }
  out.push(new Paragraph({ alignment: AlignmentType.CENTER, children: [new ImageRun({ type: "png", data: fs.readFileSync(path.join(G, file)), transformation: { width, height } })] }));
}
const BOX = (t, fill = "EEF3F8") => out.push(new Paragraph({ children: runs(t), shading: { type: ShadingType.CLEAR, fill, color: "auto" },
  border: { left: { style: BorderStyle.SINGLE, size: 18, color: NAVY, space: 6 } }, spacing: { before: 80, after: 140 }, indent: { left: 120 } }));
const EX = t => BOX("**In the example:** " + t, "FFF7E6");

const S = n => `[[Step ${n}|s${n}]]`;
function STEP(n, title, purpose, card, how, watch, example) {
  H2(`Step ${n}: ${title}`, "s" + n, true);
  P(purpose);
  T(null, card, [2.3, 7.7], { shadeFirst: true });
  H3("How");
  N(how);
  if (watch) B(watch.map(w => "**Watch out:** " + w));
  EX(example);
}

// ======================= COVER =======================
out.push(new Paragraph({ children: [new TextRun({ text: "Choosewell", bold: true, size: 56, font: FONT, color: NAVY })], spacing: { before: 2000, after: 200 } }));
out.push(new Paragraph({ children: [new TextRun({ text: "A step-by-step guide to making structured choices", size: 32, font: FONT })], spacing: { after: 300 } }));
P("Use this to compare options and make a choice you can defend: which partner, which location, which activities, what organisational form, or a smaller design decision. You need a spreadsheet and nothing else.");
H3("How this guide is organised");
T(["Part", "What's in it", "Labelled"], [
  ["[[The Guide|guide]]", "Ten steps, in order, with a worked example running through every step", "Step 1 to Step 10"],
  ["[[The three trees|trees]]", "Short decision trees that set up the appraisal", "Tree 1, Tree 2, Tree 3"],
  ["[[The Toolkit|toolkit]]", "Reference material that the steps point to", "Toolkit A to Toolkit I"]], [2.2, 5.5, 2.3]);
P("Links in blue jump to the section named. If you're new, read the Guide once, then work through it with your own decision.");
BOX("**Three rules that matter most.** Agree how you'll judge options before anyone scores them. Only rule an option out for failing something truly non-negotiable; not knowing something is a reason to find out, not to mark it down. Keep every claim traceable to a source.");
H3("Where to start");
T(["If you…", "Go to"], [
  ["Are starting from scratch", `[[Tree 1|t1]], then ${S(1)}`],
  ["Know what you're deciding, but not how thorough to be", S(2)],
  ["Already have a list of options", S(4)],
  ["Already have options and criteria agreed", S(6)],
  ["Have scores and want to know if they're robust", S(8)],
  ["Have a result and need to present it", S(10)],
  ["Need to look up a method or calculation", "[[The Toolkit|toolkit]]"]], [6, 4]);
out.push(new Paragraph({ children: [new PageBreak()] }));
H1("Contents", null, false);
out.push(new TableOfContents("Contents", { hyperlink: true, headingStyleRange: "1-2" }));
P("If the contents list is empty, right-click it in Word and choose Update Field.");

// ======================= THE GUIDE =======================
H1("The Guide: ten steps", "guide");
IMG("flow.png", 635, 1383, 250, 320);
T(["Step", "What you're doing", "Main output"], [
  [S(1) + ": Frame the decision", "Pin down what's being decided, by whom, and why", "A one-page frame"],
  [S(2) + ": Set the rules and rigour", "Decide which rulebook applies and how thorough to be ([[Tree 2|t2]])", "Method base, depth, defensibility"],
  [S(3) + ": Build the long list", "Gather every reasonable option, including changing nothing", "A numbered long list"],
  [S(4) + ": Choose how to assess", "Pick the assessment method ([[Tree 3|t3]])", "A method"],
  [S(5) + ": Agree criteria, scores and weights", "Decide how to judge options, before judging them", "A criteria table"],
  [S(6) + ": Gather the evidence", "Find out what's true about each option, with sources", "An evidence log"],
  [S(7) + ": Assess the options", "Apply the method, ideally as a group", "Agreed scores"],
  [S(8) + ": Test the result", "Check consistency and robustness", "A tested ranking"],
  [S(9) + ": Decide and explain", "Choose, say why, say what could go wrong", "A recommendation"],
  [S(10) + ": Check and present", "Verify, then tell the story", "A checked write-up or deck"]], [3.2, 4.6, 2.2]);
B(["Keep everything in one spreadsheet, one tab per [[template|tkF]].",
  "Small, reversible decisions can move through all ten steps in an hour or two; large ones may take weeks. [[Step 2|s2]] tells you which you're dealing with."]);

// ---- Trees
H1("The three trees", "trees");
T(["Tree", "Answers", "Looks only at", "Gives you", "Used in"], [
  ["[[Tree 1|t1]]", "What type of choice is this?", "The subject of the decision", "A type of choice, with suggested criteria and a storyline", "Before [[Step 1|s1]]"],
  ["[[Tree 2|t2]]", "Which rules apply, and how thorough to be?", "The setting: who it's for, reversibility, stakes, scrutiny", "Method base, depth, defensibility", "[[Step 2|s2]]"],
  ["[[Tree 3|t3]]", "How to assess the options?", "The options and evidence (plus defensibility from Tree 2)", "An assessment method", "[[Step 4|s4]]"]], [1.2, 2.3, 2.7, 2.6, 1.2]);
B(["The trees don't overlap: Tree 1 is about the subject, Tree 2 the setting, Tree 3 the options and evidence.",
  "Tree 2 comes before Tree 3 because the setting limits the methods. UK business cases can't use simple points-scoring, for example, and a quick decision doesn't warrant an elaborate method."]);

H2("Tree 1: What are you deciding?", "t1", true);
B(["Big decisions follow a natural order, from the highest level to the lowest: what's covered, what you'll do, where, how you're organised, who with, then the details.",
  "Later choices depend on earlier ones (\"where to play\" before \"how to win\"; form follows function).",
  "**Start at the top and stop at the first question you can't yet answer.** If you've been handed a narrower question, run down the list anyway and note any open earlier questions as assumptions.",
  "**Not on the ladder:** a single go/no-go, timing or amount decision (launch or not, pilot first, settle or go to trial, bid or not, invest now or wait, how much to spend). That's a **whether, when or how much** choice: go straight to [[Tree 2|t2]] and use a [[quantified decision tree|mech-qtree]]."]);
T(["Question", "If no", "If yes"], [
  ["1. Have you agreed what's in and out of scope?", "Your choice is about **scope**: which sectors, customers, offers and geographies are priorities", "Go to question 2"],
  ["2. Do you know which activities you'll do, and in what order?", "Your choice is **what**: which activities, and what first (supporting only: see the note below)", "Go to question 3"],
  ["3. Do you know where you'll operate?", "Your choice is **where**: countries, regions, cities, sites", "Go to question 4"],
  ["4. Do you know how you'll be organised?", "Your choice is **structure**. If one form is best overall, choose it once; if it depends on each case (e.g. a contracting model per deal), you need **structure by situation**", "Go to question 5"],
  ["5. Do you know who you'll work with?", "Your choice is **who**: partners, suppliers, grantees", "What's left are **design choices**: team, funding, host, name (name is supporting only)"]], [3.4, 4.8, 1.8]);
BOX("**Lighter areas.** This method handles **activity prioritisation** and **naming** only lightly, as inputs to the other choices: what a unit will do informs its structure, and a name follows once the structure is settled. If either is your main question, treat what you get here as a first pass. Activity analysis on its own usually needs fuller process, capacity and cost modelling; naming needs linguistic and cultural checks in each market, trademark and domain searches, and audience testing.", "FFF7E6");
P(`Then go to ${S(1)}.`);
IMG("n1.png", 1288, 2067, 330);

H2("Tree 2: What rules apply, and how much rigour?", "t2", true);
P("Answer all four questions and record the answers on your frame.");
T(["Question", "Answer", "Then"], [
  ["1. Who is the decision for?", "UK central government", "Follow the [[Green Book|tkG]]"],
  ["", "US federal government", "Follow [[OMB and GAO guidance|tkG]]"],
  ["", "Anyone else", "Use the [[general method|tkG]]"],
  ["2. How reversible is it, and what's at stake?", "Easy to reverse and low stakes", "Quick depth"],
  ["", "Hard to reverse and high stakes", "Full depth"],
  ["", "Anything in between", "Standard depth"],
  ["3. Will an auditor, regulator, board or the public scrutinise it?", "Yes", "It must be defensible: pass/fail tests and a full decisions log"],
  ["", "No", "Normal record-keeping"],
  ["4. Can analysis answer it now?", "Yes", `Continue to ${S(3)}`],
  ["", "No: cause and effect are unclear and experts disagree about what would work", "Stop. Pilot or stage the decision first, then return (see [[Toolkit C|tkC]])"]], [3.4, 3.4, 3.2]);
T(["Depth", "What it adds"], [
  ["Quick", "A few criteria with written definitions; a check of what would change the answer; sources for every fact"],
  ["Standard", "Knock-out tests; private scoring before discussion; price compared separately; prioritised open questions; what could go wrong"],
  ["Full", "A structured long list; costed comparison of the short list; scenarios; independent review"]], [2, 8]);
IMG("n2.png", 871, 1819, 230);

H2("Tree 3: How will you assess the options?", "t3", true);
T(["First: what kind of answer do you need?", "Then"], [
  ["**Match**: which option fits each situation as it arises?", "Use a [[decision tree|mech-tree]]"],
  ["**Sequence**: which of many activities first?", "If it's unclear who does what today, start with [[responsibility mapping|mech-raci]]. Then use the [[impact and availability matrix|mech-matrix]] (what you can do) or the [[Eisenhower matrix|mech-eis]] (what you must do)"],
  ["**Select**: pick or shortlist from a set", "Use the table below"]], [4, 6]);
T(["How many options?", "Then ask", "Use"], [
  ["Many (about 20 or more)", "Hard data for the key tests? **Yes**", "[[Threshold filter|mech-threshold]], then assess the survivors"],
  ["Many", "**No**, mainly judgement", "Knock-outs, then a light [[scored screen|mech-scored]]"],
  ["Few", "Must it be defensible (Tree 2, question 3)? **Yes**", "[[Red/amber/green against success factors|mech-rag]]"],
  ["Few", "**No**, and it's one design choice with 2–4 options", "[[Pros and cons|mech-proscons]]"],
  ["Few", "**No**, otherwise", "[[Scored criteria|mech-scored]] with swing weights"]], [2.5, 4, 3.5]);
B(["**Then, whatever the answer:** if a few uncertain events drive the result, or the choice comes in stages (pilot, phase, wait, test first), add a [[quantified decision tree|mech-qtree]] for the two or three options left. If every consequence can be put in money, the tree replaces the scoring method and you can skip [[Step 5|s5]].",
  "Methods often combine: a threshold filter on 40 places, then scored criteria on the five that survive.",
  "If costs and benefits can be put into numbers for the short list, add a costed comparison at the end ([[Toolkit B|tkB]])."]);
P(`Then go to ${S(5)}.`);
IMG("n3.png", 1384, 949, 330);

// ---- Steps
STEP(1, "Frame the decision", "Write down exactly what's being decided before looking at options. Most appraisals that go wrong do so here, because people are quietly answering different questions.",
  [["Skip if", "The decision-maker has already agreed a written frame"], ["You'll end up with", "A one-page frame the group has agreed"], ["Template", "[[Frame|tpl-frame]], [[Principles|tpl-principles]]"], ["Next", S(2)]],
  ["Write the decision in one sentence: what's chosen, for what purpose, over what period.", "Note who decides, and by when.",
    "Describe the need without naming a solution: \"move chilled food from donors to hubs\", not \"a logistics contract\".",
    "Sort related decisions: already decided, deciding now, deciding later.",
    "Write four to eight principles any good answer must respect, each with the issue it addresses and what it implies.",
    "Say what happens after the decision, since that sets how much detail you need now."],
  ["Don't let the frame name the answer. \"Choose a national logistics company\" has already ruled out a pair of regional ones."],
  "shortlisting two or three logistics partners for site visits, ahead of a three-year contract. The operations committee decides. Already decided: six regional hubs and the budget. Deciding later: contract terms.");
STEP(2, "Set the rules and rigour", "Use [[Tree 2|t2]] to decide which rulebook applies, how thorough to be, and how carefully to document the work.",
  [["Skip if", "Never. It takes five minutes and stops a quick screen being mistaken for a business case"], ["You'll end up with", "A method base, a depth and a defensibility setting, written on the frame"], ["Template", "[[Frame|tpl-frame]]"], ["Next", `${S(3)}; or, if analysis can't answer the question yet, design a pilot ([[Toolkit C|tkC]])`]],
  ["Answer the four questions in [[Tree 2|t2]].", "Record the answers on the frame.", "Tell everyone involved, so expectations match."],
  null,
  "a charity, so the general method. The shortlist is easy to revisit but the contract isn't, so standard depth with extra checks on the final two or three. Trustees will scrutinise it, so it must be defensible.");
STEP(3, "Build the long list", "Gather every reasonable option before narrowing down, so the choice isn't limited to whatever someone thought of first.",
  [["Skip if", "You already have a complete list (go to " + S(4) + ")"], ["You'll end up with", "A numbered long list in families, plus early exclusions with reasons"], ["Template", "[[Options|tpl-options]]"], ["Next", S(4)]],
  ["Collect options from stakeholders, from how others solved the same problem, and from your own thinking.",
    "Include business as usual: what happens if nothing changes. It's the benchmark for every other option.",
    "If the decision is uncertain and hard to reverse, add flexible versions: pilot first, phase it, start small.",
    "Group options into families (e.g. national vs regional) and number them; never renumber.",
    "Rule out anything clearly impossible now, with one line on why."],
  null,
  "20 suppliers in two families, national carriers and regional specialists, plus business as usual (the current volunteer drivers) as the benchmark.");
STEP(4, "Choose how to assess", "Use [[Tree 3|t3]] to pick the method that fits your options and evidence.",
  [["Skip if", "The method is prescribed (e.g. a Green Book business case: go to " + S(5) + " using [[red/amber/green|mech-rag]])"], ["You'll end up with", "A chosen method and scale, explained in a short paragraph"], ["Template", "[[Frame|tpl-frame]] (method section)"], ["Next", S(5)]],
  ["Decide whether you need to match, sequence or select.", "Follow [[Tree 3|t3]] to a method.", "Choose a scale ([[Toolkit A: choosing a scale|tkA-scale]]).", "Write a few sentences explaining the method and why it suits this decision."],
  null,
  "selecting from 20 options with no hard data for most tests, so Tree 3 gives knock-outs then scored criteria. Scores run 0 to 3; price is kept separate so the quality-versus-cost trade-off stays visible.");
STEP(5, "Agree criteria, scores and weights", "Decide how options will be judged before anyone looks at the evidence; rules agreed after seeing results tend to favour a preferred option.",
  [["Skip if", "Criteria, score definitions and weights are already agreed, or your method doesn't score (a money-only quantified tree, a matching decision tree, pros and cons): agree just the knock-outs and go to " + S(6)], ["You'll end up with", "An agreed criteria table with knock-outs, score definitions and weights"], ["Template", "[[Criteria|tpl-criteria]]"], ["Next", S(6)]],
  ["List knock-outs: tests that rule an option out on their own (e.g. no safety certification).",
    "Choose three to seven criteria. For each, write the question it asks and what earns each score; countable definitions are best (\"serves all 6 regions = 3\").",
    "Word every sub-question so \"yes\" is good.", "Check no two criteria measure the same thing, and each is likely to separate the options.",
    "Set weights using [[swing weighting|calc-swing]].", "Write down how scores combine, and get the group to agree all of this before scoring."],
  ["A criterion on which every option scores the same adds nothing but noise. Drop or redefine it."],
  "knock-outs: no cold-chain certification; an unresolved safety notice; fewer than three regions. Criteria: coverage, capability, likely interest, alignment, each 0 to 3. Swing points of 100, 80, 50 and 40 give weights of 37%, 30%, 19% and 15%.");
STEP(6, "Gather the evidence", "Find out what's true about each option, recording where each fact came from and how sure you are.",
  [["Skip if", "Never, though at quick depth one source per criterion is enough"], ["You'll end up with", "An evidence log and a list of open questions"], ["Template", "[[Claims log|tpl-claims]], [[Open questions|tpl-questions]]"], ["Next", S(7)]],
  ["Start with what you have, then primary sources (annual reports, official statistics, the organisation's site), then reputable news and sector bodies.",
    "Record each fact with its source, date and type: fact, the organisation's own claim, your inference, or your estimate.",
    "Give each rating a confidence level: high, medium or low.", "Turn important unknowns into open questions, with who could answer them.",
    "Check cost, time and take-up estimates against how similar projects turned out."],
  ["Don't mark an option down because you couldn't find information. Mark it low confidence and note what its score would be if the gap turned out well."],
  "most evidence comes from the supplier spreadsheet. Unknowns include whether Coldwell Freight has a food-waste commitment.");
STEP(7, "Assess the options", "Apply the method. If a group scores, how you run the session matters as much as the criteria.",
  [["Skip if", "Scores are already agreed (go to " + S(8) + ")"], ["You'll end up with", "Agreed scores for every option, with reasons for any judgement calls"], ["Template", "[[Ratings|tpl-ratings]], [[Decisions log|tpl-log]]"], ["How to run the session", "[[Toolkit D|tkD]]"], ["Next", S(8)]],
  ["Apply knock-outs; list the options removed and why.", "Each person scores privately first, one criterion at a time across all options.",
    "Compare scores; discuss differences on the evidence; score again.", "Record the agreed score and the reason if it differs from what the rules suggest.",
    "Combine scores using the rules from " + S(5) + " ([[weighted score|calc-weighted]])."],
  ["If people disagree widely, the definition is unclear or the evidence thin. Fix that rather than averaging."],
  "three suppliers knocked out. Of the 17 left, Arcline Chilled scores 3.00, top on every criterion; Greenleaf and FreshRoute score 2.33 at the lowest price band.");
STEP(8, "Test the result", "Check the answer is consistent, and ask how easily it could change.",
  [["Skip if", "Never. At quick depth, just ask what single change would alter the top choice"], ["You'll end up with", "A tested result and a short list of open questions that matter"], ["Template", "[[Open questions|tpl-questions]]"], ["Next", `${S(9)}; or back to ${S(6)} if an open question could change the answer and is cheap to settle`]],
  ["Check similar options were scored similarly, and each criterion separated the options.",
    "Drop any option another beats on every criterion ([[dominance|calc-dominance]]), unless it's much cheaper or business as usual.",
    "Work out what would have to change to alter the top choice ([[switching values|calc-switch]]).",
    "If the future is uncertain, compare options under two or three [[scenarios|tkC]].",
    "Rank open questions: could the answer change the choice? How costly is being wrong? How cheap is finding out?"],
  null,
  "no change in weights moves Arcline off the top. If its coverage score were a 2 rather than a 3, it would tie with Evercool, so a site visit must confirm coverage. Two open questions could add new front-runners, so they're chased first.");
STEP(9, "Decide and explain", "Make the choice, and explain it so someone who wasn't in the room can follow and challenge it.",
  [["Skip if", "Never"], ["You'll end up with", "A recommendation with reasons, risks and conditions"], ["Template", "[[Option card|tpl-card]], [[decision quality check|tkC-quality]]"], ["Next", S(10)]],
  ["For the top two or three options, list what could go wrong, how likely, and how serious.", "Imagine it's two years on and the choice has failed: why?",
    "State the preferred option and why it beats each alternative.", "Say what it keeps open, what it rules out, and what would make you revisit it.",
    "Rate the [[decision quality|tkC-quality]] and name its weakest element."],
  null,
  "shortlist Arcline (national) and the Greenleaf–FreshRoute pair (regional). Site visits should test peak-season priority and temperature monitoring. The weakest element is the information: one spreadsheet.");
STEP(10, "Check and present", "Check the work, then present it as a clear argument rather than a data dump.",
  [["Skip if", "Never"], ["You'll end up with", "A checked write-up or deck someone else can follow and verify"], ["Template", "[[Storylines and slide patterns|tkE]]"], ["Next", "Done. Keep the spreadsheet as the record"]],
  ["Re-check every number from the spreadsheet.", "Re-read the sources behind the top options and any knock-outs.", "Check any guidance you relied on is still current.",
    "For important decisions, ask someone who didn't do the work to review it ([[Toolkit D|tkD]]).",
    "Pick the storyline for your type of choice ([[Toolkit E|tkE]]) and write each slide's headline as a full sentence.", "Include a short \"how we worked\" section ([[Toolkit H|tkH]])."],
  null,
  "a five-slide story: how we screened; results; the national-versus-regional trade-off; recommendation and open questions; what site visits should test. One page per front-runner in an appendix.");

// ======================= TOOLKIT =======================
H1("The Toolkit", "toolkit");
T(["Section", "Contains"], [["[[Toolkit A|tkA]]", "Assessment methods (including quantified decision trees), and choosing a scale"], ["[[Toolkit B|tkB]]", "Calculations, explained with examples"], ["[[Toolkit C|tkC]]", "Handling uncertainty; decision quality check"],
  ["[[Toolkit D|tkD]]", "Running group sessions; checking your work"], ["[[Toolkit E|tkE]]", "Presenting: storylines and slide patterns"], ["[[Toolkit F|tkF]]", "Templates"],
  ["[[Toolkit G|tkG]]", "Rulebooks: UK, US, everyone else"], ["[[Toolkit H|tkH]]", "Where the methods come from"], ["[[Toolkit I|tkI]]", "Glossary"]], [2, 8]);

H2("Toolkit A: Assessment methods", "tkA", true);
H3("Choosing a scale", "tkA-scale");
T(["Scale", "Works best for", "Watch out for"], [
  ["Red / amber / green", "Pass-or-fail tests; public-sector audiences", "Define amber, or it becomes a catch-all"],
  ["Scores of 0 to 3", "Ranking many options on a few criteria", "Small differences in totals look more precise than they are"],
  ["One to three stars", "Five to eight options compared visually", "Say how the stars were used to choose"],
  ["✓ / – / ✗ / ?", "Building a rating from short statements", "Needs agreed rules for combining ([[factor rating|calc-rag]])"],
  ["0 to 100, best to worst", "Formal weighted analysis, including Green Book long lists", "80 isn't \"twice as good\" as 40"]], [2.4, 4, 3.6]);
const MECH = (name, anchor, use, how, watch) => { H3(name, anchor); T(null, [["Use it when", use], ...(watch ? [["Watch out", watch]] : [])], [2, 8], { shadeFirst: true }); N(how); };
MECH("Threshold filter", "mech-threshold", "Many options (about 20+) and measurable data; you need to cut quickly to a shortlist",
  ["Remove options excluded for other reasons, saying why.", "For each criterion, set a measure and a minimum (\"at least one of these\" is fine).",
    "Look at the spread of data first; anchor thresholds to something real, like break-even size.", "Apply filters in order, most fundamental first, counting survivors at each.",
    "Check how many pass if each threshold moves a little ([[threshold sensitivity|calc-threshold]])."], "An option just below a threshold may be better overall than one just above. Report near-misses");
MECH("Scored criteria", "mech-scored", "Ranking organisations, places or segments on a handful of criteria, with judgement as well as data",
  ["Apply knock-outs; don't score excluded options.", "Score 0 to 3 (or stars) against the written definitions, with evidence and a confidence level.",
    "Combine with a [[weighted score|calc-weighted]].", "Rank, then group into tiers with stated cut-offs.", "If options fall into types, show rankings within each type too."], "Use tiers, not decimal places");
MECH("Red/amber/green against success factors", "mech-rag", "Options must pass tests to stay in and the result must be defensible; the UK Green Book's method for narrowing a long list",
  ["Agree the success factors (the Green Book's five: strategic fit, value for money, supplier capacity, affordability, achievability; add local ones only if needed).",
    "Break each into four to eight statements worded so \"yes\" is good; mark the deal-breakers.", "Mark each statement ✓, ✗, – or ? for each option.",
    "Turn marks into ratings ([[factor rating|calc-rag]]).", "Apply strategic fit first; options failing it are dropped before the rest are rated."], "Use ? and a provisional flag for unknowns, not amber");
MECH("Impact and availability matrix", "mech-matrix", "Many activities to sequence, based on what you can do",
  ["Score impact 1 to 3 from countable evidence (e.g. how many stakeholders asked for it).", "Score availability 1 to 3: the average of difficulty, dependency, capacity and in-house skills.",
    "Plot on a 3 by 3 grid (zones below).", "Before plotting, remove internal tasks and out-of-scope items, saying why."], "If everything lands in one or two columns, that axis isn't separating anything. Supporting method only: for standalone prioritisation, treat the result as a first pass");
T(["", "Low availability", "High availability"], [["**High impact**", "Longer-term roadmap", "Priorities now"], ["**Low impact**", "Hand over or drop", "Easy extras (not priorities)"]], [2, 4, 4]);
MECH("Eisenhower matrix", "mech-eis", "Sorting work by what you must do",
  ["Define \"urgent\" (deadline, legal requirement, commitment) and \"important\" (serves agreed objectives) in writing.", "Sort into the four boxes below."], null);
T(["", "Not urgent", "Urgent"], [["**Important**", "Schedule it", "Do now"], ["**Not important**", "Drop it", "Delegate it"]], [2, 4, 4]);
MECH("Responsibility mapping", "mech-raci", "A new or changing team needs to know who does what today",
  ["List activities as verb plus object (\"qualify sales leads\").", "For each activity and organisation mark A (accountable), AD (accountable and delivers), D (delivers) or S (supports).",
    "Read the patterns (table below) and decide an action for each activity."], "Supporting method only: it informs scope and structure choices; a standalone activity analysis needs fuller process and capacity work");
T(["Pattern", "Likely issue", "Action"], [["Nobody involved", "Gap", "Create a remit"], ["Several accountable", "Unclear ownership", "Confirm who owns it"], ["Delivered, nobody accountable", "Unclear ownership", "Confirm who owns it"],
  ["Accountable, nobody delivers", "Under-investment", "Add people"], ["Several delivering", "Duplication: useful or wasteful?", "Signpost or redistribute"], ["Serves no objective", "Unnecessary", "Stop"]], [3.3, 3.3, 3.4]);
MECH("Decision tree (matching options to situations)", "mech-tree", "The right option depends on each case, and conditions emerge over time",
  ["Describe each option in the same format.", "Find the fewest yes/no questions that separate the options; order them by when the answer becomes known.",
    "Mark red lines (conditions that force a branch); drop options that are your red lines.", "Where no red line decides, weigh what pushes you towards an option against what pulls the other party.",
    "Optional: if you can put rough odds on how often each situation comes up, or on what each option is worth, add them and treat it as a [[quantified decision tree|mech-qtree]]."], null);
MECH("Quantified decision tree", "mech-qtree", "A few uncertain events drive the result, or the choice comes in stages: pilot, phase, wait, test first",
  ["List the options, including doing nothing and stopping at each later decision.", "Draw decisions (squares) and uncertain events (circles) left to right in the order they happen; put each decision after whatever you'll know by then.",
    "Give each event's outcomes probabilities that add to 1, each with its source and a low and high value. Start from how similar cases turned out.",
    "Put a value on each end point. Enter each cost once, where it happens; leave out money already spent.",
    "[[Fold back|calc-fold]] from right to left. Read off the strategy: what to do now and at each later decision.",
    "Show the risk profile (every result with its probability), find the [[break-even|calc-breakeven]] values, and work out what any study is worth ([[value of a test|calc-evsi]])."],
  "The expected value is an average, not a forecast: show the risk profile beside it. If one bad result would be too much to bear, see [[certainty equivalent|calc-ce]]");
P("**Example (invented).** A national roll-out is worth +900 if it succeeds and −400 if it fails (£k); similar launches succeeded 40% of the time. A regional pilot costs 40. Of comparable pilots, 80% of eventual successes went well, and 30% of eventual failures did too. The pilot-first strategy is worth 176 against 120 for rolling out now: pilot, roll out only if it goes well. Its results: +860 (32%), −40 (50%), −440 (18%).");
IMG("qtree.png", 1113, 578, 300);
MECH("Pros and cons", "mech-proscons", "One design choice with two to four options",
  ["Say which consideration matters most.", "Remove options that break a firm principle.", "List pros and cons of similar length for each.",
    "Label options Preferred, Do minimum, Do nothing or Alternative ([[option card|tpl-card]]).", "Say how reversible it is; set a review date if easy to change."], null);

H2("Toolkit B: Calculations", "tkB", true);
P("Each works in an ordinary spreadsheet.");
const CALC = (name, a, what, how) => { H3(name, a); T(null, [["What it does", what], ["How", how]], [2, 8], { shadeFirst: true }); };
CALC("Swing weights", "calc-swing", "Turns judgements about what matters into weights that add to 100%", "Give the most valuable worst-to-best improvement 100 points; rate the others against it (say 80, 50, 40); divide each by the total (270). Coverage = 100 ÷ 270 = 37%");
CALC("Weighted score", "calc-weighted", "Combines criterion scores into one number", "Multiply each score by its weight and add: (3 × 37%) + (3 × 30%) + (1 × 19%) + (3 × 15%) = 2.63 out of 3");
CALC("Factor rating (red/amber/green)", "calc-rag", "Turns ✓/✗ marks into a rating", "Red if any deal-breaker is ✗. Otherwise (ticks − crosses) ÷ statements answered; 0.4 or more is green. ✓✓✓–✗ gives (3 − 1) ÷ 5 = 0.4: green. Overall: red if any factor is red; otherwise green if at least half the factors are green. These thresholds are our defaults; adjust them");
CALC("Rescaling to 0–100", "calc-rescale", "Puts criteria in different units on one scale", "(value − worst) ÷ (best − worst) × 100");
CALC("Dominance", "calc-dominance", "Finds options you can drop", "If A is at least as good as B on every criterion and better on one, drop B (unless it's much cheaper or business as usual)");
CALC("Value for money", "calc-value", "Compares quality and price with price kept separate", "Keep options where nothing else is both cheaper (or the same) and better");
CALC("Switching value", "calc-switch", "Shows what the answer depends on", "How far would a score or weight have to move to change the top choice? If the leader is 0.37 ahead and a criterion weighs 37%, its score would have to fall by 0.37 ÷ 0.37 = 1 point");
CALC("Expected value", "calc-ev", "Average outcome across scenarios, weighted by likelihood", "60% chance of +10, 40% chance of −5: 0.6 × 10 + 0.4 × (−5) = 4. It's the long-run average, not what will happen this time");
CALC("Folding back a tree", "calc-fold", "Finds the best strategy in a [[quantified decision tree|mech-qtree]]", "Work right to left. At a circle, take the expected value of its branches; at a square, take the best branch and cross out the rest. Roll-out example: roll out after a good pilot = 0.64 × 900 − 0.36 × 400 = 432; after a poor pilot, stop (0); pilot first = 0.5 × 432 + 0.5 × 0 − 40 = 176");
CALC("Value of perfect information", "calc-voi", "The most it's worth paying to remove an uncertainty", "Average result if you always knew the outcome first, minus the expected value of your best choice now. Roll-out example: 0.4 × 900 = 360 with foresight, minus 120 now = 240. No study can be worth more");
CALC("Tree flip (updating a probability)", "calc-flip", "Turns a test's track record into what you need: the chance of each result, and the probability of the truth after it", "1. Prior × track record for each pair: success and good pilot 0.4 × 0.8 = 0.32; failure and good pilot 0.6 × 0.3 = 0.18. 2. Add them: chance of a good pilot = 0.50. 3. Divide: chance of success after a good pilot = 0.32 ÷ 0.50 = 0.64. Watch rare events: with a 5% prior, a test that catches 90% and wrongly flags 10% is right only 0.045 ÷ 0.14 = 32% of the time it flags");
CALC("Value of a test or study", "calc-evsi", "Whether a pilot, survey or study is worth its cost", "Expected value with the test (before its cost), minus expected value without it. Roll-out example: 0.5 × 432 + 0.5 × 0 = 216, minus 120 = 96. Buy it if it costs less than 96. If every result would lead to the same action, it's worth nothing");
CALC("Value of keeping options open", "calc-option", "Whether a flexible version (pilot, phase, wait) is worth it", "Expected value of the flexible version minus the rigid one, both from the same tree: 176 − 120 = 56 for piloting first");
CALC("Which risky step first", "calc-order", "Several pass/fail hurdles, any failure sends you to a fallback", "Do first the one with the lowest cost ÷ chance of failing (100 ÷ 0.2 = 500 beats 300 ÷ 0.4 = 750). But if a late failure costs more (less time for the fallback), the step most likely to fail may belong first. Work out every order in a tree");
CALC("Certainty equivalent", "calc-ce", "Allowing for risk when one bad result would hurt", "Risk tolerance R = the size of 50–50 bet (win R, lose R/2) you'd just accept. For each result x, U = 1 − e^(−x/R); average U by probability; certainty equivalent = −R × ln(1 − average U). A 50–50 bet of +3 or −1 (EV 1) is worth about 0.13 to someone with R = 2");
CALC("Regret", "calc-regret", "How much worse an option does than the best one in the same scenario", "Best city earns 3.8 if funding is cut; yours earns 2.0; regret 1.8. Prefer the option whose worst regret is smallest");
CALC("Break-even probability", "calc-breakeven", "When one option overtakes another", "Find the value of an input at which both options have the same expected value: \"A beats B only if the good scenario is over 55% likely\". Try a range of values in a table and note where the best option changes");
CALC("Threshold sensitivity", "calc-threshold", "Shows whether a cut-off is doing too much work", "Recount passes with each threshold 10–20% looser and tighter");

H2("Toolkit C: Handling uncertainty", "tkC", true);
T(["Tool", "Use it when", "How"], [
  ["Keep options open", "The future is uncertain and the choice is hard to undo", "Prefer options you can pilot, phase, expand or exit; say what each keeps open and rules out"],
  ["Route with triggers", "You want to start small and grow", "Agree in advance what would trigger the next step, how long it takes, and who watches for it"],
  ["Scenarios", "A few plausible futures would change the answer", "Describe two or three futures; prefer options that do acceptably in all ([[regret|calc-regret]])"],
  ["Pilot first", "Analysis can't answer it yet ([[Tree 2|t2]], question 4)", "Run a small, time-limited trial with success measures agreed in advance; then appraise"],
  ["Reality check", "You have cost, time or take-up estimates", "Compare with how similar projects actually turned out"],
  ["Pre-mortem", "Before committing", "Imagine it's failed two years on; list why; add safeguards"]], [2, 3.5, 4.5]);
H3("Decision quality check", "tkC-quality");
T(["Element", "Ask", "High / medium / low"], [["Frame", "Right problem, right scope?", ""], ["Alternatives", "Genuinely different options, including doing nothing?", ""], ["Information", "Reliable and sourced?", ""],
  ["Values", "Criteria and weights agreed before scoring?", ""], ["Reasoning", "Numbers right; robustness tested?", ""], ["Commitment", "Decision-makers ready to act?", ""]], [2, 6, 2]);
P("The decision is only as strong as its weakest element.");

H2("Toolkit D: Group sessions and checking your work", "tkD", true);
H3("Running a scoring session");
N(["Agree criteria, score definitions and combining rules first.", "Share an evidence pack per option beforehand.", "Each person scores privately, one criterion at a time.",
  "Show the spread; discuss differences on evidence, not seniority.", "Score again; record agreed scores and reasons.", "Only then judge the overall picture."]);
T(["If the group overrules the calculated result by…", "It needs"], [["One step (e.g. amber to green)", "A sentence explaining why"], ["Two steps (red to green)", "Evidence: a document, legal view or precedent"], ["Repeatedly, in the same direction", "A change to the rules or weights, made openly"]], [5, 5]);
H3("Checking your work");
T(["Check", "How"], [["Sources", "Every fact has one; otherwise label it as inference or unknown"], ["Numbers", "Re-check each against the spreadsheet"], ["Key sources", "Re-read those behind the top options and any knock-outs"],
  ["Currency", "Confirm guidance is current; date-stamp it"], ["Uncertainty", "Show confidence next to scores, ranges for estimates, open questions"], ["Independent review", "For important decisions, by someone who didn't do the work"]], [2.5, 7.5]);

H2("Toolkit E: Presenting the result", "tkE", true);
T(["Layer", "What it is", "Analogy"], [["Storyline", "The argument: which points, in what order, lead to your recommendation", "The chapter list"], ["Slide pattern", "The standard layout for making one point", "How each chapter is laid out"]], [2, 5.5, 2.5]);
B(["Pick the storyline for your type of choice below; each row names the pattern to use.", "Open with a one-sentence answer and close with \"how we worked\".",
  "Write headlines as full sentences that make a point (\"One national carrier leads on every criterion\"), not labels (\"Results\")."]);
const STORY = (name, rows) => { H3(name); T(["#", "What the slide says", "Pattern"], rows, [0.8, 5.6, 3.6]); };
STORY("Who: partners and suppliers", [["1", "The answer and how we got there", "Executive summary"], ["2", "Where the options came from", "Long list by source"], ["3", "How we judged them", "Criteria with score definitions"], ["4", "The front-runners", "Ranked table with tiers"], ["5", "The trade-offs", "Value for money view; pros and cons"], ["6", "What we still need to know", "Open questions table"], ["7", "How we worked", "How we worked"], ["App.", "Each front-runner; exclusions", "One page per option"]]);
STORY("Where: locations", [["1", "The answer", "Executive summary"], ["2", "How we judged places", "Criteria (or threshold) table"], ["3", "How the list narrowed", "Funnel with counts, and a map"], ["4", "How the shortlist compares", "Star grid; value for money view"], ["5", "How it holds up in different futures", "Scenario table"], ["6", "Our recommendation and route", "Route with triggers"], ["7", "How we worked", "How we worked"]]);
STORY("What: activities", [["1", "The answer", "Executive summary"], ["2", "Who does what today", "Responsibility heatmap"], ["3", "Gaps and overlaps", "Issue and action table"], ["4", "How we narrowed the list", "Waterfall"], ["5", "What to do first", "Plotted matrix"], ["6", "How it phases", "Roadmap"], ["7", "How we worked", "How we worked"]]);
STORY("Structure: organisational form", [["1", "The answer", "Executive summary"], ["2", "What a good answer must do", "Principles table"], ["3", "The options considered", "Long-list family tree"], ["4", "How we tested them", "Success factors and rating rules"], ["5", "Where each dropped out", "Drop-out tracker"], ["6", "The short list", "Summary ratings table"], ["7", "Why the preferred option", "Case against each alternative"], ["8", "How we worked", "How we worked"]]);
STORY("Structure by situation; scope; design choices", [["1", "The models (or scope lines) available", "Model comparison table / scope spectrum"], ["2", "How to choose between them", "Decision tree / option cards"], ["3", "The answer on one page", "Answer on a page"], ["4", "How we worked", "How we worked"]]);
H3("Slide patterns");
T(["Pattern", "What it shows", "Use it when"], [
  ["Executive summary", "Answer, reasons, what you need from the reader", "Always, first"], ["Principles table", "Principle, issue, implication", "Agreeing what good looks like"],
  ["Long list by source / family tree", "All options, grouped, with early exclusions", "Showing you looked widely"], ["Criteria with score definitions", "Each criterion, weight, what earns each score", "Before any results"],
  ["Threshold table and funnel", "Tests, minimums, survivors at each step", "Filtering a long list"], ["Ranked table with tiers", "Options in order with scores, confidence, tier", "Selecting from a set"],
  ["Star grid", "Stars per criterion for a few options", "Five to eight options"], ["Value for money view", "Score against price; best-value options picked out", "Price kept separate"],
  ["Success factors and rating rules", "Tests, statements, combining rules", "Red/amber/green appraisals"], ["Drop-out tracker", "Where each option stopped", "Long list to short list"],
  ["Summary ratings table", "Options by factor, with overall rating", "Red/amber/green appraisals"], ["Responsibility heatmap", "Who's accountable, delivers, supports", "Mapping who does what"],
  ["Waterfall", "How a list grew and shrank, with a rule per change", "Explaining exclusions"], ["Plotted matrix", "Activities on a grid with zones", "Prioritising activities"],
  ["Scenario table", "Each option in each future, worst shortfall", "Uncertain futures"], ["Route with triggers", "Now, next trigger, who watches", "Staged recommendations"],
  ["Decision tree", "Questions in answer order, leading to options", "Matching options to situations"], ["Case against each alternative", "Why the preferred beats each, risks that remain", "The recommendation"],
  ["Option cards", "Two to four labelled options with pros and cons", "Small design choices"], ["Open questions table", "Unknowns, whether they matter, who's finding out", "Always, near the end"],
  ["One page per option", "Same fields for every option", "Appendix"], ["How we worked", "Methods, sources, our judgement calls", "Always, near the end"]], [2.8, 4, 3.2]);

H2("Toolkit F: Templates", "tkF", true);
P("Each template is a tab in your spreadsheet.");
const TPL = (name, a, when, step, headers, widths) => { H3(name, a); P(`**Use it when** ${when} (${step}).`); T(headers, [headers.map(() => ""), headers.map(() => "")], widths); };
TPL("Frame", "tpl-frame", "starting any appraisal; keep it to one page", S(1) + ", " + S(2) + ", " + S(4), ["Decision", "Decided by, when", "Need (no solution named)", "Decided / now / later", "Method base, depth, defensibility, method"], [2, 1.6, 2.2, 2, 2.2]);
TPL("Principles", "tpl-principles", "the group needs to agree what any good answer must respect", S(1), ["Process or result?", "Principle", "Issue it addresses", "What it implies"], [1.8, 3, 2.6, 2.6]);
TPL("Options", "tpl-options", "building the long list; number once, never renumber", S(3), ["No.", "Option", "Family", "Source", "Ruled out early? Why?"], [0.7, 3, 1.8, 2, 2.5]);
TPL("Criteria", "tpl-criteria", "agreeing how to judge options, before scoring", S(5), ["Criterion and question", "Weight", "Score 3 (best)", "Score 2", "Score 1", "Score 0 (worst)", "Deal-breaker?"], [2.4, 0.9, 1.6, 1.4, 1.4, 1.4, 1]);
TPL("Ratings", "tpl-ratings", "recording scores; one row per option per criterion", S(7), ["Option", "Criterion", "Suggested", "Agreed", "Reason if different", "Evidence", "Source", "Confidence"], [1.3, 1.3, 1, 1, 1.6, 1.7, 1.2, 1]);
TPL("Claims log", "tpl-claims", "evidence comes from research and needs checking", S(6) + ", " + S(10), ["Claim (one fact)", "Fact, claim, inference or estimate?", "Source", "Date", "Confidence", "Checked by"], [3, 1.6, 2, 1, 1.1, 1.3]);
TPL("Open questions", "tpl-questions", "something you don't know could matter", S(6) + ", " + S(8), ["Question", "Could it change the answer?", "Cost of being wrong", "Cost to find out", "Who, how, by when"], [3, 1.7, 1.5, 1.5, 2.3]);
TPL("Option card", "tpl-card", "presenting a small design choice", S(9), ["Label", "Option in one line", "Pros", "Cons", "Keeps open / rules out"], [1.8, 2.2, 2, 2, 2]);
TPL("Inputs for a quantified tree", "tpl-inputs", "building a [[quantified decision tree|mech-qtree]]; every number in the tree refers to this table", S(6) + ", " + S(8), ["Input", "Central value", "Low", "High", "Source or basis", "Owner"], [2.2, 1.3, 1, 1, 3, 1.5]);
TPL("Tree flip", "tpl-flip", "a test, pilot or study is fallible and you need probabilities after its result", S(8), ["Truth", "Prior", "P(result A | truth)", "Prior × that", "P(truth | result A)"], [2, 1.5, 2.2, 2, 2.3]);
TPL("Decisions log", "tpl-log", "any group is involved; it's the audit trail", S(7), ["Date", "Decision", "Agreed by", "Evidence", "What it replaced"], [1.2, 3.5, 1.5, 2, 1.8]);

H2("Toolkit G: Rulebooks", "tkG", true);
T(["", "UK central government", "US federal government", "Everyone else"], [
  ["Guidance", "HM Treasury Green Book (2026 edition)", "OMB Circular A-94 (1992 version, reinstated 2025); A-4 (2003) for regulations; GAO best practices", "The general method: the best of both"],
  ["Building options", "Five kinds of choice: scope, solution, delivery, implementation, funding", "Vary scale, method of provision and degree of government involvement", "Either approach"],
  ["Narrowing", "Red/amber/green against five success factors; strategic fit as a gate", "Criteria agreed before analysis", "Success factors with a strategic-fit gate"],
  ["Weighted scoring", "Long list only, if ratings don't settle it; swing weights; trained facilitator; no simple points tables", "Allowed; criteria and weights set in advance", "Allowed at any stage; swing weights recommended"],
  ["Benchmark", "Business as usual, always on the short list", "Status quo, always included", "Business as usual"],
  ["Short list", "Business as usual, do minimum, preferred, more and less ambitious; costed analysis", "Net present value at 7% real (base case) with sensitivity", "Costed comparison where possible, at your own cost of capital"],
  ["Must also", "Optimism-bias adjustment; switching values; statutory duties", "Whole-life costs; one document; independent review", "Your own legal duties and policies; independent review for big decisions"]], [1.6, 2.9, 2.9, 2.6]);
P("Guidance changes. Check current versions on gov.uk, whitehouse.gov and gao.gov before formal use.");

H2("Toolkit H: Where the methods come from", "tkH", true);
T(["Method or idea", "Source"], [
  ["Options appraisal, success factors, business as usual, five kinds of choice", "HM Treasury, The Green Book (2026)"],
  ["Swing weighting; rules on weighted scoring", "HM Treasury Green Book supplementary guidance on multi-criteria decision analysis (2024); Analysis Function, Introductory Guide to MCDA"],
  ["Valuing flexibility; routes with triggers", "HM Treasury Green Book supplementary guidance, Accounting for the effects of climate change"],
  ["US federal analysis", "OMB Circulars A-94 and A-4; GAO Cost Estimating and Assessment Guide"],
  ["\"Where to play\" before \"how to win\"", "Lafley and Martin, Playing to Win (2013)"],
  ["Reversible and irreversible decisions", "Jeff Bezos, Amazon shareholder letters (2015, 2016)"],
  ["Problems that analysis can't yet answer", "Snowden and Boone, Harvard Business Review (2007), the Cynefin framework"],
  ["Decision quality's six elements", "Spetzler, Winter and Meyer, Decision Quality (2016)"],
  ["Value of information", "Decision analysis (Raiffa; Howard); Hubbard, How to Measure Anything"],
  ["Quantified decision trees, folding back, risk profiles, tree flip (Bayes' rule)", "Howard Raiffa, Decision Analysis (1968); standard management-science texts"],
  ["Risk tolerance and certainty equivalents", "Ronald Howard, \"Decision analysis: practice and promise\", Management Science (1988)"],
  ["Regret; good enough in every future", "Savage; Simon; Marchau et al., Decision Making under Deep Uncertainty (2019)"],
  ["Musts before wants; what could go wrong", "Kepner and Tregoe, The Rational Manager (1965)"],
  ["Private scoring before discussion", "Kahneman, Sibony and Sunstein, Noise (2021)"],
  ["Pre-mortem", "Gary Klein, Harvard Business Review (2007)"],
  ["Reality-checking estimates", "Kahneman and Tversky; Flyvbjerg (reference-class forecasting)"],
  ["Eisenhower matrix", "Attributed to Eisenhower; popularised by Stephen Covey"],
  ["Accountable / delivers / supports", "Adapted from RACI matrices"],
  ["Impact and availability; the red/amber/green thresholds; the six issue types", "Our own practice, from real appraisals; thresholds calibrated on one working group's ratings"]], [4.5, 5.5]);

H2("Toolkit I: Glossary", "tkI", true);
T(["Term", "Meaning"], [["Business as usual", "What happens if nothing changes; the benchmark"], ["Success factor", "A test every acceptable option must pass"], ["Deal-breaker", "A statement that, if \"no\", fails the whole factor"],
  ["Knock-out", "A condition that excludes an option before scoring"], ["Long list / short list", "All reasonable options / the few compared in detail"], ["Swing weighting", "Weights set by how much the worst-to-best difference matters"],
  ["Switching value", "How far an input must move to change the recommendation"], ["Regret", "How much worse an option does than the best in the same scenario"], ["Value of information", "How much it's worth knowing something before deciding"], ["Expected value", "The probability-weighted average result"], ["Risk profile", "Every possible result of an option with its probability"],
  ["Tree flip", "Updating a probability using a test's track record (Bayes' rule)"], ["Certainty equivalent", "The sure amount you'd accept instead of a risky option"],
  ["Pre-mortem", "Imagining failure to find the likely reasons in advance"], ["Multi-criteria analysis", "Formal weighted scoring"], ["Cost-benefit analysis", "Comparing options in money terms"]], [3, 7]);
P("Guidance summaries reflect sources checked in November 2026. Not legal, financial or regulatory advice.", { spacing: { before: 300 } });

// ======================= DOC =======================
const missing = [...used].filter(a => !anchors.has(a));
if (missing.length) { console.error("MISSING ANCHORS:", missing); process.exit(1); }
const numbering = { config: [{ reference: "bul", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 270 } } } }] }] };
for (let i = 1; i <= nc; i++) numbering.config.push({ reference: "num" + i, levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 300 } } } }] });
const doc = new Document({
  creator: "Choosewell", title: "Choosewell: a step-by-step guide", features: { updateFields: true },
  styles: {
    default: { document: { run: { font: FONT, size: 20 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 34, bold: true, color: NAVY }, paragraph: { spacing: { before: 240, after: 160 }, keepNext: true, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 27, bold: true, color: NAVY }, paragraph: { spacing: { before: 220, after: 110 }, keepNext: true, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 22, bold: true }, paragraph: { spacing: { before: 160, after: 80 }, keepNext: true, outlineLevel: 2 } }]
  },
  numbering,
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: "Choosewell guide  |  ", font: FONT, size: 16, color: "777777" }), new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 16, color: "777777" })] })] }) },
    children: out
  }]
});
Packer.toBuffer(doc).then(b => { fs.writeFileSync(OUT, b); console.log("ok; links:", used.size, "anchors:", anchors.size); });
