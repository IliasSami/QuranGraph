#!/usr/bin/env python3
"""
Build high-precision Quranic Top Lemmas & Vocabulary Lab Dataset.
Enriches lemmas from quran.sqlite and corpus.json with:
- Academic transliteration
- English & Bengali vocabulary meanings
- Grammatical Part-of-Speech categorization
- Triliteral roots & occurrence counts
- Anchor verses with Arabic, English, and Bengali text
"""

import json
import sqlite3
import os

LEMMA_METADATA = {
    "مِن": {
        "translit": "min",
        "en": "from / of / among",
        "bn": "হতে / থেকে / মধ্য থেকে",
        "pos": "preposition",
        "pos_label": "Preposition (হরফ)",
        "sample": "1:6"
    },
    "اللَّه": {
        "translit": "Allāh",
        "en": "Allah (The One True God)",
        "bn": "আল্লাহ (একমাত্র উপাস্য)",
        "pos": "noun",
        "pos_label": "Proper Divine Name (ইসমে জালালাত)",
        "sample": "112:1"
    },
    "ما": {
        "translit": "mā",
        "en": "what / that which / not",
        "bn": "যা / যা কিছু / না",
        "pos": "particle",
        "pos_label": "Relative / Negative Particle (অব্যয়)",
        "sample": "2:255"
    },
    "فِي": {
        "translit": "fī",
        "en": "in / inside / concerning",
        "bn": "মধ্যে / ভিতরে / বিষয়ে",
        "pos": "preposition",
        "pos_label": "Preposition (হরফ)",
        "sample": "2:255"
    },
    "لا": {
        "translit": "lā",
        "en": "no / not / neither",
        "bn": "না / নেই",
        "pos": "particle",
        "pos_label": "Negative Particle (না-বোধক হরফ)",
        "sample": "2:255"
    },
    "إِنّ": {
        "translit": "inna",
        "en": "indeed / surely / truly",
        "bn": "নিশ্চয়ই / নিঃসন্দেহে",
        "pos": "particle",
        "pos_label": "Emphatic Particle (নিশ্চয়তাবোধক হরফ)",
        "sample": "2:20"
    },
    "قالَ": {
        "translit": "qāla",
        "en": "he said / uttered",
        "bn": "সে বলল / বলল",
        "pos": "verb",
        "pos_label": "Form I Verb (ক্রিয়া)",
        "sample": "12:4"
    },
    "الَّذِي": {
        "translit": "alladhī",
        "en": "the one who / which / that",
        "bn": "যিনি / যা / যে ব্যক্তি",
        "pos": "pronoun",
        "pos_label": "Relative Pronoun (সম্বন্ধসূচক সর্বনাম)",
        "sample": "1:7"
    },
    "عَلَى": {
        "translit": "‘alā",
        "en": "upon / on / over",
        "bn": "উপরে / প্রতি",
        "pos": "preposition",
        "pos_label": "Preposition (হরফ)",
        "sample": "2:5"
    },
    "كانَ": {
        "translit": "kāna",
        "en": "was / has always been",
        "bn": "ছিল / সর্বদা বিরাজমান",
        "pos": "verb",
        "pos_label": "Defective Verb (ক্রিয়া)",
        "sample": "4:96"
    },
    "ذا": {
        "translit": "dhā",
        "en": "this / owner of / possessor",
        "bn": "এই / অধিকারী",
        "pos": "pronoun",
        "pos_label": "Demonstrative / Possessive (ইশারা / সম্বন্ধ)",
        "sample": "2:255"
    },
    "رَبّ": {
        "translit": "rabb",
        "en": "Lord / Sustainer / Cherisher",
        "bn": "রব্ব / প্রতিপালক / প্রভু",
        "pos": "noun",
        "pos_label": "Primary Noun (বিশেষ্য)",
        "sample": "1:2"
    },
    "مَن": {
        "translit": "man",
        "en": "who / whoever / anyone",
        "bn": "কে / যে / যে ব্যক্তি",
        "pos": "pronoun",
        "pos_label": "Interrogative / Conditional Pronoun",
        "sample": "2:255"
    },
    "إِلَى": {
        "translit": "ilā",
        "en": "to / towards / until",
        "bn": "দিকে / প্রতি / পর্যন্ত",
        "pos": "preposition",
        "pos_label": "Preposition (হরফ)",
        "sample": "2:28"
    },
    "إِن": {
        "translit": "in",
        "en": "if / in case",
        "bn": "যদি / যদি না",
        "pos": "particle",
        "pos_label": "Conditional Particle (শর্তসূচক হরফ)",
        "sample": "2:24"
    },
    "إِلّا": {
        "translit": "illā",
        "en": "except / save / but",
        "bn": "ব্যতীত / ছাড়া / কেবল",
        "pos": "particle",
        "pos_label": "Exceptive Particle (ব্যতিক্রমবোধক হরফ)",
        "sample": "2:255"
    },
    "أَن": {
        "translit": "an",
        "en": "that / to",
        "bn": "যে / যাতে",
        "pos": "particle",
        "pos_label": "Subordinating Particle (সংযোগকারী হরফ)",
        "sample": "2:26"
    },
    "آمَنَ": {
        "translit": "āmana",
        "en": "he believed / had faith",
        "bn": "ঈমান আনল / বিশ্বাস করল",
        "pos": "verb",
        "pos_label": "Form IV Verb (ক্রিয়া)",
        "sample": "2:13"
    },
    "يَوْم": {
        "translit": "yawm",
        "en": "day / era / time",
        "bn": "দিন / দিবস / কাল",
        "pos": "noun",
        "pos_label": "Time Noun (সময়বাচক বিশেষ্য)",
        "sample": "1:4"
    },
    "عَن": {
        "translit": "‘an",
        "en": "from / about / concerning",
        "bn": "হতে / সম্পর্কে / বিষয়ে",
        "pos": "preposition",
        "pos_label": "Preposition (হরফ)",
        "sample": "2:48"
    },
    "أُولاءِ": {
        "translit": "ulā’ika",
        "en": "those / they are the ones",
        "bn": "তারাই / সেইসব লোক",
        "pos": "pronoun",
        "pos_label": "Plural Demonstrative Pronoun",
        "sample": "2:5"
    },
    "أَيّ": {
        "translit": "ayy",
        "en": "which / whatever / any",
        "bn": "কোনটি / যে কোনো",
        "pos": "noun",
        "pos_label": "Interrogative / Indefinite Noun",
        "sample": "55:13"
    },
    "عَلِمَ": {
        "translit": "‘alima",
        "en": "he knew / comprehended",
        "bn": "সে জানল / অবগত হলো",
        "pos": "verb",
        "pos_label": "Form I Verb (ক্রিয়া)",
        "sample": "2:31"
    },
    "كُلّ": {
        "translit": "kull",
        "en": "every / all / whole",
        "bn": "প্রত্যেক / সব / সমগ্র",
        "pos": "noun",
        "pos_label": "Universal Quantifier Noun",
        "sample": "2:20"
    },
    "هُمْ": {
        "translit": "hum",
        "en": "they / them (masculine)",
        "bn": "তারা / তাদের",
        "pos": "pronoun",
        "pos_label": "3rd Person Plural Pronoun",
        "sample": "2:5"
    },
    "أَرْض": {
        "translit": "arḍ",
        "en": "earth / land / world",
        "bn": "পৃথিবী / যমীন / দেশ",
        "pos": "noun",
        "pos_label": "Feminine Noun (বিশেষ্য)",
        "sample": "2:22"
    },
    "قَدْ": {
        "translit": "qad",
        "en": "already / certainly / indeed",
        "bn": "অবশ্যই / ইতিপূর্বে / নিঃসন্দেহে",
        "pos": "particle",
        "pos_label": "Expectation / Certainty Particle",
        "sample": "2:137"
    },
    "سَمَاء": {
        "translit": "samā’",
        "en": "heaven / sky / cloud",
        "bn": "আসমান / আকাশ",
        "pos": "noun",
        "pos_label": "Noun (বিশেষ্য)",
        "sample": "2:22"
    },
    "كِتاب": {
        "translit": "kitāb",
        "en": "book / scripture / record",
        "bn": "কিতাব / গ্রন্থ / বিধান",
        "pos": "noun",
        "pos_label": "Noun (বিশেষ্য)",
        "sample": "2:2"
    },
    "جَعَلَ": {
        "translit": "ja‘ala",
        "en": "he made / appointed / created",
        "bn": "সে বানাল / সৃষ্টি করল / নির্ধারণ করল",
        "pos": "verb",
        "pos_label": "Form I Verb (ক্রিয়া)",
        "sample": "2:22"
    },
    "نَفْس": {
        "translit": "nafs",
        "en": "soul / self / person",
        "bn": "আত্মা / ব্যক্তি / প্রাণ",
        "pos": "noun",
        "pos_label": "Feminine Noun (বিশেষ্য)",
        "sample": "2:48"
    },
    "أَنّ": {
        "translit": "anna",
        "en": "that / indeed that",
        "bn": "যে / নিশ্চয়ই যে",
        "pos": "particle",
        "pos_label": "Subordinating Accusative Particle",
        "sample": "2:25"
    },
    "عَمِلَ": {
        "translit": "‘amila",
        "en": "he did / acted / performed",
        "bn": "সে আমল করল / কাজ করল",
        "pos": "verb",
        "pos_label": "Form I Verb (ক্রিয়া)",
        "sample": "2:25"
    },
    "أَمْر": {
        "translit": "amr",
        "en": "command / matter / affair",
        "bn": "আদেশ / নির্দেশ / বিষয়",
        "pos": "noun",
        "pos_label": "Noun (বিশেষ্য)",
        "sample": "2:109"
    },
    "كَفَرَ": {
        "translit": "kafara",
        "en": "he disbelieved / denied",
        "bn": "সে কুফরি করল / অস্বীকার করল",
        "pos": "verb",
        "pos_label": "Form I Verb (ক্রিয়া)",
        "sample": "2:6"
    },
    "رَسُول": {
        "translit": "rasūl",
        "en": "messenger / envoy / apostle",
        "bn": "রাসূল / দূত / বার্তাবাহক",
        "pos": "noun",
        "pos_label": "Noun (বিশেষ্য)",
        "sample": "2:285"
    },
    "آيَة": {
        "translit": "āyah",
        "en": "sign / verse / miracle",
        "bn": "আয়াত / নিদর্শন / অলৌকিক প্রমাণ",
        "pos": "noun",
        "pos_label": "Noun (বিশেষ্য)",
        "sample": "2:39"
    },
    "بَعْدَ": {
        "translit": "ba‘da",
        "en": "after / afterward / later",
        "bn": "পরে / এরপর",
        "pos": "preposition",
        "pos_label": "Temporal Preposition",
        "sample": "2:27"
    },
    "بَيْنَ": {
        "translit": "bayna",
        "en": "between / amidst / among",
        "bn": "মধ্যে / মাঝে",
        "pos": "preposition",
        "pos_label": "Locative Preposition",
        "sample": "2:255"
    },
    "عَذاب": {
        "translit": "‘adhāb",
        "en": "torment / punishment / chastisement",
        "bn": "আযাব / শাস্তি / দণ্ড",
        "pos": "noun",
        "pos_label": "Noun (বিশেষ্য)",
        "sample": "2:7"
    },
    "جاءَ": {
        "translit": "jā’a",
        "en": "he came / arrived",
        "bn": "সে আসল / উপস্থিত হলো",
        "pos": "verb",
        "pos_label": "Form I Verb (ক্রিয়া)",
        "sample": "2:89"
    },
    "أَهْل": {
        "translit": "ahl",
        "en": "people / family / adherents",
        "bn": "অধিবাসী / পরিবার / অনুসারী",
        "pos": "noun",
        "pos_label": "Noun (বিশেষ্য)",
        "sample": "2:105"
    },
    "عِندَ": {
        "translit": "‘inda",
        "en": "with / near / in presence of",
        "bn": "কাছে / নিকট / সমীপে",
        "pos": "preposition",
        "pos_label": "Locative Preposition",
        "sample": "2:255"
    },
    "حَقّ": {
        "translit": "ḥaqq",
        "en": "truth / right / certainty",
        "bn": "সত্য / সঠিক / অধিকার",
        "pos": "noun",
        "pos_label": "Noun (বিশেষ্য)",
        "sample": "2:42"
    },
    "خَيْر": {
        "translit": "khayr",
        "en": "good / better / best",
        "bn": "কল্যাণ / উত্তম / মঙ্গল",
        "pos": "noun",
        "pos_label": "Superlative Noun",
        "sample": "2:103"
    },
    "رَأَى": {
        "translit": "ra’ā",
        "en": "he saw / perceived / deemed",
        "bn": "সে দেখল / উপলব্ধি করল",
        "pos": "verb",
        "pos_label": "Form I Verb (ক্রিয়া)",
        "sample": "12:4"
    },
    "نَحْنُ": {
        "translit": "naḥnu",
        "en": "we / us",
        "bn": "আমরা / আমাদেরকে",
        "pos": "pronoun",
        "pos_label": "1st Person Plural Pronoun",
        "sample": "2:14"
    },
    "قَبْل": {
        "translit": "qabl",
        "en": "before / prior to",
        "bn": "পূর্বে / আগে",
        "pos": "preposition",
        "pos_label": "Temporal Preposition",
        "sample": "2:4"
    },
    "دُون": {
        "translit": "dūn",
        "en": "besides / other than / without",
        "bn": "ব্যতীত / ছাড়া / নিম্ন",
        "pos": "preposition",
        "pos_label": "Preposition (হরফ)",
        "sample": "2:23"
    },
    "صاحِب": {
        "translit": "ṣāḥib",
        "en": "companion / fellow / dweller",
        "bn": "সঙ্গী / সাথী / অধিবাসী",
        "pos": "noun",
        "pos_label": "Noun (বিশেষ্য)",
        "sample": "2:39"
    },
    "حَتَّى": {
        "translit": "ḥattā",
        "en": "until / so that / even",
        "bn": "পর্যন্ত / যে পর্যন্ত না",
        "pos": "particle",
        "pos_label": "Preposition / Conjunction",
        "sample": "2:55"
    },
    "أَتَى": {
        "translit": "atā",
        "en": "he came / brought forth",
        "bn": "সে এল / নিয়ে এল",
        "pos": "verb",
        "pos_label": "Form I Verb (ক্রিয়া)",
        "sample": "2:106"
    },
    "قَوْم": {
        "translit": "qawm",
        "en": "people / folk / nation",
        "bn": "কওম / সম্প্রদায় / জাতি",
        "pos": "noun",
        "pos_label": "Collective Noun",
        "sample": "2:54"
    },
    "نار": {
        "translit": "nār",
        "en": "fire / hellfire",
        "bn": "আগুন / জাহান্নামের আগুন",
        "pos": "noun",
        "pos_label": "Feminine Noun",
        "sample": "2:24"
    },
    "شَيْء": {
        "translit": "shay’",
        "en": "thing / anything / matter",
        "bn": "কিছু / বস্তু / বিষয়",
        "pos": "noun",
        "pos_label": "Indefinite Noun",
        "sample": "2:20"
    },
    "ثُمَّ": {
        "translit": "thumma",
        "en": "then / furthermore",
        "bn": "অতঃপর / তারপর",
        "pos": "particle",
        "pos_label": "Sequence Conjunction Particle",
        "sample": "2:28"
    },
    "هَذا": {
        "translit": "hādhā",
        "en": "this (masculine)",
        "bn": "ইহা / এই",
        "pos": "pronoun",
        "pos_label": "Demonstrative Pronoun",
        "sample": "2:25"
    },
    "أَرَادَ": {
        "translit": "arāda",
        "en": "he intended / willed / desired",
        "bn": "সে চাইল / ইচ্ছা করল",
        "pos": "verb",
        "pos_label": "Form IV Verb (ক্রিয়া)",
        "sample": "2:26"
    },
    "رَحْمَة": {
        "translit": "raḥmah",
        "en": "mercy / grace / compassion",
        "bn": "রহমত / দয়া / অনুগ্রহ",
        "pos": "noun",
        "pos_label": "Noun (বিশেষ্য)",
        "sample": "2:105"
    },
    "عَظِيم": {
        "translit": "‘aẓīm",
        "en": "great / immense / magnificent",
        "bn": "মহা / সুমহান / বিরাট",
        "pos": "noun",
        "pos_label": "Intensive Adjective",
        "sample": "2:255"
    },
    "أَخَذَ": {
        "translit": "akhadha",
        "en": "he took / seized",
        "bn": "সে গ্রহণ করল / পাকড়াও করল",
        "pos": "verb",
        "pos_label": "Form I Verb (ক্রিয়া)",
        "sample": "2:63"
    },
    "أَنزَلَ": {
        "translit": "anzala",
        "en": "he sent down / revealed",
        "bn": "নাযিল করল / অবতীর্ণ করল",
        "pos": "verb",
        "pos_label": "Form IV Verb (ক্রিয়া)",
        "sample": "2:4"
    },
    "حَمْد": {
        "translit": "ḥamd",
        "en": "all praise and gratitude",
        "bn": "যাবতীয় প্রশংসা ও কৃতজ্ঞতা",
        "pos": "noun",
        "pos_label": "Primary Noun",
        "sample": "1:2"
    },
    "صِراط": {
        "translit": "ṣirāṭ",
        "en": "path / straight way",
        "bn": "পথ / সোজা পথ",
        "pos": "noun",
        "pos_label": "Noun",
        "sample": "1:6"
    },
    "مُسْتَقِيم": {
        "translit": "mustaqīm",
        "en": "straight / upright",
        "bn": "সরল / সঠিক",
        "pos": "noun",
        "pos_label": "Participle Adjective",
        "sample": "1:6"
    }
}

