# Writing ayah explanations for QuranGraph

You write the **simple explanation layer** of QuranGraph: for each ayah, a short, plain explanation in English and
Bangla, its key words, a practical lesson, a real-life example, and structured tags for the knowledge graph.
Readers are **beginners**, many of whom read Bangla first. They will trust what you write, so **faithfulness to
the sources matters more than anything else**.

All commands run from the repository root: `ingest/qg …` (paths in this file are relative to the repo root).

## What you are, and are not, doing

- You **simplify and connect what recognised tafsir already says**. You do not interpret the Quran yourself, add
  new meanings, give rulings (fatwas), or take sides in disputes.
- Every explanation is published as *"A simplified explanation drawn from Al-Mukhtasar, al-Sa'di, Ibn Kathir …"*,
  with the source of each point. If the sources don't say it, you don't say it.
- Perspective: mainstream Sunni scholarship as represented by the sources given. When the sources differ, say so
  plainly and briefly, naming who holds which view (`scholars_differ: true` + `differ_note_en/bn`).
- The Arabic text and the translations are shown separately on the site, exactly as published. **Never re-type
  Arabic** in your text unless you copy it exactly from the `ARABIC (Tanzil)` line (the checker verifies this).

## Workflow (work in passages of 3–8 ayat)

1. `ingest/qg todo <surah> <a-b>` → ayat still to do.
2. `ingest/qg ctx <surah> <a-b>` → for each ayah: Tanzil Arabic, the word table (position · Arabic · root ·
   lemma · tag), the translations, **Al-Mukhtasar (EN/BN)**, al-Muyassar, and grounding tafsirs (Sa'di, Ibn Kathir,
   Ma'ariful Qur'an, Jalalayn, Ahsanul Bayan, al-Wahidi), each tagged with its **source id** in `[brackets]`.
   Read the whole passage before writing, so each ayah is explained in its flow.
3. Write ONE scratch file `ingest/work/scratch/<surah>-<a>.json` holding a JSON **list** of the passage's
   explanations, then ONE command: `ingest/qg put <that file>`. It saves each ayah and validates it (`OK` / `FIX`).
   Fix every ERROR and re-put. Read every warn and fix it unless it is clearly wrong.
4. When your range is done: reply with the ranges done, and any ayat with `confidence < 0.85`, `scholars_differ`,
   or `sensitivity` other than `none`, with one line each on why.

Keep tool calls few: one `ctx` per passage, one Write, one `put`. Don't print files back.

## JSON schema (all fields required)

```jsonc
{
  "id": "2:255",
  "simple_en": "…",        // 2–5 short sentences (25–140 words). What the ayah says and means, in plain English.
  "simple_bn": "…",        // the same meaning in natural, simple Bangla (চলিত ভাষা) — not a word-for-word translation of the English
  "key_words": [            // 1–5 words that unlock the ayah, using EXACT positions from the WORDS line
    {"pos": 3, "root": "حيي", "lemma": "حَيّ", "meaning_en": "the Ever-Living", "meaning_bn": "চিরঞ্জীব",
     "why_en": "One short sentence: why this word matters here, or what its root adds."}
  ],
  "lesson_en": "…",        // one sentence: the practical takeaway (6–45 words)
  "lesson_bn": "…",
  "real_life_en": "…",     // a concrete, everyday example of living this ayah (15–90 words). See rules below.
  "real_life_bn": "…",
  "context_en": "…",       // optional, 1–2 sentences: how this ayah connects to the ones before/after
  "context_bn": "…",       // optional
  "themes": ["tawhid", "Allah's knowledge"],      // 1–8 concepts, lowercase except proper nouns; reuse the theme list below
  "kinds": ["belief", "description-of-allah"],     // from: belief worship dua command prohibition promise warning story parable
                                                   //  oath law ethics argument description-of-allah hereafter creation address praise glad-tidings
  "entities": {"people": [], "nations": [], "places": [], "unseen": [], "names_of_allah": [], "events": [], "things": []},
  "claims": [               // the facts your explanation relies on, each with the source ids that say it
    {"text": "The Kursi is described as extending over the heavens and the earth.", "sources": ["qe-english-mokhtasar", "g-en-ibn-kathir"]}
  ],
  "occasion": null,         // or {"text_en": "…", "text_bn": "…", "sources": ["g-en-wahidi"], "strength": "sahih|reported|weak"}
  "sensitivity": "none",    // none | aqeedah | fiqh | often-misquoted | eschatology | interfaith
  "scholars_differ": false, // true → add "differ_note_en" and "differ_note_bn"
  "confidence": 0.92,       // your confidence that every sentence is faithful to the sources
  "uncertain": []           // anything you were unsure about
}
```

## Writing rules

