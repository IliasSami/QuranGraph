"""`ingest/qg`: the helper used while writing ayah explanations (by Claude Code or the Batch pipeline).

  ingest/qg ctx   <surah> <a-b>          everything needed to explain these ayat: Arabic, words (root/lemma), translations,
                                          Mukhtasar, Muyassar and the grounding tafsirs, each tagged with its source id
  ingest/qg word  <surah> <ayah>          word table for one ayah (position, Arabic, root, lemma, part of speech)
  ingest/qg root  <root> [...]            occurrences of a root: count, lemmas, a few ayat
  ingest/qg put   <file.json>             write one explanation or a JSON list of them, then validate
  ingest/qg check <surah> [a-b|all]       validate explanation files
  ingest/qg todo  <surah> [a-b|all]       ayat still without a valid explanation
  ingest/qg warned <surah> "<text>"       ayat whose validator warnings contain <text> (e.g. "names a tafsir")
  ingest/qg stats                         progress + review queue counts
"""
import json
import os
import re
import sqlite3
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(ROOT, "work")
EXPLAIN = os.path.join(ROOT, "content", "explain")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schema import validate  # noqa: E402

_db = None

# order in which sources are shown in `ctx` (display sources first, then grounding)
CTX_SOURCES = [
    ("qe-english-saheeh", "TRANSLATION · Saheeh International", None),
    ("qe-bengali-zakaria", "TRANSLATION · Bangla · Abu Bakr Zakaria", None),
    ("qe-english-mokhtasar", "TAFSIR · Al-Mukhtasar (English)", None),
    ("qe-bengali-mokhtasar", "TAFSIR · Al-Mukhtasar (Bangla)", None),
    ("qe-arabic-moyassar", "TAFSIR · al-Muyassar (Arabic)", None),
    # limits are per PASSAGE (the mirrors store one passage under every ayah it covers; it is printed once)
    ("g-ar-saadi", "GROUNDING · al-Sa'di (Arabic)", 3500),
    ("g-en-ibn-kathir", "GROUNDING · Ibn Kathir abridged (English, ©, paraphrase only)", 9000),
    ("g-en-maarif", "GROUNDING · Ma'ariful Qur'an (English, ©, paraphrase only)", 4000),
    ("g-en-jalalayn", "GROUNDING · Jalalayn (English, ©, paraphrase only)", 1200),
    ("g-bn-ahsanul-bayan", "GROUNDING · Ahsanul Bayan (Bangla, ©, paraphrase only)", 2000),
]


def db():
    global _db
    if _db is None:
        _db = sqlite3.connect(os.path.join(WORK, "quran.sqlite"))
    return _db


def ayah_count(s):
    return db().execute("SELECT ayat FROM surah WHERE id=?", (s,)).fetchone()[0]


def rng(s, spec="all"):
    n = ayah_count(s)
    if spec == "all":
        return list(range(1, n + 1))
    if "-" in spec:
        a, b = spec.split("-")
        return list(range(int(a), min(int(b), n) + 1))
    return [int(spec)]


def path(s, a):
    return os.path.join(EXPLAIN, f"{s:03d}", f"{a:03d}.json")


def clean(t):
    t = re.sub(r"<[^>]+>", "", t or "")
    return re.sub(r"[ \t]+", " ", t).strip()


def grounding_text(src, s, a):
    """Grounding text for an ayah and the first ayah of the passage it belongs to (the mirrors repeat a passage's
    text under every ayah it covers)."""
    row = db().execute("SELECT text FROM text WHERE source=? AND surah=? AND ayah=?", (src, s, a)).fetchone()
    if not row or not row[0].strip():
        return (None, None)
    first = a
    while first > 1:
        prev = db().execute("SELECT text FROM text WHERE source=? AND surah=? AND ayah=?", (src, s, first - 1)).fetchone()
        if not prev or prev[0] != row[0]:
            break
        first -= 1
    return (row[0], first)


def words(s, a):
    return db().execute("SELECT pos, text, root, lemma, tag, features FROM word WHERE surah=? AND ayah=? ORDER BY pos", (s, a)).fetchall()


# ----------------------------------------------------------------------------------------------------- ctx
def ctx(s, spec):
    sr = db().execute("SELECT name_ar, name_translit, name_en, type, revelation_order, ayat FROM surah WHERE id=?", (s,)).fetchone()
    print(f"##### SURAH {s} {sr[1]} ({sr[0]}, \"{sr[2]}\") · {sr[3]} · revelation order {sr[4]} · {sr[5]} ayat")
    shown_grounding = set()
    for a in rng(s, spec):
        row = db().execute("SELECT text_uthmani, juz, page, sajda FROM ayah WHERE surah=? AND ayah=?", (s, a)).fetchone()
        print(f"\n=== {s}:{a}   (juz {row[1]}, page {row[2]}{', SAJDA ' + row[3] if row[3] else ''})")
        print(f"ARABIC (Tanzil): {row[0]}")
        print("WORDS (pos · arabic · root · lemma · tag):  " + " | ".join(
            f"{p}·{t}·{r or '-'}·{lm or '-'}·{tg}" for p, t, r, lm, tg, _ in words(s, a)))
        for src, label, limit in CTX_SOURCES:
            if src.startswith("g-"):
                text, at = grounding_text(src, s, a)
                if not text:
                    continue
                key = (src, at)
                if key in shown_grounding:
                    print(f"[{src}] (see {s}:{at} above)")
                    continue
                shown_grounding.add(key)
                t = clean(text)
                note = f" (passage starting {s}:{at})" if at != a else ""
                print(f"[{src}] {label}{note}:\n  {t[:limit]}{' …[truncated]' if len(t) > limit else ''}")
            else:
                r = db().execute("SELECT text, footnotes, note FROM text WHERE source=? AND surah=? AND ayah=?", (src, s, a)).fetchone()
                if r and (r[2] or "").startswith("misaligned"):
                    print(f"[{src}] {label}: NOT AVAILABLE — the source files another ayah's explanation here "
                          f"({r[2].split(':', 1)[1]}); do not use or cite it for this ayah")
                elif r:
                    print(f"[{src}] {label}: {clean(r[0])}")
                    if r[1] and src == "qe-bengali-zakaria":
                        print(f"  footnotes: {clean(r[1])[:1500]}")
        prev = path(s, a - 1)
        if a > 1 and os.path.exists(prev):
            try:
                print("PREVIOUS AYAH (your explanation):", json.load(open(prev, encoding="utf-8"))["simple_en"][:300])
            except Exception:
                pass