def main():
    conn = sqlite3.connect("ingest/work/quran.sqlite")
    c = conn.cursor()

    # Load corpus.json for verse texts
    with open("web/src/lib/search/corpus.json") as f:
        corpus = json.load(f)
    corpus_map = {f"{item['s']}:{item['a']}": item for item in corpus}

    total_words = c.execute("SELECT count(*) FROM word").fetchone()[0]

    # Query top 65 lemmas
    query = """
        SELECT w.lemma, w.root, w.tag, count(*) as cnt, min(w.surah), min(w.ayah)
        FROM word w
        WHERE w.lemma IS NOT NULL AND w.lemma != ''
        GROUP BY w.lemma
        ORDER BY cnt DESC
        LIMIT 65
    """
    rows = c.execute(query).fetchall()

    enriched_lemmas = []
    cumulative_count = 0

    for idx, (lem, root, tag, cnt, s_min, a_min) in enumerate(rows, 1):
        cumulative_count += cnt
        pct = round((cnt / total_words) * 100, 2)
        cum_pct = round((cumulative_count / total_words) * 100, 2)

        meta = LEMMA_METADATA.get(lem, {})
        sample_ref = meta.get("sample", f"{s_min}:{a_min}")
        sample_verse = corpus_map.get(sample_ref, {})

        enriched_lemmas.append({
            "rank": idx,
            "lemma": lem,
            "translit": meta.get("translit", lem),
            "meaning_en": meta.get("en", "Quranic vocabulary"),
            "meaning_bn": meta.get("bn", "কুরআনিক শব্দ"),
            "pos": meta.get("pos", "particle" if tag == "P" else "verb" if tag == "V" else "noun"),
            "pos_label": meta.get("pos_label", "Particle (অব্যয়)" if tag == "P" else "Verb (ক্রিয়া)" if tag == "V" else "Noun (বিশেষ্য)"),
            "root": root if root else None,
            "count": cnt,
            "percentage": pct,
            "cumulative_pct": cum_pct,
            "sample_ref": sample_ref,
            "sample_ar": sample_verse.get("ar", ""),
            "sample_en": sample_verse.get("en", ""),
            "sample_bn": sample_verse.get("bn", "")
        })

    os.makedirs("web/src/lib/search", exist_ok=True)
    out_path = "web/src/lib/search/lemmas_lab.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(enriched_lemmas, f, ensure_ascii=False, indent=2)

    print(f"Successfully generated {len(enriched_lemmas)} top lemmas at {out_path}")
    print(f"Cumulative coverage reached: {cumulative_count} / {total_words} words ({cum_pct}%)")

if __name__ == "__main__":
    main()
