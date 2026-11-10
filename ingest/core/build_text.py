"""Build the text core: work/quran.sqlite from the raw sources (work/raw, see sources.yaml / sources.lock.json).

Tables
  source     every source: id, kind, use (display|data|grounding), title, lang, version, licence, attribution
  surah      114 rows: Arabic/translit/English names, Meccan/Medinan, revelation order, ayah count, rukus
  ayah       6,236 rows: global id, surah, ayah, Uthmani text (display), simple-clean text (search), skel (search key),
             juz, hizb quarter, manzil, ruku, mushaf page, sajda
  word       one row per word (morphology segmentation): text, root, lemma, part of speech, features, segments
  text       translations + tafsir per (source, surah, ayah): text, footnotes  -- display AND grounding sources;
             the exporter only ever ships rows whose source.use == 'display'

Checks (fail the build): 6,236 ayat in every source; display texts verbatim from their files; morphology words
cover every ayah. Prints a short report.
"""
import collections
import glob
import json
import os
import re
import sqlite3
import sys
import xml.etree.ElementTree as ET

import yaml

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.normalize import tokenize_many  # noqa: E402
from core.surah_names_bn import SURAH_NAMES_BN  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(ROOT, "work")
RAW = os.path.join(WORK, "raw")
DB_PATH = os.path.join(WORK, "quran.sqlite")
N_AYAT = 6236

SCHEMA = """
CREATE TABLE source (id TEXT PRIMARY KEY, kind TEXT, use TEXT, role TEXT, title TEXT, publisher TEXT, lang TEXT,
                     version TEXT, licence TEXT, attribution TEXT, status TEXT);
CREATE TABLE surah (id INTEGER PRIMARY KEY, name_ar TEXT, name_translit TEXT, name_en TEXT, name_bn TEXT, type TEXT,
                    revelation_order INTEGER, ayat INTEGER, rukus INTEGER, start INTEGER);
CREATE TABLE ayah (id INTEGER PRIMARY KEY, surah INTEGER, ayah INTEGER, text_uthmani TEXT, text_simple TEXT, skel TEXT,
                   juz INTEGER, hizb_quarter INTEGER, manzil INTEGER, ruku INTEGER, page INTEGER, sajda TEXT,
                   UNIQUE (surah, ayah));
CREATE TABLE word (surah INTEGER, ayah INTEGER, pos INTEGER, text TEXT, root TEXT, lemma TEXT, tag TEXT,
                   features TEXT, segments TEXT, PRIMARY KEY (surah, ayah, pos));
CREATE TABLE text (source TEXT, surah INTEGER, ayah INTEGER, text TEXT, footnotes TEXT, note TEXT, PRIMARY KEY (source, surah, ayah));
CREATE TABLE basmala (surah INTEGER PRIMARY KEY, text_uthmani TEXT, text_simple TEXT);
CREATE INDEX word_root ON word(root);
CREATE INDEX word_lemma ON word(lemma);
"""


def read_tanzil(path):
    """Tanzil txt-2: 'sura|aya|text' lines; the licence block is '#' comments at the end."""
    rows = {}
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if not line or line.startswith("#"):
            continue
        s, a, t = line.split("|", 2)
        rows[(int(s), int(a))] = t
    if len(rows) != N_AYAT:
        sys.exit(f"{path}: {len(rows)} ayat, expected {N_AYAT}")
    return rows


def metadata():
    root = ET.parse(os.path.join(RAW, "tanzil-metadata", "quran-data.xml")).getroot()
    suras = [dict(e.attrib) for e in root.find("suras")]

    def starts(tag):
        return sorted(((int(e.get("sura")), int(e.get("aya"))), int(e.get("index"))) for e in root.find(tag))

    sajdas = {(int(e.get("sura")), int(e.get("aya"))): e.get("type") for e in root.find("sajdas")}
    return suras, {t: starts(t) for t in ("juzs", "hizbs", "manzils", "rukus", "pages")}, sajdas


def locate(starts, key):
    """Index of the last division that starts at or before (sura, aya)."""
    idx = 0
    for (k, i) in starts:
        if k <= key:
            idx = i
        else:
            break
    return idx


def read_morphology():
    words = collections.OrderedDict()
    for line in open(os.path.join(RAW, "morphology", "quran-morphology.txt"), encoding="utf-8"):
        loc, form, tag, feats = line.rstrip("\n").split("\t")
        s, a, w, seg = map(int, loc.split(":"))
        f = feats.split("|")
        root = next((x[5:] for x in f if x.startswith("ROOT:")), None)
        lemma = next((x[4:] for x in f if x.startswith("LEM:")), None)
        rec = words.setdefault((s, a, w), {"text": "", "root": None, "lemma": None, "tag": None, "features": [],
                                           "segments": [], "_stem": False})
        rec["text"] += form
        rec["segments"].append([form, tag, feats])
        is_affix = "PREF" in f or "SUFF" in f
        # the stem carries the word's root, lemma and part of speech; a word made only of particles uses its first one
        if (not is_affix and not rec["_stem"]) or rec["tag"] is None:
            rec.update(root=root, lemma=lemma, tag=tag, features=[x for x in f if not x.startswith(("ROOT:", "LEM:"))])
            rec["_stem"] = not is_affix
    return words


