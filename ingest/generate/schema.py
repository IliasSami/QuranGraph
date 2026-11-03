"""Schema + automatic checks for one ayah explanation (work/explain/<sss>/<aaa>.json). See agent/INSTRUCTIONS.md.

validate(d, db) -> (errors, warnings). Errors block the ayah from the site; warnings go to the reviewer.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.normalize import arabic_skeleton  # noqa: E402  (the one shared normaliser)

KINDS = {"belief", "worship", "dua", "command", "prohibition", "promise", "warning", "story", "parable", "oath",
         "law", "ethics", "argument", "description-of-allah", "hereafter", "creation", "address", "praise", "glad-tidings"}
SENSITIVITY = {"none", "aqeedah", "fiqh", "often-misquoted", "eschatology", "interfaith"}
ENTITY_KEYS = {"people", "nations", "places", "unseen", "names_of_allah", "events", "things"}
REQUIRED = ("id", "simple_en", "simple_bn", "key_words", "lesson_en", "lesson_bn", "real_life_en", "real_life_bn",
            "themes", "kinds", "entities", "claims", "sensitivity", "scholars_differ", "confidence", "uncertain")
DISPLAY_TAFSIR = {"qe-english-mokhtasar", "qe-bengali-mokhtasar", "qe-arabic-mokhtasar", "qe-arabic-moyassar"}

# phrases that make text robotic, padded, or claim authority it doesn't have
BANNED_EN = [r"\bdelve", r"\btapestry\b", r"\bin conclusion\b", r"\bit is (important|worth) (to note|noting)\b", r"\bfurthermore\b",
             r"\bmoreover\b", r"\bin today'?s (fast-paced|modern) world\b", r"\bjourney\b", r"\bnavigat(e|ing) (life|the)",
             r"\bas an ai\b", r"\ball scholars agree\b", r"\bfatwa\b", r"\bit is haram\b", r"\bit is halal\b",
             r"\bprofound\b", r"\bunlock\b", r"\bembrace\b", r"\btestament to\b", r"\brealm\b", r"!"]
# naming tafsir sources belongs in `claims`, not in the teaching text (except in differ notes)
SOURCE_NAMES = re.compile(r"(Mukhtasar|Sa'?di|Ibn Kathir|Jalalayn|Ma'?ari?f|Muyassar|Zakaria|Ahsanul|মুখতাসার|সা'?দী|ইবনে কাসীর|জালালাইন|মাআরিফ|মুয়াসসার|যাকারিয়া|আহসানুল)")
ARABIC_RUN = re.compile(r"[؀-ۿ][؀-ۿ\s]{6,}[؀-ۿ]")


def sentences(t):
    return [x for x in re.split(r"(?<=[.?!।])[\"'”’)]*\s+", t.strip()) if x]


def words_of(t):
    return re.findall(r"[A-Za-z']+", t)


def syllables(w):
    w = w.lower()
    groups = re.findall(r"[aeiouy]+", w)
    n = len(groups) - (1 if w.endswith("e") and len(groups) > 1 else 0)
    return max(1, n)


def fk_grade(t):
    ss, ws = sentences(t), words_of(t)
    if not ss or not ws:
        return 0
    return 0.39 * len(ws) / len(ss) + 11.8 * sum(syllables(w) for w in ws) / len(ws) - 15.59


def validate(d, db):
    errs, warns = [], []
    for k in REQUIRED:
        if k not in d:
            errs.append(f"missing field {k}")
    if errs:
        return errs, warns
    m = re.match(r"^(\d{1,3}):(\d{1,3})$", str(d["id"]))
    row = db.execute("SELECT text_uthmani, skel FROM ayah WHERE surah=? AND ayah=?", (int(m.group(1)), int(m.group(2)))).fetchone() if m else None
    if not row:
        return [f"id {d['id']!r} is not an ayah"], warns
    s, a = int(m.group(1)), int(m.group(2))

    # ---- plain-language fields
    for k, lo, hi in (("simple_en", 25, 140), ("lesson_en", 6, 45), ("real_life_en", 15, 90)):
        n = len(words_of(d[k]))
        if not (lo <= n <= hi):
            (errs if n < lo // 2 or n > hi * 1.5 else warns).append(f"{k}: {n} words (aim {lo}-{hi})")
        g = fk_grade(d[k])
        if g > 10:
            warns.append(f"{k}: reading grade {g:.1f} (aim <= 8; shorter sentences, plainer words)")
        for pat in BANNED_EN:
            if re.search(pat, d[k], re.I):
                warns.append(f"{k}: avoid {pat.strip(chr(92)+'b')!r}")
    for k in ("simple_bn", "lesson_bn", "real_life_bn"):
        t = d[k]
        if not re.search(r"[ঀ-৿]", t):
            errs.append(f"{k}: not Bangla")
        if re.search(r"[A-Za-z]{3,}", t):
            warns.append(f"{k}: contains Latin words")
        if any(len(x.split()) > 30 for x in sentences(t)):
            warns.append(f"{k}: a sentence over 30 words")

    for k in ("simple_en", "simple_bn", "lesson_en", "lesson_bn", "real_life_en", "real_life_bn"):
        if SOURCE_NAMES.search(d[k]):
            warns.append(f"{k}: names a tafsir source — teach in plain words; attributions go in claims")

    # ---- Arabic quoted in our text must be Quran text (this ayah or another), never re-typed differently
    for k in ("simple_en", "simple_bn", "lesson_en", "lesson_bn", "real_life_en", "real_life_bn"):
        for q in ARABIC_RUN.findall(d[k]):
            qk = arabic_skeleton(q)
            if qk and not db.execute("SELECT 1 FROM ayah WHERE (surah=? AND ayah=? AND instr(skel, ?)) OR instr(skel, ?) LIMIT 1",
                                     (s, a, qk, qk)).fetchone():
                warns.append(f"{k}: Arabic {q.strip()!r} does not match the Quran text — quote exactly or leave it out")

    # ---- key words must be real words of this ayah with their real root/lemma
    wrows = {r[0]: r for r in db.execute("SELECT pos, text, root, lemma FROM word WHERE surah=? AND ayah=?", (s, a))}
    if not 1 <= len(d["key_words"]) <= 5:
        warns.append(f"key_words: give 1-5 (got {len(d['key_words'])})")
    for i, w in enumerate(d["key_words"]):
        r = wrows.get(w.get("pos"))
        if not r:
            errs.append(f"key_words[{i}].pos {w.get('pos')} is not a word position in {s}:{a}")
            continue
        if (w.get("root") or None) != (r[2] or None):
            errs.append(f"key_words[{i}].root {w.get('root')!r} != morphology {r[2]!r} for {r[1]}")
        for k in ("meaning_en", "meaning_bn", "why_en"):
            if not w.get(k):
                errs.append(f"key_words[{i}].{k} missing")

    # ---- every claim cites a source that actually has text for this ayah (or its passage)
    have = {x[0] for x in db.execute("SELECT DISTINCT source FROM text WHERE surah=? AND ayah BETWEEN ? AND ? AND coalesce(note, '') NOT LIKE 'misaligned%'",
                                     (s, max(1, a - 11), a))}
    if not d["claims"]:
        errs.append("claims: at least one claim with its sources is required")
    for i, c in enumerate(d["claims"]):
        srcs = c.get("sources") or []
        if not srcs:
            errs.append(f"claims[{i}] has no sources")
        for sid in srcs:
            if sid not in have:
                errs.append(f"claims[{i}] cites {sid!r}, which has no (usable) text for {s}:{a}")
        if not any(sid in DISPLAY_TAFSIR or sid.startswith(("qe-", "g-")) for sid in srcs):
            errs.append(f"claims[{i}] must cite a tafsir or translation source")
    if not any(sid in DISPLAY_TAFSIR for c in d["claims"] for sid in c.get("sources", [])):
        warns.append("no claim cites Al-Mukhtasar / al-Muyassar (the displayed tafsir)")

    # ---- vocabulary
    bad = set(d["kinds"]) - KINDS
    if bad or not d["kinds"]:
        errs.append(f"kinds: unknown or empty {sorted(bad)}")
    if d["sensitivity"] not in SENSITIVITY:
        errs.append(f"sensitivity must be one of {sorted(SENSITIVITY)}")
    if not isinstance(d["entities"], dict) or set(d["entities"]) - ENTITY_KEYS:
        errs.append(f"entities keys must be among {sorted(ENTITY_KEYS)}")
    if not (1 <= len(d["themes"]) <= 8):
        warns.append("themes: give 1-8")
    if d["scholars_differ"] and not d.get("differ_note_en"):
        errs.append("scholars_differ is true: add differ_note_en (and differ_note_bn) naming the views and sources")
    if not 0 <= float(d["confidence"]) <= 1:
        errs.append("confidence must be 0-1")
    return errs, warns
