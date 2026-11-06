"""Build a self-contained review page for explained ayat: ingest/work/review/index.html

For each ayah: Tanzil Arabic, Saheeh International + Zakaria translations, Al-Mukhtasar (EN), then QuranGraph's
explanation (EN + BN), key words, lesson, real-life example, context, claims with their sources, and review flags
(sensitivity, scholars differ, low confidence, validator warnings). Only display-licensed sources are shown;
grounding texts never appear on the page.

Usage: uv run generate/review_page.py [surah ...]      (default: every surah that has explanations)
"""
import html
import json
import os
import re
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schema import validate  # noqa: E402
from qg import review_priority  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(ROOT, "work")
OUT = os.path.join(WORK, "review", "index.html")
SOURCE_LABEL = {
    "qe-english-saheeh": "Saheeh Intl", "qe-bengali-zakaria": "Zakaria (BN)", "qe-english-mokhtasar": "Mukhtasar (EN)",
    "qe-bengali-mokhtasar": "Mukhtasar (BN)", "qe-arabic-mokhtasar": "Mukhtasar (AR)", "qe-arabic-moyassar": "Muyassar",
    "g-ar-saadi": "Sa'di", "g-en-ibn-kathir": "Ibn Kathir", "g-en-maarif": "Ma'ariful Qur'an", "g-en-jalalayn": "Jalalayn",
    "g-bn-ahsanul-bayan": "Ahsanul Bayan", "g-en-wahidi": "al-Wahidi", "g-ar-ibn-kathir": "Ibn Kathir (AR)",
}

CSS = """
:root{--bg:#f6f5f1;--surface:#fff;--ink:#1d1f1c;--ink2:#565a52;--line:#dcd9cf;--accent:#1f5f4a;--soft:#e8f1ec;
--warn:#8a5a00;--warnbg:#fff4dc;--flag:#8a1f2b;--flagbg:#fde8ea;--radius:10px}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#141614;--surface:#1d201d;--ink:#e9ebe6;--ink2:#a9ada4;
--line:#353a34;--accent:#7fc8a9;--soft:#22302a;--warn:#f0c46a;--warnbg:#3a3020;--flag:#f39aa4;--flagbg:#3d2226}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif}
header{position:sticky;top:0;z-index:2;background:var(--surface);border-bottom:1px solid var(--line);padding:10px 16px}
header .row{max-width:1100px;margin:0 auto;display:flex;flex-wrap:wrap;gap:8px 16px;align-items:center}
h1{font-size:18px;margin:0;color:var(--accent)} .stat{color:var(--ink2);font-size:14px}
button,select{font:inherit;font-size:14px;padding:6px 12px;border-radius:8px;border:1px solid var(--line);background:var(--surface);color:var(--ink);cursor:pointer;min-height:36px}
button[aria-pressed=true]{background:var(--accent);color:var(--surface);border-color:var(--accent)}
main{max-width:1100px;margin:0 auto;padding:16px}
h2{font-size:20px;margin:28px 0 8px} h2 small{color:var(--ink2);font-weight:400;font-size:14px}
.ayah{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);margin:12px 0;padding:16px}
.ayah.flagged{border-left:4px solid var(--line)}
.ayah.must-review{border-left:4px solid var(--flag)}
.ayah.sample-review{border-left:4px solid var(--warn)}
.top{display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap;align-items:baseline}
.ref{font-weight:700;color:var(--accent)} .badges{display:flex;gap:6px;flex-wrap:wrap}
.badge{font-size:12px;padding:2px 8px;border-radius:99px;background:var(--soft);color:var(--accent)}
.badge.flag{background:var(--flagbg);color:var(--flag)} .badge.warn{background:var(--warnbg);color:var(--warn)}
.badge.must{background:var(--flagbg);color:var(--flag);font-weight:600} .badge.sample{background:var(--warnbg);color:var(--warn)}
.ar{font-family:"Amiri Quran","Amiri","KFGQPC Uthmanic Script HAFS",serif;font-size:28px;line-height:2.2;direction:rtl;text-align:right;margin:8px 0}
.bn{font-family:"Noto Serif Bengali","Hind Siliguri",serif;line-height:1.9}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:16px} @media (max-width:760px){.grid{grid-template-columns:1fr}}
.box{border-top:1px solid var(--line);padding-top:10px;margin-top:10px}
.label{font-size:12px;letter-spacing:.04em;text-transform:uppercase;color:var(--ink2);margin-bottom:2px}
.ours{background:var(--soft);border-radius:8px;padding:10px 12px}
.src{color:var(--ink2);font-size:14px}
details{margin-top:8px} summary{cursor:pointer;color:var(--accent);font-size:14px}
ul{margin:4px 0;padding-left:20px} li{margin:2px 0}
.kw{display:flex;gap:10px;flex-wrap:wrap} .kw div{border:1px solid var(--line);border-radius:8px;padding:6px 10px;font-size:14px;max-width:340px}
.kw .w{font-family:"Amiri Quran","Amiri",serif;font-size:22px;direction:rtl}
.cite{font-size:12px;color:var(--ink2)} .warnlist{color:var(--warn);font-size:14px}
"""