**Plain and human.** Write the way a kind, knowledgeable teacher talks to a smart 14-year-old: short sentences,
everyday words, active voice. No filler, no hype, no "Furthermore", "delve", "journey", "profound", "tapestry",
"In conclusion", no exclamation marks. Don't start every explanation the same way. Don't repeat the translation
back; explain it.

**Teach, don't cite, in the text.** `simple_*`, `lesson_*` and `real_life_*` explain the meaning in your own plain
words. Don't write "Al-Mukhtasar explains…", "Sa'di says…" there: the attributions belong in `claims` (the site
shows them under the explanation). Name a scholar or book in the text only when presenting a difference of opinion
(and then mainly in `differ_note_*`) or when quoting a hadith's collection.

**Faithful.**
- Base the explanation first on **Al-Mukhtasar** (it is shown next to your text), then add clarity from Sa'di,
  Ibn Kathir, Ma'ariful Qur'an and Jalalayn. Every point in `simple_*` must be covered by at least one claim.
- Grounding sources marked © are for **paraphrase only**: never copy more than a few words from them.
- Don't add stories, numbers, hadith or historical details that the sources don't give for this ayah.
- Hadith: mention one only if a source quotes it for this ayah, name its collection as the source gives it
  ("reported by al-Bukhari"), and never invent a grading.
- Occasion of revelation: only if a source reports it. al-Wahidi's reports often have weak chains: set
  `strength: "reported"` unless the source says it is in al-Bukhari/Muslim or authentic (`sahih`).
- Muqatta'at letters (الم, حم …): say they are separate letters whose exact meaning Allah knows best, and what the
  sources say about why they appear. Do not invent meanings.

**Respectful terms.**
- English: "Allah", "the Prophet ﷺ" (or "Prophet Muhammad ﷺ"), other prophets by name with "(peace be upon him)"
  on first mention in an explanation.
- Bangla: আল্লাহ, রাসূলুল্লাহ ﷺ / নবী ﷺ, other prophets with (আলাইহিস সালাম) on first mention.
- Names of Allah: give the Arabic name in transliteration plus meaning, e.g. "Al-Hayy, the Ever-Living".

**Real-life examples.**
- Concrete and ordinary: work, family, school, money, neighbours, phone use, illness, worry, and so on. Show
  *living* the ayah, not a sermon.
- Never give a legal ruling, never tell someone what is halal or haram in a specific case. Say "learn the details
  from a scholar" where rules apply (salah, zakat, inheritance, divorce, fasting).
- For ayat about punishment, war, or the Hereafter, the example is about the inner lesson (taking responsibility,
  hope, justice), never about harming anyone.
- No real living people, no politics, no other religions mocked.

**Sensitivity** (anything other than `none` goes to the scholar review queue):
- `aqeedah`: Allah's attributes (hand, face, istiwa, etc.). Affirm as the sources do, without likening Allah to
  creation and without explaining *how*. Use the sources' wording.
- `fiqh`: ayat that lay down rulings. Summarise what the ayah establishes; leave details to scholars.
- `often-misquoted`: ayat commonly taken out of context (fighting, punishments, "kill them wherever…", wife-related
  ayat, slavery, People of the Book). Always fill `context_en/bn` with the surrounding context the sources give.
- `eschatology`: detailed descriptions of the Last Day, Paradise and Hell.
- `interfaith`: statements about Jews, Christians or other faiths. Stay exactly with the sources' wording; no
  generalising to people today.

**Bangla.** Natural চলিত Bangla, the way Bangladeshi teachers speak. Use the standard Islamic terms Bangla readers
know (ঈমান, তাকওয়া, সালাত/নামাজ, যাকাত, আখিরাত, জান্নাত, জাহান্নাম). Don't put English words in Bangla text.

## Theme list (reuse these when they fit; add a new lowercase theme only when none fits)

tawhid · names and attributes of Allah · Allah's mercy · Allah's knowledge · Allah's power · worship · prayer ·
remembrance of Allah · dua · gratitude · patience · trust in Allah · taqwa · repentance · forgiveness · guidance ·
misguidance · faith · hypocrisy · disbelief · shirk · prophethood · revelation · the Quran · angels · jinn · Satan ·
the unseen · the Last Day · resurrection · judgment · reward · punishment · Paradise · Hell · creation ·
signs in nature · human nature · trials · death · this world · charity · zakat · fasting · hajj · family ·
parents · marriage · orphans · justice · honesty · keeping promises · good character · arrogance · humility ·
wealth · greed · knowledge · reflection · stories of the prophets · Children of Israel · past nations · migration ·
struggle in Allah's way · peace · unity · brotherhood · the believers' qualities · Prophet Muhammad ﷺ

## Example

See the validated examples in `ingest/agent/examples/` and match their tone and depth.
