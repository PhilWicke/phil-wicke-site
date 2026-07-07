"""Generate final/activity.html, final/service.html and final/teaching.html from the captured
old_site/*.md, in the site's visual language. Activity entries are re-linked from the captured link
list. Teaching combines the teaching record with invited-lecture / Interdisciplinary College entries
from the timeline. Re-runnable.  Run: uv run python pipeline/build_archives.py"""
import re, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
OLD = ROOT/"old_site"
OUT = ROOT/"final" if (ROOT/"final").exists() else ROOT   # working repo serves from final/, the public repo from its root

TPL = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} · Philipp Wicke</title>
<meta name="robots" content="{robots}">
<link rel="icon" type="image/svg+xml" href="assets/favicon.svg">
<link rel="icon" type="image/png" sizes="32x32" href="assets/favicon-32.png">
<link rel="apple-touch-icon" href="assets/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Newsreader:ital,opsz,wght@0,6..72,400..600;1,6..72,400&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
:root{{--ink:#1a1b22;--accent:#3b4ea0;--paper:#f7f8fb;--ink-soft:#474b57;--ink-mute:#5f6478;--rule:#d2d8e6;--rule-soft:#e6eaf3;--line:#2a3666;}}
*{{box-sizing:border-box;margin:0;padding:0;}}
html{{scroll-behavior:smooth;}}
body{{font-family:"IBM Plex Mono",ui-monospace,monospace;background:var(--paper);color:var(--ink);-webkit-font-smoothing:antialiased;}}
a{{color:inherit;}}
.bar{{position:sticky;top:0;z-index:10;background:rgba(247,248,251,.85);-webkit-backdrop-filter:blur(10px);backdrop-filter:blur(10px);border-bottom:1px solid var(--line);}}
.bar .row{{max-width:1000px;margin:0 auto;padding:0 clamp(20px,4vw,48px);height:50px;display:flex;align-items:center;justify-content:space-between;}}
.bar a.back{{font-size:11.5px;letter-spacing:.14em;text-transform:uppercase;text-decoration:none;}}
.bar a.back:hover{{color:var(--accent);}}
.bar .pg{{font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--ink-mute);}}
.wrap{{max-width:1000px;margin:0 auto;padding:0 clamp(20px,4vw,48px);}}
.head{{padding:clamp(34px,6vw,60px) 0 4px;}}
.head .kick{{font-size:11.5px;letter-spacing:.16em;text-transform:uppercase;color:var(--accent);}}
.head h1{{font-family:"Instrument Serif",serif;font-weight:400;font-size:clamp(38px,7vw,72px);line-height:1;margin:6px 0 0;letter-spacing:.005em;color:var(--line);}}
.head p{{margin:14px 0 0;font-family:"Newsreader",Georgia,serif;font-size:15px;color:var(--ink-soft);line-height:1.55;max-width:64ch;}}
.head p a{{color:var(--accent);}}
.grp{{border-top:2px solid var(--line);border-image:linear-gradient(90deg,var(--line) 55%,rgba(42,54,102,.25) 85%,transparent 100%) 1;margin-top:30px;}}
.grp .gh{{font-size:13px;font-weight:500;color:var(--accent);padding:12px 0 4px;letter-spacing:.04em;}}
.e{{display:grid;grid-template-columns:104px 1fr auto;gap:16px;align-items:baseline;padding:11px 0;border-top:1px solid var(--rule-soft);}}
.e:first-of-type{{border-top:0;}}
.e .mo{{font-size:10.5px;letter-spacing:.07em;text-transform:uppercase;color:var(--ink-mute);padding-top:3px;}}
.e .d{{font-family:"Instrument Serif",serif;font-size:16.5px;line-height:1.32;color:var(--ink);}}
.e .d a{{color:var(--accent);text-decoration:none;border-bottom:1px solid rgba(59,78,160,.32);}}
.e .d a:hover{{border-bottom-color:var(--accent);}}
.e .ty{{font-size:9px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-mute);border:1px solid var(--rule);padding:2px 7px;white-space:nowrap;align-self:start;margin-top:3px;}}
.pub{{display:grid;grid-template-columns:1fr auto;gap:22px;padding:15px 0;border-top:1px solid var(--rule-soft);align-items:start;}}
.pub:first-of-type{{border-top:0;}}
.pub-t{{font-family:"Instrument Serif",serif;font-size:18px;line-height:1.28;color:var(--ink);text-decoration:none;border-bottom:1px solid rgba(59,78,160,.28);}}
.pub-t:hover{{color:var(--accent);border-bottom-color:var(--accent);}}
.pub-au{{font-family:"Newsreader",Georgia,serif;font-size:13.5px;color:var(--ink-mute);margin-top:5px;line-height:1.45;}}
.pub-au b{{color:var(--ink-soft);font-weight:600;}}
.pub-ex{{font-family:"Newsreader",Georgia,serif;font-size:14px;line-height:1.5;color:var(--ink-soft);margin-top:7px;max-width:74ch;}}
.pub-cit{{font-family:"IBM Plex Mono",monospace;text-align:right;white-space:nowrap;padding-top:4px;}}
.pub-cit b{{font-size:13px;color:var(--ink-soft);font-weight:500;}}
.pub-cit span{{display:block;font-size:8px;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-mute);margin-top:1px;}}
.grp p{{font-family:"Newsreader",Georgia,serif;font-size:14.5px;line-height:1.6;color:var(--ink-soft);padding:9px 0 3px;max-width:80ch;}}
.grp p a{{color:var(--accent);}}
.grp p b{{color:var(--ink);font-weight:500;}}
.foot a{{color:var(--ink-mute);border-bottom:1px solid var(--rule);}}.foot a:hover{{color:var(--accent);border-bottom-color:var(--accent);}}
@media (max-width:620px){{.pub{{grid-template-columns:1fr;}}.pub-cit{{text-align:left;padding-top:2px;}}}}
@media print{{
  .bar,.foot{{display:none;}}
  body{{background:#fff;color:#000;}}
  .head{{padding-top:0;}}
  .head h1,.pub-t,.e .d{{color:#000;}}
  .grp{{border-image:none;border-top:1.5pt solid #000;}}
  .grp .gh{{color:#000;}}
  .pub,.e{{break-inside:avoid;}}
  .pub-t{{border-bottom:0;}}
  a{{color:#000;text-decoration:none;border-bottom:0 !important;}}
  .pub-au,.pub-ex,.e .mo{{color:#333;}}
  .head .kick{{color:#333;}}
  .head p a,.grp p a,.e .d a{{color:#000;}}
}}
.foot{{margin-top:60px;border-top:2px solid var(--line);}}
.foot .row{{max-width:1000px;margin:0 auto;padding:20px clamp(20px,4vw,48px);font-size:10.5px;letter-spacing:.07em;text-transform:uppercase;color:var(--ink-mute);display:flex;justify-content:space-between;flex-wrap:wrap;gap:12px;}}
@media (max-width:620px){{.e{{grid-template-columns:1fr auto;}}.e .mo{{grid-column:1/-1;}}}}
</style>
</head>
<body>
<header class="bar"><div class="row"><a class="back" href="index.html">&larr; Philipp Wicke</a><span class="pg">{title}</span></div></header>
<main class="wrap">
<div class="head"><div class="kick">{kick}</div><h1>{h1}</h1><p>{intro}</p></div>
{body}
</main>
<footer class="foot"><div class="row"><span>Philipp Wicke, Berlin</span><span><a href="imprint.html">Impressum</a> &middot; &copy; 2026</span></div></footer>
</body>
</html>
'''

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def block(md, start, end="## Links"):
    lines = (OLD/md).read_text(encoding="utf-8").split("\n")
    out, on = [], False
    for ln in lines:
        s = ln.strip()
        if s == start:
            on = True; continue
        if s.startswith(end):
            break
        if on and s:
            out.append(s)
    return out

def parse_links(md):
    """anchor -> url from the '## Links' section; skip profile/redirect anchors that are URLs."""
    pairs, on = [], False
    for ln in (OLD/md).read_text(encoding="utf-8").split("\n"):
        s = ln.strip()
        if s.startswith("## Links"): on = True; continue
        if not on: continue
        m = re.match(r"^- \[(.+?)\]\((.+?)\)\s*$", s)
        if m:
            text, url = m.group(1).strip(), m.group(2).strip()
            if len(text) >= 6 and not text.lower().startswith("http") and "learn more" not in text.lower():
                pairs.append((text, url))
    pairs.sort(key=lambda p: -len(p[0]))   # match longer (more specific) anchors first
    return pairs

def link_desc(desc, links):
    """Wrap any link-anchor phrases occurring in desc, non-overlapping; escape the rest."""
    spans = []
    for anchor, url in links:
        i = desc.find(anchor)
        if i >= 0: spans.append((i, i + len(anchor), url, anchor))
    spans.sort(key=lambda s: (s[0], -(s[1]-s[0])))
    chosen, end = [], -1
    for s in spans:
        if s[0] >= end: chosen.append(s); end = s[1]
    out, pos = [], 0
    for s, e, url, anchor in chosen:
        out.append(esc(desc[pos:s]))
        out.append(f'<a href="{esc(url)}">{esc(anchor)}</a>')
        pos = e
    out.append(esc(desc[pos:]))
    return "".join(out), len(chosen)

def classify(d):
    dl = d.lower()
    if any(k in dl for k in ["role change", "vp ai", "lead ai", "akademischer rat", "postdoc", "tenured position", "internship", "intern."]): return "Role"
    if any(k in dl for k in ["paper", "findings", "poster", "thesis", "journal", "publication", "proceedings", "short paper", "extended abstract", "press release"]): return "Paper"
    if any(k in dl for k in ["keynote", "invited speaker", "speaker", "lecturer", "guest-lecture", "guest lecturer", "colloquium", "lunch talk", "outreach"]): return "Talk"
    if any(k in dl for k in ["reviewer", "area chair", "program committee", "pc member", "organiser", "organizer", "chair", "editor", "committee", "panelist", "co-author", "general chair"]): return "Service"
    if any(k in dl for k in ["award", "scholarship", "awardee", "distinction", "bachelor", "member of the", "associate member", "associated member", "rise ", "erasmus"]): return "Award"
    return "Activity"

MONTHS = {m: i for i, m in enumerate(["January","February","March","April","May","June","July","August","September","October","November","December"], 1)}

def timeline_rows():
    rows = []
    for ln in block("home.md", "Research Activities"):
        m = re.match(r"^(\d{4})\b(.*)$", ln)
        if not m: continue
        year, rest = int(m.group(1)), m.group(2)
        month = ""
        if "|" in rest:
            mp, desc = rest.split("|", 1)
            month = re.sub(r"[-\s]", "", mp).strip(); desc = desc.strip()
        else:
            desc = rest.lstrip(" -|").strip()
        if month and month not in MONTHS:
            desc = month + " " + desc if not desc else desc; month = ""
        rows.append((year, MONTHS.get(month, 0), month, desc))
    rows.sort(key=lambda r: (-r[0], -r[1]))
    return rows

def build_activity():
    links = parse_links("home.md")
    rows = timeline_rows(); linked = 0
    body, cur = [], None
    for year, _, month, desc in rows:
        if year != cur:
            if cur is not None: body.append("</div>")
            body.append(f'<section class="grp"><div class="gh tnum">{year}</div>'); cur = year
        dl, n = link_desc(desc, links); linked += (1 if n else 0)
        body.append(f'<div class="e"><div class="mo">{esc(month)}</div><div class="d">{dl}</div><div class="ty">{classify(desc)}</div></div>')
    body.append("</div>")
    html = TPL.format(robots="index,follow", title="Activity", kick="Full record", h1="Activity",
        intro=f'A complete chronological record of papers, talks, service and roles, {rows[-1][0]}&ndash;{rows[0][0]}; most entries link to the paper, talk or venue. Selected highlights live on the <a href="index.html#about">front page</a>; the full publication list is on <a href="https://scholar.google.com/citations?user=qEXBDy4AAAAJ">Google Scholar</a>.',
        body="".join(body))
    (OUT/"activity.html").write_text(html, encoding="utf-8")
    print(f"activity.html: {len(rows)} entries, {linked} linked")

def build_service():
    items = []
    for ln in block("editorial-service.md", "Editorial Service"):
        if ":" in ln:
            role, rest = ln.split(":", 1); items.append((role.strip(), rest.strip().rstrip(".")))
        else:
            items.append(("", ln.strip().rstrip(".")))
    body = ['<section class="grp"><div class="gh">Reviewing, chairing &amp; committees</div>']
    for role, rest in items:
        body.append(f'<div class="e"><div class="mo"></div><div class="d">{esc(rest)}</div><div class="ty">{esc(role) or "Service"}</div></div>')
    body.append("</div>")
    html = TPL.format(robots="index,follow", title="Service", kick="Full record", h1="Editorial &amp; review service",
        intro='Reviewing, area-chairing, program committees and editorial roles across computational linguistics, cognitive science and human-robot interaction. A condensed summary is on the <a href="index.html#contact">front page</a>.',
        body="".join(body))
    (OUT/"service.html").write_text(html, encoding="utf-8")
    print(f"service.html: {len(items)} entries")

def grp(title, entries):
    """entries: list of (period, desc_html, kind)"""
    out = [f'<section class="grp"><div class="gh">{title}</div>']
    for period, desc, kind in entries:
        out.append(f'<div class="e"><div class="mo">{esc(period)}</div><div class="d">{desc}</div><div class="ty">{esc(kind)}</div></div>')
    out.append("</div>")
    return "".join(out)

def build_teaching():
    links = parse_links("home.md")
    pos = block("teaching.md", "Teaching", end="Supervision")
    sup = block("teaching.md", "Supervision")
    lectures, tutoring = [], []
    for ln in pos:
        if "|" not in ln: continue
        yr, rest = ln.split("|", 1); yr = yr.strip()
        d = rest.replace("|", " · ").strip()
        is_tutor = "tutor" in d.lower()
        d = re.sub(r"^(Lecturer|Tutor(\s*/\s*Teaching Assistance)?)\s*[-.:]?\s*", "", d, flags=re.I).strip()
        (tutoring if is_tutor else lectures).append((yr, esc(d), "Tutor / TA" if is_tutor else "Lecture"))
    # invited lectures + Interdisciplinary College, pulled from the timeline
    invited = []
    KW = ["guest-lecture", "guest lecturer", "colloquium", "sample lecture", "lab visit", "lunch talk"]
    for year, _, month, desc in timeline_rows():
        dl = desc.lower()
        ik = ("interdisciplinary college" in dl and "lecturer" in dl)
        if ik or any(k in dl for k in KW):
            linkedhtml, _ = link_desc(desc, links)
            kind = "Interdisciplinary College" if ik else ("Guest lecture" if "guest" in dl else "Invited")
            invited.append((f"{year}{(' · '+month) if month else ''}", linkedhtml, kind))
    # theses
    theses, degree = [], "MSc"
    for ln in sup:
        if ln.lower().startswith("supervised master"): degree = "MSc"; continue
        if ln.lower().startswith("supervised bachelor"): degree = "BSc"; continue
        m = re.match(r"^(\d{4})\s*:\s*(.+)$", ln)
        if m: theses.append((m.group(1), esc(m.group(2).strip().strip('"')), degree))
    body = grp("Lecturing", lectures) + grp("Invited lectures &amp; Interdisciplinary College", invited) \
         + grp("Tutoring &amp; teaching assistance", tutoring) + grp("Thesis supervision", theses)
    html = TPL.format(robots="index,follow", title="Teaching", kick="Full record", h1="Teaching",
        intro='Lecturing, invited lectures and courses at the Interdisciplinary College, a decade of tutoring from Osnabr&uuml;ck onward, and supervised theses. A summary of current courses is on the <a href="index.html#teaching">front page</a>.',
        body=body)
    (OUT/"teaching.html").write_text(html, encoding="utf-8")
    print(f"teaching.html: {len(lectures)} lectures, {len(invited)} invited, {len(tutoring)} tutoring, {len(theses)} theses")

def build_recent():
    """Inject the full timeline (links restored) into index.html between markers, for the
    front-page scrollable 'Activity' feed (no separate full-timeline link needed)."""
    links = parse_links("home.md")
    rows = timeline_rows()
    out = []
    for year, _, month, desc in rows:
        dl, _ = link_desc(desc, links)
        mo = " &middot; " + month[:3] if month else ""
        out.append(f'<div class="e"><div class="yr tnum">{year}{mo}</div><div class="d">{dl}</div><div class="ty">{classify(desc)}</div></div>')
    snippet = "\n" + "\n".join(out) + "\n"
    idx = OUT/"index.html"
    html = idx.read_text(encoding="utf-8")
    new = re.sub(r"(<!-- RECENT-START -->).*?(<!-- RECENT-END -->)",
                 lambda m: m.group(1) + snippet + m.group(2), html, flags=re.S)
    if new == html:
        print("index.html recent feed: markers not found (skipped)")
    else:
        idx.write_text(new, encoding="utf-8"); print(f"index.html activity feed: {len(rows)} entries injected")

def build_research():
    """Inject the publication list into index.html: chronological (recent first), with verified authors
    + layman explanations from pipeline/papers_meta.json and a subtle live per-paper citation count."""
    try:
        sj = json.loads((OUT/"assets"/"scholar.json").read_text(encoding="utf-8"))
    except Exception:
        print("research feed: scholar.json unreadable, skipped"); return
    meta = {}
    mp = pathlib.Path(__file__).resolve().parent / "papers_meta.json"
    if mp.exists():
        try: meta = json.loads(mp.read_text(encoding="utf-8"))
        except Exception: meta = {}
    EXCLUDE = {"UebtZRa9Y70C"}   # Scholar artifacts that are not real papers (seminar TOC fragment)
    best = {}   # dedup Scholar's duplicate entries by normalised title, keep the higher-cited one
    for p in sj.get("papers", []):
        if p.get("id") in EXCLUDE:
            continue
        k = re.sub(r'[^a-z0-9]', '', p.get("title", "").lower())[:55]
        if k and (k not in best or p.get("citations", 0) > best[k].get("citations", 0)):
            best[k] = p
    papers = sorted(best.values(), key=lambda p: (str(p.get("year", "")), p.get("citations", 0)), reverse=True)
    out = []
    for p in papers:
        m = meta.get(p.get("id", ""), {})
        title = esc(m.get("title") or p.get("title", ""))        # papers_meta may override title/venue/link
        link = esc(m.get("link") or p.get("link", "#"))
        venue = esc(m.get("venue") or p.get("venue", ""))
        yr, cit = esc(str(p.get("year", ""))), int(p.get("citations", 0))
        alist = m.get("authors") or [a.strip() for a in p.get("authors", "").split(",") if a.strip()]
        au = ", ".join(f"<b>{esc(a)}</b>" if "Wicke" in a else esc(a) for a in alist)
        au_line = au + (f' &middot; {venue}' if venue else "")
        ex = esc(m.get("explanation", "").strip())
        if ex:   # a + sits left of the title; on expand it turns to x with a thin line down to the description
            dblock = (f'<button class="pex-t" type="button" aria-expanded="true" aria-label="Toggle description"><span class="pex-i" aria-hidden="true">+</span></button>'
                      f'<div class="pex-body"><a href="{link}">{title}</a><span class="pex-au">{au_line}</span><p class="pex">{ex}</p></div>')
            dcls = "d hasexp"
        else:
            dblock = f'<a href="{link}">{title}</a><span class="au">{au_line}</span>'
            dcls = "d"
        out.append(f'<div class="e"><div class="yr tnum">{yr}</div><div class="{dcls}">{dblock}</div></div>')
    snippet = "\n" + "\n".join(out) + "\n"
    idx = OUT/"index.html"; html = idx.read_text(encoding="utf-8")
    new = re.sub(r"(<!-- PAPERS-START -->).*?(<!-- PAPERS-END -->)", lambda m: m.group(1)+snippet+m.group(2), html, flags=re.S)
    withmeta = sum(1 for p in papers if meta.get(p.get("id", "")))
    if new != html:
        idx.write_text(new, encoding="utf-8"); print(f"index.html research feed: {len(papers)} papers ({withmeta} with verified meta)")
    else:
        print("index.html research feed: markers not found / unchanged")

def build_research_record():
    """Generate research.html: every publication grouped by year, each with its full plain-language
    note shown inline (the front page carries the same list as a collapsible scrollable feed)."""
    try:
        sj = json.loads((OUT/"assets"/"scholar.json").read_text(encoding="utf-8"))
    except Exception:
        print("research.html: scholar.json unreadable, skipped"); return
    meta = {}
    mp = pathlib.Path(__file__).resolve().parent / "papers_meta.json"
    if mp.exists():
        try: meta = json.loads(mp.read_text(encoding="utf-8"))
        except Exception: meta = {}
    EXCLUDE = {"UebtZRa9Y70C"}
    best = {}
    for p in sj.get("papers", []):
        if p.get("id") in EXCLUDE: continue
        k = re.sub(r'[^a-z0-9]', '', p.get("title", "").lower())[:55]
        if k and (k not in best or p.get("citations", 0) > best[k].get("citations", 0)):
            best[k] = p
    papers = sorted(best.values(), key=lambda p: (str(p.get("year", "")), p.get("citations", 0)), reverse=True)
    groups = []
    for p in papers:
        y = str(p.get("year", "")) or "Undated"
        if not groups or groups[-1][0] != y: groups.append((y, []))
        groups[-1][1].append(p)
    body, total, withmeta = [], 0, 0
    for y, plist in groups:
        rows = []
        for p in plist:
            total += 1
            m = meta.get(p.get("id", ""), {})
            if m: withmeta += 1
            title = esc(m.get("title") or p.get("title", ""))
            link = esc(m.get("link") or p.get("link", "#"))
            venue = esc(m.get("venue") or p.get("venue", ""))
            cit = int(p.get("citations", 0))
            alist = m.get("authors") or [a.strip() for a in p.get("authors", "").split(",") if a.strip()]
            au = ", ".join(f"<b>{esc(a)}</b>" if "Wicke" in a else esc(a) for a in alist)
            au_line = au + (f' &middot; {venue}' if venue else "")
            ex = esc(m.get("explanation", "").strip())
            exhtml = f'<p class="pub-ex">{ex}</p>' if ex else ""
            cithtml = (f'<div class="pub-cit"><b>{cit}</b><span>cited</span></div>' if cit else '<div class="pub-cit"></div>')
            rows.append(f'<div class="pub"><div class="pub-main"><a class="pub-t" href="{link}">{title}</a>'
                        f'<div class="pub-au">{au_line}</div>{exhtml}</div>{cithtml}</div>')
        body.append(f'<section class="grp"><div class="gh">{esc(y)}</div>' + "".join(rows) + "</section>")
    html = TPL.format(robots="index,follow", title="Publications", kick="Full record", h1="Publications",
        intro='Every publication on record, grouped by year, each with a plain-language note on what it set out to do. '
              'The front page carries the same list as a scrollable feed; citation counts are live from '
              '<a href="https://scholar.google.com/citations?user=qEXBDy4AAAAJ">Google Scholar</a>.',
        body="".join(body))
    (OUT/"research.html").write_text(html, encoding="utf-8")
    print(f"research.html: {total} papers in {len(groups)} year-groups ({withmeta} with notes)")

def _address_svg():
    """The inline address SVG: fresh from the gitignored pipeline/address.svg when present
    (local machine), otherwise carried over from the existing imprint.html (CI rebuilds)."""
    staged = pathlib.Path(__file__).parent / "address.svg"
    if staged.exists():
        return staged.read_text(encoding="utf-8").strip()
    prev = OUT / "imprint.html"
    if prev.exists():
        m = re.search(r"<!-- ADDR-START -->(.*?)<!-- ADDR-END -->", prev.read_text(encoding="utf-8"), re.S)
        if m:
            return m.group(1)
    raise SystemExit("imprint address missing: no pipeline/address.svg and no existing block to carry over")

def build_imprint():
    """Generate imprint.html: a slim German Impressum with the legally required parts (provider details
    per § 5 DDG / § 18 Abs. 1 MStV, an email contact, and the responsible person under § 18 Abs. 2 MStV)
    plus one concise combined liability-and-copyright note. Address is a c/o at the Zander Labs Berlin office."""
    body = (
        '<section class="grp"><div class="gh">Angaben gem&auml;&szlig; &sect; 5 DDG</div>'
        '<p>Philipp Wicke</p>'
        # the postal address is INLINE SVG of glyph paths: no JS needed, no image asset/URL exists
        # (nothing to right-click-save or fetch), and the address never appears as text anywhere.
        # Source: gitignored pipeline/address.svg (from gen_address_svg.py); in CI, where that file
        # is absent, the block is carried over from the previously built imprint.html.
        f'<p style="margin-top:8px;"><!-- ADDR-START -->{_address_svg()}<!-- ADDR-END --></p></section>'
        '<section class="grp"><div class="gh">Kontakt</div>'
        '<p>E&#8209;Mail: philippwicke.contact&#8202;[at]&#8202;gmail.com</p></section>'
        '<section class="grp"><div class="gh">Redaktionell verantwortlich (&sect; 18 Abs. 2 MStV)</div>'
        '<p>Philipp Wicke, Anschrift wie oben.</p></section>'
        '<section class="grp"><div class="gh">Haftung und Urheberrecht</div>'
        '<p>Die eigenen Inhalte dieser Website wurden sorgf&auml;ltig erstellt; eine Gew&auml;hr f&uuml;r '
        'Richtigkeit und Vollst&auml;ndigkeit kann ich jedoch nicht &uuml;bernehmen. F&uuml;r die Inhalte '
        'verlinkter externer Seiten ist deren jeweiliger Anbieter verantwortlich; werde ich auf eine '
        'Rechtsverletzung aufmerksam, entferne ich die betreffenden Inhalte oder Links umgehend. Meine '
        'eigenen Inhalte unterliegen dem deutschen Urheberrecht, eine Nutzung &uuml;ber dessen gesetzliche '
        'Grenzen hinaus bedarf meiner Zustimmung.</p></section>'
    )
    html = TPL.format(robots="noindex,follow", title="Impressum", kick="Legal notice", h1="Impressum",
        intro='Pflichtangaben nach deutschem Recht (&sect; 5 DDG). Legal notice as required under German law.',
        body=body)
    (OUT/"imprint.html").write_text(html, encoding="utf-8")
    print("imprint.html written (slim: provider, contact, editorial responsibility, combined disclaimer)")

build_activity()
build_service()
build_teaching()
build_recent()
build_research()
build_research_record()
build_imprint()