def word_cmd(s, a):
    for p, t, r, lm, tg, f in words(s, a):
        print(f"{p:>3}  {t:<18} root={r or '-':<6} lemma={lm or '-':<12} {tg} {f}")


def root_cmd(*roots):
    for r in roots:
        rows = db().execute("SELECT surah, ayah, text, lemma FROM word WHERE root=?", (r,)).fetchall()
        lem = {}
        for _, _, _, lm in rows:
            lem[lm] = lem.get(lm, 0) + 1
        print(f"root {r}: {len(rows)} occurrences in {len({(x[0], x[1]) for x in rows})} ayat; lemmas: " +
              ", ".join(f"{k} ({v})" for k, v in sorted(lem.items(), key=lambda x: -x[1])))
        print("  e.g. " + ", ".join(f"{x[0]}:{x[1]} {x[2]}" for x in rows[:8]))


# ----------------------------------------------------------------------------------------------------- put / check
def put(p):
    data = json.load(open(p, encoding="utf-8"))
    items = data if isinstance(data, list) else [data]
    for d in items:
        s, a = map(int, d["id"].split(":"))
        os.makedirs(os.path.dirname(path(s, a)), exist_ok=True)
        json.dump(d, open(path(s, a), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        errs, warns = validate(d, db())
        status = "OK " if not errs else "FIX"
        print(f"{status} {d['id']}" + ("" if not (errs or warns) else ""))
        for e in errs:
            print("   ERROR", e)
        for w in warns:
            print("   warn ", w)


def check(s, spec="all"):
    ok = bad = 0
    for a in rng(s, spec):
        p = path(s, a)
        if not os.path.exists(p):
            continue
        errs, warns = validate(json.load(open(p, encoding="utf-8")), db())
        if errs or warns:
            print(f"{s}:{a}")
            for e in errs:
                print("   ERROR", e)
            for w in warns:
                print("   warn ", w)
        ok += not errs
        bad += bool(errs)
    print(f"{ok} valid, {bad} with errors")


def todo(s, spec="all"):
    left = []
    for a in rng(s, spec):
        p = path(s, a)
        if not os.path.exists(p) or validate(json.load(open(p, encoding="utf-8")), db())[0]:
            left.append(a)
    print("all done" if not left else compress(left))


def warned(s, needle):
    hits = []
    for a in rng(s):
        p = path(s, a)
        if os.path.exists(p) and any(needle in w for w in validate(json.load(open(p, encoding="utf-8")), db())[1]):
            hits.append(a)
    print(f"{s}: {compress(hits)}" if hits else f"{s}: none")


def compress(nums):
    out, start = [], None
    for i, n in enumerate(nums):
        if start is None:
            start = n
        if i + 1 == len(nums) or nums[i + 1] != n + 1:
            out.append(f"{start}" if start == n else f"{start}-{n}")
            start = None
    return " ".join(out)


def stats():
    done = review = 0
    flags = {}
    for p in sorted(os.listdir(EXPLAIN)) if os.path.isdir(EXPLAIN) else []:
        for f in os.listdir(os.path.join(EXPLAIN, p)):
            d = json.load(open(os.path.join(EXPLAIN, p, f), encoding="utf-8"))
            done += 1
            if d.get("sensitivity", "none") != "none" or d.get("confidence", 1) < 0.85 or d.get("scholars_differ"):
                review += 1
            flags[d.get("sensitivity", "none")] = flags.get(d.get("sensitivity", "none"), 0) + 1
    print(f"explained {done}/6236 ayat · review queue {review} · by sensitivity {flags}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == "ctx":
        ctx(int(args[0]), args[1] if len(args) > 1 else "all")
    elif cmd == "word":
        word_cmd(int(args[0]), int(args[1]))
    elif cmd == "root":
        root_cmd(*args)
    elif cmd == "put":
        put(args[0])
    elif cmd == "check":
        check(int(args[0]), args[1] if len(args) > 1 else "all")
    elif cmd == "todo":
        todo(int(args[0]), args[1] if len(args) > 1 else "all")
    elif cmd == "warned":
        warned(int(args[0]), args[1])
    elif cmd == "stats":
        stats()
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
