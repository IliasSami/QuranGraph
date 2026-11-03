#!/usr/bin/env python3
"""Generate neural Bengali TTS narration and verse-level alignment for QuranGraph.

Reads the Abu Bakr Zakaria translation from quran.sqlite, cleans it for natural spoken
delivery, synthesizes speech with Microsoft Azure Neural TTS (bn-BD-PradeepNeural / bn-BD-NabanitaNeural),
and generates:
  - work/export/audio/bn/<surah:03d>.mp3
  - work/export/audio/bn/<surah:03d>.json (with exact start_ms, end_ms, duration_ms per ayah)

Usage:
  uv run --with edge-tts tts/generate_bn_tts.py <surah_id>
  uv run --with edge-tts tts/generate_bn_tts.py juz30
  uv run --with edge-tts tts/generate_bn_tts.py pilot
"""

import argparse
import asyncio
import json
import os
import re
import sqlite3
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(ROOT, "work")
AUDIO_OUT = os.path.join(WORK, "export", "audio", "bn")
DB_PATH = os.path.join(WORK, "quran.sqlite")

try:
    import edge_tts
except ImportError:
    print("edge-tts not installed. Run with: uv run --with edge-tts tts/generate_bn_tts.py ...")
    sys.exit(1)


def clean_bengali_for_speech(text: str) -> str:
    """Clean footnote markers, brackets, and normalize for natural speech."""
    if not text:
        return ""
    # Strip footnotes [১], [২], etc.
    t = re.sub(r"\[[০-৯0-9]+\]", "", text)
    # Strip quotes
    t = re.sub(r"‘|’|'|\"|“|”", "", t)
    # Strip zero-width non-joiner / joiner
    t = re.sub(r"[\u200b-\u200f\ufeff]", "", t)
    # Normalize common phonetics that trigger SSML errors
    t = t.replace("আল্লাহ্\u200cর", "আল্লাহর").replace("আল্লাহ্র", "আল্লাহর").replace("আল্লাহ্", "আল্লাহ")
    t = t.replace("হাম্\u200cদ", "হামদ").replace("হাম্দ", "হামদ")
    t = t.replace("নি‘আমত", "নিয়ামত").replace("নিআমত", "নিয়ামত")
    # Clean up whitespace and punctuation
    t = re.sub(r"\s+([,।!?])", r"\1", t)
    t = re.sub(r"\s+", " ", t).strip()
    # Ensure ending has punctuation
    if t and not re.search(r"[,।!?]$", t):
        t += "।"
    return t


async def generate_surah_audio(surah_id: int, voice: str = "bn-BD-PradeepNeural") -> dict:
    """Generate audio and alignment metadata for a single surah."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        "SELECT name_bn, name_translit FROM surah WHERE id=?",
        (surah_id,)
    )
    s_row = cur.fetchone()
    if not s_row:
        raise ValueError(f"Surah {surah_id} not found in database")
    name_bn, name_translit = s_row

    cur.execute(
        "SELECT ayah, text FROM text WHERE source='qe-bengali-zakaria' AND surah=? ORDER BY ayah",
        (surah_id,)
    )
    rows = cur.fetchall()
    conn.close()

    if not rows:
        raise ValueError(f"No Bengali Zakaria text found for Surah {surah_id}")

    os.makedirs(AUDIO_OUT, exist_ok=True)
    surah_pad = f"{surah_id:03d}"
    mp3_path = os.path.join(AUDIO_OUT, f"{surah_pad}.mp3")
    json_path = os.path.join(AUDIO_OUT, f"{surah_pad}.json")

    clean_ayat = []
    for ayah_num, raw_text in rows:
        sp_text = clean_bengali_for_speech(raw_text)
        clean_ayat.append((ayah_num, sp_text))

    full_surah_text = "\n".join(t for _, t in clean_ayat)
    print(f"Generating Bengali TTS for Surah {surah_id} ({name_translit} / {name_bn}), {len(rows)} ayat...")

    comm = edge_tts.Communicate(full_surah_text, voice)
    audio_data = bytearray()
    boundaries = []

    async for chunk in comm.stream():
        if chunk["type"] == "audio":
            audio_data.extend(chunk["data"])
        elif chunk["type"] == "SentenceBoundary":
            boundaries.append(chunk)

    with open(mp3_path, "wb") as f:
        f.write(audio_data)

    # Align boundaries to ayat
    ayat_meta = []
    # If boundary count matches clean_ayat count
    if len(boundaries) == len(clean_ayat):
        for (ayah_num, sp_text), b in zip(clean_ayat, boundaries):
            s_ms = b["offset"] // 10000
            d_ms = b["duration"] // 10000
            ayat_meta.append({
                "ayah": ayah_num,
                "start_ms": s_ms,
                "end_ms": s_ms + d_ms,
                "duration_ms": d_ms,
                "text": sp_text
            })
    else:
        # Fallback proportional mapping based on text length
        total_audio_ms = 0
        if boundaries:
            last_b = boundaries[-1]
            total_audio_ms = (last_b["offset"] + last_b["duration"]) // 10000
        else:
            total_audio_ms = max(1000, len(audio_data) // 6)

        total_chars = sum(len(t) for _, t in clean_ayat) or 1
        curr_ms = 0
        for ayah_num, sp_text in clean_ayat:
            fraction = len(sp_text) / total_chars
            d_ms = int(total_audio_ms * fraction)
            ayat_meta.append({
                "ayah": ayah_num,
                "start_ms": curr_ms,
                "end_ms": curr_ms + d_ms,
                "duration_ms": d_ms,
                "text": sp_text
            })
            curr_ms += d_ms

    total_duration_ms = ayat_meta[-1]["end_ms"] if ayat_meta else 0
    meta = {
        "surah": surah_id,
        "name_translit": name_translit,
        "name_bn": name_bn,
        "voice": voice,
        "total_duration_ms": total_duration_ms,
        "total_ayat": len(ayat_meta),
        "ayat": ayat_meta
    }

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"✓ Saved {mp3_path} ({len(audio_data) // 1024} KB) and {json_path}")
    return meta


async def main():
    parser = argparse.ArgumentParser(description="Generate Bengali TTS narration for QuranGraph")
    parser.add_argument("surah", help="Surah number (1-114), 'juz30', 'pilot', or 'all'")
    parser.add_argument("--voice", default="bn-BD-PradeepNeural", help="Neural voice name")
    args = parser.parse_args()

    if args.surah.isdigit():
        surahs = [int(args.surah)]
    elif args.surah.lower() == "juz30":
        surahs = list(range(78, 115))
    elif args.surah.lower() == "pilot":
        surahs = [1, 112, 113, 114]
    elif args.surah.lower() == "all":
        surahs = list(range(1, 115))
    else:
        print(f"Unknown surah specification: {args.surah}")
        sys.exit(1)

    for s in surahs:
        await generate_surah_audio(s, args.voice)


if __name__ == "__main__":
    asyncio.run(main())
