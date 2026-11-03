"""Python access to the one shared text normaliser (web/src/lib/search/normalize.ts), run through Node.

    from core.normalize import tokenize_many
    tokenize_many(["ٱلرَّحْمَٰنِ", "দয়াময়"])  ->  [[(term, surface, script, stop, skeleton), ...], ...]
"""
import json
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CLI = os.path.join(ROOT, "web", "scripts", "normalize-cli.ts")


def tokenize_many(texts, batch=5000):
    out = []
    for i in range(0, len(texts), batch):
        r = subprocess.run(["node", CLI], input=json.dumps(texts[i:i + batch], ensure_ascii=False),
                           capture_output=True, text=True, check=True)
        out += [[tuple(t) for t in toks] for toks in json.loads(r.stdout)]
    return out


def arabic_skeleton(text):
    """Space-joined Arabic skeleton keys of a text (Uthmani and simple spellings compare equal)."""
    return " ".join(t[4] for t in tokenize_many([text])[0] if t[2] == "arabic")
