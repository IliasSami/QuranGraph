"""Download every source in sources.yaml into work/raw/<id>/ and record version + SHA-256 in sources.lock.json.

Idempotent: a source whose files already exist is skipped unless --force is given.
Usage:  uv run fetch/fetch.py              # everything missing
        uv run fetch/fetch.py --force qe-english-saheeh
        uv run fetch/fetch.py --check       # QuranEnc: report translations whose version changed (weekly CI job)
"""
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone

import requests
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "work", "raw")
LOCK = os.path.join(ROOT, "sources.lock.json")
SPA5K_COMMIT = "eb82bb6294efe30ad5c135c03b1864afaa70e855"   # pinned: github.com/spa5k/tafsir_api
UA = {"User-Agent": "QuranGraph-ingest/0.1 (+https://github.com/; contact via project owner)"}
SURAHS = range(1, 115)

session = requests.Session()
session.headers.update(UA)


def get(url, **kw):
    for attempt in range(5):
        try:
            r = session.get(url, timeout=60, **kw)
            if r.status_code == 200:
                return r
            if r.status_code in (429, 500, 502, 503, 504):
                time.sleep(2 ** attempt)
                continue
            r.raise_for_status()
        except requests.RequestException:
            if attempt == 4:
                raise
            time.sleep(2 ** attempt)
    raise RuntimeError(f"failed: {url}")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write(path, data: bytes):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)


_qe_list = None


def quranenc_versions():
    global _qe_list
    if _qe_list is None:
        r = get("https://quranenc.com/api/v1/translations/list")
        _qe_list = {t["key"]: t for t in r.json()["translations"]}
    return _qe_list


# ---------------------------------------------------------------------------------------------- per-kind fetchers
def fetch_tanzil_text(src, out):
    # Tanzil's default options (pause marks, sajda and rub signs; no extra tatweel before superscript alif)
    url = f"https://tanzil.net/pub/download/index.php?quranType={src['quranType']}&outType=txt-2&agree=true"
    # downloading through this URL accepts Tanzil's terms of use (verbatim copies, credit, link to tanzil.net)
    path = os.path.join(out, "quran.txt")
    write(path, get(url).content)
    return {"files": {"quran.txt": sha256(path)}, "version": "1.1"}


def fetch_url(src, out):
    path = os.path.join(out, src["file"])
    write(path, get(src["src"]).content)
    return {"files": {src["file"]: sha256(path)}}


def fetch_quranenc(src, out):
    key = src["key"]
    rows = []
    for s in SURAHS:
        rows += get(f"https://quranenc.com/api/v1/translation/sura/{key}/{s}").json()["result"]
        time.sleep(0.15)
    if len(rows) != 6236:
        raise RuntimeError(f"{key}: expected 6236 ayat, got {len(rows)}")
    meta = quranenc_versions().get(key, {})
    # some editions (Bangla, Mukhtasar, Muyassar) are not in QuranEnc's public list and publish no version number:
    # record a fingerprint of the text instead; the weekly --check compares sample surahs against it
    version = meta.get("version") or "unlisted-" + hashlib.sha256(json.dumps(rows, ensure_ascii=False).encode()).hexdigest()[:10]
    path = os.path.join(out, f"{key}.json")
    write(path, json.dumps({"key": key, "version": version, "last_update": meta.get("last_update"),
                            "title": meta.get("title"), "rows": rows}, ensure_ascii=False).encode())
    return {"files": {f"{key}.json": sha256(path)}, "version": version, "last_update": meta.get("last_update")}


def fetch_spa5k(src, out):
    slug = src["slug"]
    files = {}
    missing = []
    for s in SURAHS:
        url = f"https://raw.githubusercontent.com/spa5k/tafsir_api/{SPA5K_COMMIT}/tafsir/{slug}/{s}.json"
        r = session.get(url, timeout=60)
        if r.status_code == 404:
            missing.append(s)   # e.g. al-Wahidi reports no occasion for many surahs
            continue
        if r.status_code != 200:
            r = get(url)
        path = os.path.join(out, f"{s:03d}.json")
        write(path, r.content)
        files[f"{s:03d}.json"] = sha256(path)
    if len(missing) > 20 and not src.get("partial"):
        raise RuntimeError(f"{slug}: {len(missing)} surahs missing")
    return {"files": files, "version": SPA5K_COMMIT[:12], "missing_surahs": missing}


FETCHERS = {"tanzil_text": fetch_tanzil_text, "url": fetch_url, "quranenc": fetch_quranenc, "spa5k": fetch_spa5k}


def main():
    args = sys.argv[1:]
    sources = yaml.safe_load(open(os.path.join(ROOT, "sources.yaml"), encoding="utf-8"))
    lock = json.load(open(LOCK)) if os.path.exists(LOCK) else {}

    if "--check" in args:
        changed = 0
        for src in sources:
            if src["kind"] != "quranenc":
                continue
            old = lock.get(src["id"], {}).get("version")
            v = quranenc_versions().get(src["key"], {}).get("version")
            if v is None:
                # unlisted edition: compare a few surahs with the stored copy
                stored = json.load(open(os.path.join(RAW, src["id"], f"{src['key']}.json"), encoding="utf-8"))["rows"]
                by = {(r["sura"], r["aya"]): r["translation"] for r in stored}
                for sura in (1, 2, 36, 112):
                    live = get(f"https://quranenc.com/api/v1/translation/sura/{src['key']}/{sura}").json()["result"]
                    if any(by.get((r["sura"], r["aya"])) != r["translation"] for r in live):
                        v = "changed"
                        break
                else:
                    v = old
            if v != old:
                print(f"UPDATE {src['id']}: {old} -> {v}")
                changed += 1
        print(f"{changed} QuranEnc source(s) changed")
        sys.exit(1 if changed else 0)

    force = "--force" in args
    only = {a for a in args if not a.startswith("--")}
    for src in sources:
        sid = src["id"]
        if only and sid not in only:
            continue
        out = os.path.join(RAW, sid)
        if not force and sid in lock and os.path.isdir(out) and all(os.path.exists(os.path.join(out, f)) for f in lock[sid]["files"]):
            print(f"skip   {sid}")
            continue
        t0 = time.time()
        info = FETCHERS[src["kind"]](src, out)
        info.update({"fetched": datetime.now(timezone.utc).isoformat(timespec="seconds"), "use": src["use"],
                     "licence": src["licence"]})
        lock[sid] = info
        json.dump(lock, open(LOCK, "w"), ensure_ascii=False, indent=1, sort_keys=True)
        print(f"fetched {sid} ({len(info['files'])} files, {time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()
