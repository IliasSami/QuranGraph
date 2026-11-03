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


def truncate_at_sentence(t, limit):
    """Cut text at a sentence or word boundary within limit, never mid-word."""
    if not limit or len(t) <= limit:
        return t, False
    sub = t[:limit]
    matches = list(re.finditer(r"[।?!.](\s+|$)", sub))
    if matches and matches[-1].end() >= int(limit * 0.6):
        cut = matches[-1].end()
        return t[:cut].rstrip(), True
    space_idx = sub.rfind(" ")
    if space_idx >= int(limit * 0.8):
        return t[:space_idx].rstrip(), True
    return sub.rstrip(), True


def grounding_text(src, s, a):
    """Grounding text for an ayah, the first ayah of the passage, and the passage length in ayat (the mirrors
    repeat a passage's text under every ayah it covers)."""
    row = db().execute("SELECT text FROM text WHERE source=? AND surah=? AND ayah=?", (src, s, a)).fetchone()
    if not row or not row[0].strip():
        return (None, None, 0)
    txt = row[0]
    first = a
    while first > 1:
        prev = db().execute("SELECT text FROM text WHERE source=? AND surah=? AND ayah=?", (src, s, first - 1)).fetchone()
        if not prev or prev[0] != txt:
            break
        first -= 1
    n = ayah_count(s)
    last = a
    while last < n:
        nxt = db().execute("SELECT text FROM text WHERE source=? AND surah=? AND ayah=?", (src, s, last + 1)).fetchone()
        if not nxt or nxt[0] != txt:
            break
        last += 1
    return (txt, first, last - first + 1)


def words(s, a):
    return db().execute("SELECT pos, text, root, lemma, tag, features FROM word WHERE surah=? AND ayah=? ORDER BY pos", (s, a)).fetchall()


# ----------------------------------------------------------------------------------------------------- ctx
def ctx(s, spec):
    sr = db().execute("SELECT name_ar, name_translit, name_en, type, revelation_order, ayat, name_bn FROM surah WHERE id=?", (s,)).fetchone()
    print(f"##### SURAH {s} {sr[1]} / {sr[6]} ({sr[0]}, \"{sr[2]}\") · {sr[3]} · revelation order {sr[4]} · {sr[5]} ayat")
    shown_grounding = set()
    for a in rng(s, spec):
        row = db().execute("SELECT text_uthmani, juz, page, sajda FROM ayah WHERE surah=? AND ayah=?", (s, a)).fetchone()
        print(f"\n=== {s}:{a}   (juz {row[1]}, page {row[2]}{', SAJDA ' + row[3] if row[3] else ''})")
        print(f"ARABIC (Tanzil): {row[0]}")
        print("WORDS (pos · arabic · root · lemma · tag):  " + " | ".join(
            f"{p}·{t}·{r or '-'}·{lm or '-'}·{tg}" for p, t, r, lm, tg, _ in words(s, a)))
        for src, label, limit in CTX_SOURCES:
            if src.startswith("g-"):
                text, at, passage_len = grounding_text(src, s, a)
                if not text:
                    continue
                key = (src, at)
                if key in shown_grounding:
                    print(f"[{src}] (see {s}:{at} above)")
                    continue
                shown_grounding.add(key)
                t = clean(text)
                note = f" (passage starting {s}:{at})" if at != a else ""
                cur_limit = limit
                if src == "g-en-ibn-kathir" and passage_len > 8:
                    cur_limit = max(limit or 9000, passage_len * 1500)
                cut, trunc = truncate_at_sentence(t, cur_limit)
                print(f"[{src}] {label}{note}:\n  {cut}{' …[truncated]' if trunc else ''}")
            else:
                r = db().execute("SELECT text, footnotes, note FROM text WHERE source=? AND surah=? AND ayah=?", (src, s, a)).fetchone()
                if r and (r[2] or "").startswith("misaligned"):
                    print(f"[{src}] {label}: NOT AVAILABLE — the source files another ayah's explanation here "
                          f"({r[2].split(':', 1)[1]}); do not use or cite it for this ayah")
                elif r:
                    print(f"[{src}] {label}: {clean(r[0])}")
                    if r[1] and src == "qe-bengali-zakaria":
                        fn_cut, fn_trunc = truncate_at_sentence(clean(r[1]), 3000)
                        print(f"  footnotes: {fn_cut}{' …[truncated]' if fn_trunc else ''}")
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
    if s == "all":
        surahs = sorted(int(d) for d in os.listdir(EXPLAIN) if d.isdigit() and os.path.isdir(os.path.join(EXPLAIN, d)))
        total_ok = total_bad = 0
        for num in surahs:
            for a in rng(num, "all"):
                p = path(num, a)
                if not os.path.exists(p):
                    continue
                errs, warns = validate(json.load(open(p, encoding="utf-8")), db())
                if errs or warns:
                    print(f"{num}:{a}")
                    for e in errs:
                        print("   ERROR", e)
                    for w in warns:
                        print("   warn ", w)
                total_ok += not errs
                total_bad += bool(errs)
        print(f"Total: {total_ok} valid, {total_bad} with errors")
        if total_bad:
            sys.exit(1)
        return
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
    if bad:
        sys.exit(1)


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


def review_priority(d):
    """Classify review priority: 'must', 'sample', or None.
    - 'must': aqeedah, fiqh, often-misquoted, interfaith, confidence < 0.88, scholars_differ on aqeedah.
    - 'sample': eschatology only.
    """
    sens = d.get("sensitivity", "none")
    conf = float(d.get("confidence", 1))
    diff = bool(d.get("scholars_differ"))
    if (sens in {"aqeedah", "fiqh", "often-misquoted", "interfaith"} or
            conf < 0.88 or
            (diff and (sens == "aqeedah" or "aqeedah" in d.get("themes", [])))):
        return "must"
    if sens == "eschatology":
        return "sample"
    return None


def stats():
    done = 0
    must_n = sample_n = 0
    flags = {}
    for p in sorted(os.listdir(EXPLAIN)) if os.path.isdir(EXPLAIN) else []:
        for f in os.listdir(os.path.join(EXPLAIN, p)):
            d = json.load(open(os.path.join(EXPLAIN, p, f), encoding="utf-8"))
            done += 1
            prio = review_priority(d)
            if prio == "must":
                must_n += 1
            elif prio == "sample":
                sample_n += 1
            flags[d.get("sensitivity", "none")] = flags.get(d.get("sensitivity", "none"), 0) + 1
    print(f"explained {done}/6236 ayat · review queue {must_n + sample_n} ({must_n} must-review, {sample_n} sample) · by sensitivity {flags}")


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
        if args and args[0] == "all":
            check("all")
        else:
            check(int(args[0]), args[1] if len(args) > 1 else "all")
    elif cmd == "todo":
        todo(int(args[0]), args[1] if len(args) > 1 else "all")
    elif cmd == "warned":
        warned(int(args[0]), args[1])
    elif cmd == "stats":
        stats()
    elif cmd in ("review-app", "review"):
        import review_server as rs
        rs.main()
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
