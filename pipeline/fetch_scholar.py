"""Fetch Google Scholar citation metrics for the site, write final/assets/scholar.json.
Runs locally and in CI (GitHub Action). If Scholar blocks the request, it keeps the existing
scholar.json (so the page always shows the last known good numbers)."""
import urllib.request, re, json, sys, pathlib, datetime
from html import unescape

USER = "qEXBDy4AAAAJ"
_ROOT = pathlib.Path(__file__).resolve().parents[1]
_SITE = _ROOT/"final" if (_ROOT/"final").exists() else _ROOT   # working repo vs public repo layout
OUT = _SITE / "assets" / "scholar.json"
URL = f"https://scholar.google.com/citations?user={USER}&hl=en&cstart=0&pagesize=100"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

def clean_venue(v):
    v = re.sub(r'arXiv.*', 'arXiv', v, flags=re.I)
    v = re.sub(r'[.\s]*https?:.*$', '', v)                       # URLs (incl. broken "https://doi. org")
    v = re.sub(r'\s*(?:…|\.\.\.)\s*$', '', v)               # trailing ellipsis from Scholar truncation
    v = re.sub(r'\s+\d+\s*\(\d+\)[\s\d.,()\-–—:e]*$', '', v)   # " 15 (9), e0240010"
    v = re.sub(r',\s*\d[\s\d.,()\-–—:e]*$', '', v)     # trailing ", 56-63" / ", 651997"
    v = re.sub(r'\s+\d+$', '', v)                                # trailing bare volume/year
    v = re.sub(r'Findings of the Association for Computational Linguistics:?\s*ACL?', 'Findings of ACL', v)
    return v.strip().rstrip(' ,;.')

def fetch():
    req = urllib.request.Request(URL, headers={"User-Agent": UA, "Accept-Language": "en"})
    html = urllib.request.urlopen(req, timeout=45).read().decode("utf-8", "ignore")
    std = [int(x) for x in re.findall(r'gsc_rsb_std">(\d+)<', html)]   # [cit_all,cit_since,h_all,h_since,i10_all,i10_since]
    if len(std) < 6:
        raise RuntimeError("metrics not found (Scholar likely blocked the request)")
    years = [int(y) for y in re.findall(r'class="gsc_g_t"[^>]*>(\d{4})<', html)]
    counts = [int(c) for c in re.findall(r'class="gsc_g_al">(\d+)<', html)]
    per_year = [{"year": y, "n": c} for y, c in zip(years, counts)] if len(years) == len(counts) else []
    papers = []
    for row in re.findall(r'<tr class="gsc_a_tr">(.*?)</tr>', html, re.S):
        m = re.search(r'href="(/citations\?view_op=view_citation[^"]+)"[^>]*class="gsc_a_at">([^<]+)</a>', row)
        if not m:
            continue
        grays = re.findall(r'class="gs_gray">([^<]*)<', row)
        cm = re.search(r'class="gsc_a_ac[^"]*"[^>]*>(\d+)<', row)
        ym = re.search(r'class="gsc_a_h[^"]*">(\d{4})<', row)
        pid = re.search(r'citation_for_view=[^:]*:([\w-]+)', m.group(1))
        papers.append({"title": unescape(m.group(2)),
                       "id": pid.group(1) if pid else "",
                       "authors": unescape(grays[0]) if grays else "",
                       "venue": clean_venue(unescape(grays[1])) if len(grays) > 1 else "",
                       "year": ym.group(1) if ym else "",
                       "citations": int(cm.group(1)) if cm else 0,
                       "link": "https://scholar.google.com" + unescape(m.group(1))})
    return {"citations": std[0], "hindex": std[2], "i10index": std[4],
            "perYear": per_year, "papers": papers,
            "updated": datetime.date.today().isoformat(), "source": "scholar"}

if __name__ == "__main__":
    try:
        data = fetch()
        OUT.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        print("OK", {k: data[k] for k in ("citations", "hindex", "i10index")}, "perYear:", len(data["perYear"]), "papers:", len(data.get("papers", [])))
    except Exception as e:
        print("FETCH FAILED:", type(e).__name__, str(e)[:140])
        if not OUT.exists():
            # seed from the CV so the page has numbers even before a successful scrape
            seed = {"citations": 907, "hindex": 12, "i10index": 15,
                    "perYear": [{"year": y, "n": n} for y, n in
                                zip(range(2018, 2027), [3, 4, 37, 166, 186, 137, 140, 143, 69])],
                    "updated": "2026-06", "source": "cv-seed"}
            OUT.write_text(json.dumps(seed, indent=2) + "\n", encoding="utf-8")
            print("seeded scholar.json from CV figures")
        sys.exit(0)