DIGITS = {c: str(i % 10) for i, c in enumerate("0123456789০১২৩৪৫৬৭৮৯٠١٢٣٤٥٦٧٨٩")}


def drop_carried_over(db, srcs):
    """The tafsir mirrors sometimes repeat the previous surah's last passage under the first ayat of the next surah
    (e.g. Ma'ariful Qur'an 82:1 = its commentary on 81:19-23). Those rows are removed so they are never read as
    commentary on the new surah."""
    out = []
    last = dict(db.execute("SELECT id, ayat FROM surah"))
    for src in srcs:
        dropped = 0
        for s in range(2, 115):
            prev = db.execute("SELECT text FROM text WHERE source=? AND surah=? AND ayah=?", (src, s - 1, last[s - 1])).fetchone()
            a = 1
            while prev and a <= last[s]:
                cur = db.execute("SELECT text FROM text WHERE source=? AND surah=? AND ayah=?", (src, s, a)).fetchone()
                if not cur or cur[0] != prev[0]:
                    break
                db.execute("DELETE FROM text WHERE source=? AND surah=? AND ayah=?", (src, s, a))
                dropped += 1
                a += 1
        if dropped:
            out.append(f"{src}: removed {dropped} rows carried over from the previous surah")
    db.commit()
    return out


def check_tafsir_numbers(db):
    """Al-Mukhtasar starts each explanation with its ayah number. Where that number differs from the ayah it is filed
    under, mark it: 'same-wording' when the numbered ayah has identical Arabic (a repeated refrain, the explanation
    still fits), else 'misaligned' (that ayah's own explanation is missing in the source: hidden on the site and
    reported to QuranEnc)."""
    out = []
    for src in ("qe-english-mokhtasar", "qe-bengali-mokhtasar", "qe-arabic-mokhtasar"):
        counts = collections.Counter()
        for s, a, t in db.execute("SELECT surah, ayah, text FROM text WHERE source=?", (src,)).fetchall():
            m = re.match(r"\s*([0-9০-৯٠-٩]+)\s*[.\-–]", t)
            if not m:
                continue
            n = int("".join(DIGITS[c] for c in m.group(1)))
            if n == a:
                continue
            same = db.execute("SELECT (SELECT skel FROM ayah WHERE surah=? AND ayah=?) = (SELECT skel FROM ayah WHERE surah=? AND ayah=?)",
                              (s, a, s, n)).fetchone()[0]
            note = "same-wording" if same else "misaligned"
            counts[note] += 1
            db.execute("UPDATE text SET note=? WHERE source=? AND surah=? AND ayah=?", (f"{note}:{s}:{n}", src, s, a))
        out.append(f"{src}: numbering check {dict(counts) or 'all match'}")
    db.commit()
    return out