JS = """
const btns=document.querySelectorAll('[data-filter]');
btns.forEach(b=>b.addEventListener('click',()=>{
  btns.forEach(x=>x.setAttribute('aria-pressed',x===b));
  const f=b.dataset.filter;
  document.querySelectorAll('.ayah').forEach(a=>{
    if(f==='all') a.hidden=false;
    else if(f==='must') a.hidden=!a.classList.contains('must-review');
    else if(f==='sample') a.hidden=!a.classList.contains('sample-review');
    else if(f==='flagged') a.hidden=!a.classList.contains('flagged');
  });
}));
document.getElementById('jump').addEventListener('change',e=>{location.hash=e.target.value});
"""


def esc(t):
    return html.escape(t or "")


def strip_tags(t):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", t or "")).strip()


def main():
    db = sqlite3.connect(os.path.join(WORK, "quran.sqlite"))
    explain = os.path.join(ROOT, "content", "explain")
    surahs = [int(x) for x in sys.argv[1:]] or sorted(int(d) for d in os.listdir(explain) if d.isdigit())
    parts, total, flagged_n, warn_n, must_n, sample_n = [], 0, 0, 0, 0, 0
    jump = []
    for s in surahs:
        name = db.execute("SELECT name_translit, name_ar, name_en, type, ayat, name_bn FROM surah WHERE id=?", (s,)).fetchone()
        files = sorted(os.listdir(os.path.join(explain, f"{s:03d}")))
        jump.append(f'<option value="s{s}">{s}. {esc(name[0])} · {esc(name[5])}</option>')
        parts.append(f'<h2 id="s{s}">{s}. {esc(name[0])} · <span class="bn">{esc(name[5])}</span> <span class="ar" style="font-size:22px">{esc(name[1])}</span> '
                     f'<small>{esc(name[2])} · {name[3]} · {len(files)}/{name[4]} ayat explained</small></h2>')
        for f in files:
            d = json.load(open(os.path.join(explain, f"{s:03d}", f), encoding="utf-8"))
            a = int(f[:3])
            errs, warns = validate(d, db)
            ar = db.execute("SELECT text_uthmani FROM ayah WHERE surah=? AND ayah=?", (s, a)).fetchone()[0]
            tr = {src: strip_tags(t) for src, t in db.execute(
                "SELECT source, text FROM text WHERE surah=? AND ayah=? AND source IN ('qe-english-saheeh','qe-bengali-zakaria','qe-english-mokhtasar')", (s, a))}
            flags = []
            prio = review_priority(d)
            if prio == "must":
                flags.append(("must", "must review"))
                must_n += 1
            elif prio == "sample":
                flags.append(("sample", "sample review"))
                sample_n += 1
            if d.get("sensitivity", "none") != "none":
                flags.append(("flag", d["sensitivity"]))
            if d.get("scholars_differ"):
                flags.append(("flag", "scholars differ"))
            if float(d.get("confidence", 1)) < 0.88:
                flags.append(("flag", f"confidence {d['confidence']}"))
            if d.get("uncertain"):
                flags.append(("warn", "uncertain"))
            if errs:
                flags.append(("flag", f"{len(errs)} errors"))
            if warns:
                flags.append(("warn", f"{len(warns)} warnings"))
            is_flagged = bool(prio) or any(k == "flag" for k, _ in flags) or bool(d.get("uncertain")) or bool(errs) or bool(warns)
            total += 1
            flagged_n += is_flagged
            warn_n += bool(warns)
            badges = "".join(f'<span class="badge {k}">{esc(v)}</span>' for k, v in flags) + \
                "".join(f'<span class="badge">{esc(k)}</span>' for k in d.get("kinds", []))
            kw = "".join(f'<div><div class="w">{esc(next((r[0] for r in db.execute("SELECT text FROM word WHERE surah=? AND ayah=? AND pos=?", (s, a, w["pos"]))), ""))}</div>'
                         f'<b>{esc(w.get("meaning_en"))}</b> · <span class="bn">{esc(w.get("meaning_bn"))}</span><br>'
                         f'<span class="cite">root {esc(w.get("root") or "—")}</span> {esc(w.get("why_en"))}</div>' for w in d.get("key_words", []))
            claims = "".join(f'<li>{esc(c.get("text") or c.get("claim") or str(c))} <span class="cite">— {", ".join(SOURCE_LABEL.get(x, x) for x in c.get("sources", []))}</span></li>'
                             for c in d.get("claims", []) if isinstance(c, dict))
            ents = "; ".join(f"{k}: {', '.join(v)}" for k, v in d.get("entities", {}).items() if v)
            occ = d.get("occasion")
            if isinstance(occ, dict):
                occ_html = (f'<div class="box"><div class="label">Occasion of revelation ({esc(occ.get("strength"))})</div>{esc(occ.get("text_en"))}'
                            f'<div class="bn">{esc(occ.get("text_bn"))}</div></div>')
            elif isinstance(occ, str) and occ.strip():
                occ_html = f'<div class="box"><div class="label">Occasion of revelation</div>{esc(occ)}</div>'
            else:
                occ_html = ""
            differ = (f'<div class="box"><div class="label">Scholars differ</div>{esc(d.get("differ_note_en"))}'
                       f'<div class="bn">{esc(d.get("differ_note_bn"))}</div></div>') if d.get("scholars_differ") else ""
            context = (f'<div class="box"><div class="label">Context</div>{esc(d.get("context_en"))}'
                       f'<div class="bn">{esc(d.get("context_bn"))}</div></div>') if d.get("context_en") else ""
            unc = d.get("uncertain", [])
            unc_list = unc if isinstance(unc, list) else ([str(unc)] if unc else [])
            issues = "".join(f"<li>ERROR: {esc(e)}</li>" for e in errs) + "".join(f"<li>{esc(w)}</li>" for w in warns) + \
                "".join(f"<li>Uncertain: {esc(u)}</li>" for u in unc_list)
            parts.append(f"""
<article class="ayah{' flagged' if is_flagged else ''}{' must-review' if prio == 'must' else (' sample-review' if prio == 'sample' else '')}" id="a{s}-{a}">
 <div class="top"><span class="ref">{s}:{a}</span><div class="badges">{badges}</div></div>
 <div class="ar" lang="ar">{esc(ar)}</div>
 <div class="grid">
  <div><div class="label">Saheeh International</div><div class="src">{esc(tr.get('qe-english-saheeh'))}</div></div>
  <div><div class="label">Zakaria (Bangla)</div><div class="src bn" lang="bn">{esc(tr.get('qe-bengali-zakaria'))}</div></div>
 </div>
 <details><summary>Al-Mukhtasar (shown on the site as the source text)</summary><div class="src">{esc(tr.get('qe-english-mokhtasar'))}</div></details>
 <div class="box"><div class="label">QuranGraph simple explanation</div>
  <div class="grid"><div class="ours">{esc(d.get('simple_en'))}</div><div class="ours bn" lang="bn">{esc(d.get('simple_bn'))}</div></div></div>
 <div class="box"><div class="label">Key words</div><div class="kw">{kw}</div></div>
 <div class="box grid">
  <div><div class="label">Lesson</div>{esc(d.get('lesson_en'))}<div class="bn" lang="bn">{esc(d.get('lesson_bn'))}</div></div>
  <div><div class="label">Real life</div>{esc(d.get('real_life_en'))}<div class="bn" lang="bn">{esc(d.get('real_life_bn'))}</div></div>
 </div>
 {context}{occ_html}{differ}
 <details><summary>Claims and sources ({len(d.get('claims', []))}) · themes · entities</summary>
  <ul>{claims}</ul><div class="cite">Themes: {esc(', '.join(d.get('themes', [])))}<br>Entities: {esc(ents) or '—'}</div></details>
 {f'<details open><summary>Review notes</summary><ul class="warnlist">{issues}</ul></details>' if issues else ''}
</article>""")
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>QuranGraph Pilot Review</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Amiri+Quran&family=Noto+Serif+Bengali:wght@400;600&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body>
<header><div class="row"><h1>QuranGraph · Pilot review</h1>
<span class="stat">{total} ayat · {must_n} must review · {sample_n} sample review · {warn_n} with validator warnings</span>
<button data-filter="all" aria-pressed="true">All</button>
<button data-filter="must" aria-pressed="false">Must review ({must_n})</button>
<button data-filter="sample" aria-pressed="false">Sample review ({sample_n})</button>
<button data-filter="flagged" aria-pressed="false">All flagged ({flagged_n})</button>
<select id="jump" aria-label="Jump to surah"><option value="">Jump to surah…</option>{''.join(jump)}</select></div></header>
<main>
<p class="src">Arabic: Tanzil Project (tanzil.net). Translations and Al-Mukhtasar via QuranEnc.com. The simple explanation,
key words, lesson and real-life example are AI-drafted from the cited tafsir sources and are awaiting scholarly review.</p>
{''.join(parts)}
</main><script>{JS}</script></body></html>"""
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write(page)
    print(f"wrote {OUT}: {total} ayat, {must_n} must-review, {sample_n} sample-review, {flagged_n} flagged total")


if __name__ == "__main__":
    main()