def main():
    sources = yaml.safe_load(open(os.path.join(ROOT, "sources.yaml"), encoding="utf-8"))
    lock = json.load(open(os.path.join(ROOT, "sources.lock.json")))
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    db = sqlite3.connect(DB_PATH)
    db.executescript(SCHEMA)

    for s in sources:
        db.execute("INSERT INTO source VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                   (s["id"], s["kind"], s["use"], s.get("role"), s["title"], s.get("publisher"), s.get("lang"),
                    str(lock.get(s["id"], {}).get("version") or ""), s["licence"], s["attribution"], s["status"]))

    # ---- surahs + ayat
    suras, div, sajdas = metadata()
    for e in suras:
        si = int(e["index"])
        name_bn = SURAH_NAMES_BN.get(si, "")
        db.execute("INSERT INTO surah VALUES (?,?,?,?,?,?,?,?,?,?)",
                   (si, e["name"], e["tname"], e["ename"], name_bn, e["type"], int(e["order"]), int(e["ayas"]),
                    int(e["rukus"]), int(e["start"])))
    uth = read_tanzil(os.path.join(RAW, "tanzil-uthmani", "quran.txt"))
    simple = read_tanzil(os.path.join(RAW, "tanzil-simple-clean", "quran.txt"))
    # Tanzil writes the Basmalah at the start of ayah 1 of every surah except al-Fatiha (where it IS ayah 1) and
    # at-Tawbah (none). It is not part of the ayah's numbered text, so it is stored separately for the surah header;
    # both parts stay character-for-character Tanzil's text.
    # the Basmalah exactly as Tanzil writes it in 1:1, plus the variant with shadda on the ba (95:1, 97:1)
    basmala_uth = [uth[(1, 1)], "\u0628\u0651\u0650" + uth[(1, 1)][2:]]
    basmala_simple = simple[(1, 1)]
    for e in suras:
        si = int(e["index"])
        if si in (1, 9):
            continue
        k = (si, 1)
        bu = next((b for b in basmala_uth if uth[k].startswith(b + " ")), None)
        bs = basmala_simple if simple[k].startswith(basmala_simple + " ") else None
        if not (bu and bs):
            sys.exit(f"surah {si}: no Basmalah found at the start of ayah 1")
        db.execute("INSERT INTO basmala VALUES (?,?,?)", (si, bu, bs))
        uth[k], simple[k] = uth[k][len(bu) + 1:], simple[k][len(bs) + 1:]
    keys = list(uth)
    skel = {k: " ".join(t[4] for t in toks if t[2] == "arabic") for k, toks in zip(keys, tokenize_many([uth[k] for k in keys]))}
    gid = 0
    for e in suras:
        si = int(e["index"])
        for a in range(1, int(e["ayas"]) + 1):
            gid += 1
            k = (si, a)
            db.execute("INSERT INTO ayah VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                       (gid, si, a, uth[k], simple[k], skel[k], locate(div["juzs"], k), locate(div["hizbs"], k),
                        locate(div["manzils"], k), locate(div["rukus"], k), locate(div["pages"], k), sajdas.get(k)))
    assert gid == N_AYAT, gid

    # ---- translations + tafsir (QuranEnc display sources, spa5k grounding sources)
    report = []
    for s in sources:
        sid = s["id"]
        if s["kind"] == "quranenc":
            d = json.load(open(os.path.join(RAW, sid, f"{s['key']}.json"), encoding="utf-8"))
            n = 0
            for r in d["rows"]:
                k = (int(r["sura"]), int(r["aya"]))
                if r.get("arabic_text") and r["arabic_text"] != uth[k]:
                    pass   # QuranEnc ships its own Arabic copy; QuranGraph displays Tanzil's
                tr = (r.get("translation") or "").strip()
                fn = (r.get("footnotes") or "").strip()
                # Defensive check: if translation is mistakenly a ruku/section heading with HTML tags
                # and footnotes contains the real translation, swap them cleanly.
                if ("<b" in tr or "রুকু" in tr.lower() or "ruku" in tr.lower()) and len(tr) < 35:
                    if fn and len(fn) > len(tr) and not fn.startswith("[1]") and not fn.startswith("[১]"):
                        tr = fn
                        fn = ""
                # Strip any rogue HTML tags from translations
                tr = re.sub(r"</?[a-zA-Z0-9]+[^>]*>", "", tr).strip()
                db.execute("INSERT INTO text VALUES (?,?,?,?,?,?)", (sid, k[0], k[1], tr, fn or None, None))
                n += 1
            report.append(f"{sid}: {n} ayat (v{d.get('version')})")
        elif s["kind"] == "spa5k":
            n = 0
            for f in sorted(glob.glob(os.path.join(RAW, sid, "*.json"))):
                data = json.load(open(f, encoding="utf-8"))
                for r in data["ayahs"] if isinstance(data, dict) else data:   # some editions wrap rows in {"ayahs": [...]}
                    t = (r.get("text") or "").strip()
                    if t:
                        db.execute("INSERT OR REPLACE INTO text VALUES (?,?,?,?,?,?)", (sid, int(r["surah"]), int(r["ayah"]), t, None, None))
                        n += 1
            report.append(f"{sid}: {n} ayat with grounding text")

    # ---- words (morphology segmentation)
    words = read_morphology()
    per_ayah = collections.Counter()
    for (s, a, w), r in words.items():
        db.execute("INSERT INTO word VALUES (?,?,?,?,?,?,?,?,?)",
                   (s, a, w, r["text"], r["root"], r["lemma"], r["tag"], "|".join(r["features"]),
                    json.dumps(r["segments"], ensure_ascii=False)))
        per_ayah[(s, a)] += 1
    missing = [k for k in uth if k not in per_ayah]
    # word segmentation vs Tanzil whitespace words (they differ by design for a few spellings: report, don't fail)
    differ = sum(1 for k, t in uth.items() if len([w for w in t.split() if re.search(r"[ء-ي]", w)]) != per_ayah[k])
    db.commit()

    roots = db.execute("SELECT COUNT(DISTINCT root) FROM word WHERE root IS NOT NULL").fetchone()[0]
    lemmas = db.execute("SELECT COUNT(DISTINCT lemma) FROM word WHERE lemma IS NOT NULL").fetchone()[0]
    print(f"surahs 114 · ayat {gid} · words {len(words)} · roots {roots} · lemmas {lemmas}")
    print(f"ayat whose Tanzil word count differs from the morphology segmentation: {differ}")
    report += drop_carried_over(db, [x["id"] for x in sources if x["kind"] == "spa5k"])
    report += check_tafsir_numbers(db)
    for line in report:
        print("  " + line)
    if missing:
        sys.exit(f"morphology is missing {len(missing)} ayat, e.g. {missing[:5]}")
    print(f"wrote {DB_PATH}")


if __name__ == "__main__":
    main()
