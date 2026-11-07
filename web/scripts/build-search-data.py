"""Builds search corpus and knowledge data for QuranGraph client-side search engine.
Generates:
  - web/src/lib/search/corpus.json
  - web/src/lib/search/knowledge.json
"""
import json
import os
import sqlite3
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.dirname(BASE_DIR)
DB_PATH = os.path.join(PROJECT_DIR, "ingest", "work", "quran.sqlite")
KB_DIR = os.path.join(PROJECT_DIR, "ingest", "kb")
SEARCH_DIR = os.path.join(BASE_DIR, "src", "lib", "search")

sys.path.insert(0, os.path.join(PROJECT_DIR, "ingest", "core"))
from translit import transliterate

KNOWLEDGE_ENTRIES = [
    # Famous Names & Passages
    {
        "id": "passage-basmalah",
        "title_en": "Bismillahir Rahmanir Rahim (The Basmalah)",
        "title_ar": "بسم الله الرحمن الرحيم",
        "title_bn": "বিসমিল্লাহির রাহমানির রাহিম",
        "aliases": [
            "bismillah", "bismilla", "bismillahir rahmanir rahim", "bismillah ar-rahman ar-rahim",
            "bismi allah", "বিসমিল্লাহ", "বিসমিল্লাহির রাহমানির রাহিম", "بسم الله الرحمن الرحيم"
        ],
        "ayat": ["1:1"]
    },
    {
        "id": "passage-al-fatihah",
        "title_en": "Surah al-Fatihah (The Opening / Umm al-Kitab)",
        "title_ar": "الفاتحة",
        "title_bn": "সূরা আল-ফাতিহা",
        "aliases": [
            "fatiha", "fateha", "al-fatihah", "alfatihah", "surah fatiha", "surah fateha", "فاتحة", "الفاتحة",
            "ফাতিহা", "আল ফাতিহা", "উম্মুল কিতাব", "umm al-kitab", "the opening", "seven oft-repeated"
        ],
        "ayat": ["1:1", "1:2", "1:3", "1:4", "1:5", "1:6", "1:7"]
    },
    {
        "id": "passage-al-baqarah",
        "title_en": "Surah al-Baqarah (The Cow)",
        "title_ar": "البقرة",
        "title_bn": "সূরা আল-বাকারা",
        "aliases": [
            "baqarah", "baqra", "bakara", "al-baqarah", "surah baqarah", "surah baqra", "surah bakara",
            "the cow", "البقرة", "বাকারা", "আল বাকারা"
        ],
        "ayat": ["2:1", "2:255", "2:285", "2:286"]
    },
    {
        "id": "passage-yaseen",
        "title_en": "Surah Ya-Sin (Heart of the Quran)",
        "title_ar": "يس",
        "title_bn": "সূরা ইয়াসিন",
        "aliases": [
            "yasin", "yaseen", "ya-sin", "surah yasin", "surah yaseen", "يس", "ইয়াসিন", "সূরা ইয়াসিন",
            "heart of the quran"
        ],
        "ayat": ["36:1", "36:2", "36:3", "36:58", "36:82"]
    },
    {
        "id": "passage-al-mulk",
        "title_en": "Surah al-Mulk (The Sovereignty / Tabarak)",
        "title_ar": "الملك",
        "title_bn": "সূরা আল-মুলক (তাবারক)",
        "aliases": [
            "mulk", "al-mulk", "surah mulk", "tabarak", "surah tabarak", "الملك", "تبارك", "মুলক", "আল মুলক", "তাবারক"
        ],
        "ayat": ["67:1", "67:2", "67:12"]
    },
    {
        "id": "passage-al-kahf",
        "title_en": "Surah al-Kahf (The Cave)",
        "title_ar": "الكهف",
        "title_bn": "সূরা আল-কাহফ",
        "aliases": [
            "kahf", "al-kahf", "kahaf", "surah kahf", "surah kahaf", "الكهف", "কাহফ", "আল কাহফ", "the cave"
        ],
        "ayat": ["18:1", "18:10", "18:27", "18:109", "18:110"]
    },
    {
        "id": "passage-ayatul-kursi",
        "title_en": "Ayat al-Kursi (The Throne Verse)",
        "title_ar": "آية الكرسي",
        "title_bn": "আয়াতুল কুরসি",
        "aliases": [
            "ayatul kursi", "ayat al kursi", "ayatalkursi", "throne verse", "the throne verse", "kursi verse",
            "আয়াতুল কুরসি", "আয়াতুল কুরসী", "আয়াতুল কুরসি",
            "آية الكرسي", "اية الكرسي"
        ],
        "ayat": ["2:255"]
    },
    {
        "id": "passage-laylatul-qadr",
        "title_en": "Laylat al-Qadr (Night of Decree / Power)",
        "title_ar": "ليلة القدر",
        "title_bn": "লাইলাতুল কদর",
        "aliases": [
            "laylatul qadr", "laylat al qadr", "night of decree", "night of power",
            "লাইলাতুল কদর", "শবে কদর", "শবে ক্বদর",
            "ليلة القدر"
        ],
        "ayat": ["97:1", "97:3", "97:2", "97:4", "97:5", "44:3"]
    },
    {
        "id": "passage-al-kawthar",
        "title_en": "Surah al-Kawthar / River in Paradise",
        "title_ar": "الكوثر",
        "title_bn": "আল-কাওসার",
        "aliases": ["kawthar", "al-kawthar", "alkawthar", "কাওসার", "আল কাওসার", "الكوثر"],
        "ayat": ["108:1", "108:2", "108:3"]
    },
    {
        "id": "passage-iqra",
        "title_en": "Iqra / The First Revelation",
        "title_ar": "اقرأ",
        "title_bn": "ইকরা (পড়ুন)",
        "aliases": ["iqra", "iqraa", "ইকরা", "اقرأ"],
        "ayat": ["96:1", "96:2", "96:3"]
    },
    {
        "id": "translit-ikhlas",
        "title_en": "Qul Huwa Allahu Ahad",
        "title_ar": "قل هو الله أحد",
        "title_bn": "কুল হুয়াল্লাহু আহাদ",
        "aliases": [
            "qul huwa allahu ahad", "qul huwallahu ahad", "qul huwa allah ahad",
            "কুল হুয়াল্লাহু আহাদ", "কুল হু আল্লাহু আহাদ", "কুল হুয়াল্লাহু আহাদ",
            "قل هو الله احد"
        ],
        "ayat": ["112:1"]
    },
    {
        "id": "translit-fatihah-hamd",
        "title_en": "Alhamdulillah Rabbil Alamin",
        "title_ar": "الحمد لله رب العالمين",
        "title_bn": "আলহামদুলিল্লাহি রাব্বিল আলামিন",
        "aliases": [
            "alhamdulillah rabbil alamin", "alhamdu lillahi rabbil alamin",
            "আলহামদুলিল্লাহি রাব্বিল আলামিন", "আলহামদুলিল্লাহ রাব্বিল আলামিন",
            "الحمد لله رب العالمين"
        ],
        "ayat": ["1:2"]
    },
    {
        "id": "dua-rabbi-zidni-ilma",
        "title_en": "Dua: Rabbi Zidni 'Ilma",
        "title_ar": "رب زدني علما",
        "title_bn": "হে আমার প্রতিপালক! আমার জ্ঞান বৃদ্ধি করে দিন",
        "aliases": [
            "rabbi zidni ilma", "rabbi zidni ilman",
            "রব্বি যিদনি ইলমা", "হে আমার প্রতিপালক আমার জ্ঞান বৃদ্ধি করে দিন",
            "رب زدني علما"
        ],
        "ayat": ["20:114"]
    },
    {
        "id": "dua-rabbana-atina",
        "title_en": "Dua: Rabbana Atina fid-Dunya Hasanah",
        "title_ar": "ربنا آتنا في الدنيا حسنة",
        "title_bn": "হে আমাদের প্রতিপালক! আমাদের দুনিয়া ও আখিরাতে কল্যাণ দান করুন",
        "aliases": [
            "rabbana atina fid dunya hasanah", "rabbana atina fid dunya",
            "রব্বানা আতিনা ফিদ দুনিয়া", "রাব্বানা আতিনা ফিদ দুনিয়া হাসানাহ",
            "ربنا آتنا في الدنيا حسنة"
        ],
        "ayat": ["2:201"]
    },
    {
        "id": "phrase-hardship-ease",
        "title_en": "With Hardship Comes Ease",
        "title_ar": "مع العسر يسرا",
        "title_bn": "কষ্টের সাথেই স্বস্তি",
        "aliases": [
            "with hardship comes ease", "with hardship will be ease", "hardship and ease",
            "কষ্টের সাথে স্বস্তি", "কষ্টের সাথেই তো স্বস্তি আছে", "مع العسر يسرا", "ان مع العسر يسرا"
        ],
        "ayat": ["94:5", "94:6"]
    },
    # Names of Allah
    {
        "id": "noa-ar-rahman",
        "title_en": "Ar-Rahman (The Entirely Merciful)",
        "title_ar": "الرحمن",
        "title_bn": "আর-রহমান",
        "aliases": ["ar-rahman", "ar rahman", "al-rahman", "rahman", "রহমান", "আর রহমান", "الرحمن"],
        "ayat": ["55:1", "1:3", "20:5", "25:60"]
    },
    # Stories & Characters
    {
        "id": "story-yusuf",
        "title_en": "Story of Yusuf (Joseph) and his Brothers",
        "title_ar": "قصة يوسف",
        "title_bn": "ইউসুফ (আ.) ও তাঁর ভাইদের কাহিনী",
        "aliases": [
            "story of yusuf", "story of joseph", "joseph and his brothers", "yusuf and his brothers",
            "ইউসুফ নবীর কাহিনী", "ইউসুফ ও তাঁর ভাইয়েরা", "قصة يوسف"
        ],
        "ayat": ["12:4", "12:3", "12:7", "12:8", "12:1", "12:2"]
    },
    {
        "id": "story-people-of-the-cave",
        "title_en": "People of the Cave (Ashab al-Kahf)",
        "title_ar": "أصحاب الكهف",
        "title_bn": "আসহাবে কাহাফ (গুহাবাসী)",
        "aliases": [
            "people of the cave", "companions of the cave", "ashab al-kahf", "sleepers of the cave",
            "গুহাবাসী", "আসহাবে কাহাফ", "আসহাবুল কাহফ", "أصحاب الكهف"
        ],
        "ayat": ["18:9", "18:10", "18:11", "18:12", "18:13"]
    },
    {
        "id": "figure-dhul-qarnayn",
        "title_en": "Dhul-Qarnayn",
        "title_ar": "ذو القرنين",
        "title_bn": "যুল-কারনাইন",
        "aliases": ["dhul qarnayn", "dhul-qarnayn", "zulqarnain", "যুলকারনাইন", "যুল-কারনাইন", "যুল কারনাইন", "ذو القرنين"],
        "ayat": ["18:83", "18:84", "18:85", "18:86", "18:94"]
    },
    {
        "id": "figure-maryam",
        "title_en": "Maryam (Mary), Mother of Jesus",
        "title_ar": "مريم عليها السلام",
        "title_bn": "মারইয়াম (আলাইহাস সালাম)",
        "aliases": [
            "maryam", "mary", "mary mother of jesus", "maryam bint imran",
            "মারইয়াম", "মরিয়ম", "ঈসার মা মারইয়াম", "مريم"
        ],
        "ayat": ["19:16", "3:42", "3:45", "19:21", "21:91"]
    },
    {
        "id": "story-luqman",
        "title_en": "Luqman's Advice to his Son",
        "title_ar": "وصايا لقمان لابنه",
        "title_bn": "ছেলের প্রতি লুকমানের উপদেশ",
        "aliases": [
            "luqman advice to his son", "luqman advice", "luqman's advice", "advice of luqman",
            "ছেলের প্রতি লুকমানের উপদেশ", "লুকমানের উপদেশ", "وصايا لقمان"
        ],
        "ayat": ["31:13", "31:14", "31:15", "31:16", "31:17", "31:18"]
    },
    {
        "id": "story-musa-pharaoh",
        "title_en": "Musa (Moses) and Pharaoh",
        "title_ar": "موسى وفرعون",
        "title_bn": "মূসা ও ফেরাউনের ঘটনা",
        "aliases": [
            "musa and pharaoh", "moses and pharaoh", "musa confronts pharaoh",
            "মূসা ও ফেরাউন", "মুসা ও ফেরাউন", "موسى وفرعون"
        ],
        "ayat": ["20:24", "79:17", "26:10", "28:3", "7:103"]
    },
    {
        "id": "story-elephant",
        "title_en": "The Army of the Elephant (Ashab al-Fil)",
        "title_ar": "أصحاب الفيل",
        "title_bn": "হাতিওয়ালাদের ঘটনা (আসহাবুল ফীল)",
        "aliases": [
            "army of the elephant", "people of the elephant", "ashab al-fil", "year of the elephant",
            "হাতিওয়ালাদের ঘটনা", "আসহাবুল ফীল", "হাতির বাহিনী", "أصحاب الفيل"
        ],
        "ayat": ["105:1", "105:2", "105:3", "105:4", "105:5"]
    },
    {
        "id": "figure-ilyas",
        "title_en": "Prophet Ilyas (Elijah)",
        "title_ar": "إلياس عليه السلام",
        "title_bn": "ইলিয়াস (আলাইহিস সালাম)",
        "aliases": ["ilyas", "elias", "elijah", "prophet ilyas", "ইলিয়াস", "ইলিয়াস", "إلياس"],
        "ayat": ["37:123", "6:85", "37:124"]
    },
    # Semantic Questions
    {
        "id": "q-whale",
        "title_en": "Prophet Swallowed by a Whale (Yunus / Jonah)",
        "title_ar": "النبي صاحب الحوت (يونس عليه السلام)",
        "title_bn": "মাছের পেটে যাওয়া নবী (ইউনুস আ.)",
        "aliases": [
            "prophet who was swallowed by a whale", "swallowed by a whale", "swallowed by a fish",
            "prophet in the belly of the whale", "dhun-nun",
            "মাছের পেটে যাওয়া নবী", "মাছের পেটের নবী", "ইউনুস নবী তিমি মাছ"
        ],
        "ayat": ["37:142", "21:87", "68:48"]
    },
    {
        "id": "q-prophet-of-ad",
        "title_en": "Prophet of 'Ad (Hud peace be upon him)",
        "title_ar": "نبي عاد (هود عليه السلام)",
        "title_bn": "'আদ জাতির নবী (হুদ আ.)",
        "aliases": [
            "who is the prophet of ad", "prophet of ad", "prophet sent to ad", "prophet to ad",
            "আদ জাতির নবী কে", "আদ জাতির নবী", "نبي قوم عاد", "نبي عاد"
        ],
        "ayat": ["7:65", "11:50", "26:123", "46:21"]
    },
    # Key Concepts & Themes
    {
        "id": "concept-patience",
        "title_en": "Patience and Perseverance (Sabr)",
        "title_ar": "الصبر",
        "title_bn": "ধৈর্য (সবর)",
        "aliases": [
            "patience", "perseverance", "sabr", "patient",
            "ধৈর্য", "সবর", "ধৈর্যশীল",
            "الصبر", "صبر"
        ],
        "ayat": ["2:153", "2:155", "103:3", "2:45", "3:200", "39:10"]
    },
    {
        "id": "concept-fasting",
        "title_en": "Fasting in Ramadan (Sawm)",
        "title_ar": "الصيام في رمضان",
        "title_bn": "রমজানের রোজা (সিয়াম)",
        "aliases": [
            "fasting in ramadan", "fasting", "ramadan fasting", "sawm", "roza",
            "রোজা", "রমজানের রোজা", "সিয়াম", "সিয়াম",
            "الصيام", "صيام", "رمضان"
        ],
        "ayat": ["2:183", "2:185", "2:184", "2:187"]
    },
    {
        "id": "concept-riba",
        "title_en": "Prohibition of Riba (Usury / Interest)",
        "title_ar": "تحريم الربا",
        "title_bn": "সুদের নিষেধাজ্ঞা (রিবা)",
        "aliases": [
            "riba usury interest", "riba", "usury", "interest", "prohibition of interest",
            "সুদ", "সুদের নিষেধাজ্ঞা", "রিবা", "সুদখোর",
            "الربا", "ربا"
        ],
        "ayat": ["2:275", "2:278", "2:276", "3:130"]
    },
    {
        "id": "concept-parents",
        "title_en": "Being Kind and Dutiful to Parents",
        "title_ar": "بر الوالدين",
        "title_bn": "পিতা-মাতার সাথে সদ্ব্যবহার",
        "aliases": [
            "be kind to parents", "kindness to parents", "dutiful to parents", "honouring parents",
            "পিতা মাতার সাথে সদ্ব্যবহার", "পিতা-মাতার সাথে সদ্ব্যবহার", "বাবা মায়ের প্রতি দায়িত্ব",
            "পিতা মাতার প্রতি দয়া", "বাবা মার সেবা", "بر الوالدين", "الوالدين"
        ],
        "ayat": ["17:23", "31:14", "46:15", "17:24", "29:8"]
    },
    {
        "id": "concept-bees-honey",
        "title_en": "Bees and Honey as Healing",
        "title_ar": "النحل والعسل شفاء",
        "title_bn": "মৌমাছি ও মধুর মধ্যে নিরাময়",
        "aliases": [
            "bees honey healing", "honey healing", "the bees", "honey", "bees",
            "মৌমাছি ও মধু", "মধুর মধ্যে নিরাময়", "মধু শিফা", "মৌমাছি",
            "النحل", "العسل"
        ],
        "ayat": ["16:68", "16:69"]
    },
    {
        "id": "parable-spider",
        "title_en": "The Parable of the Spider's Frail House",
        "title_ar": "مثل بيت العنكبوت",
        "title_bn": "মাকড়সার ভঙ্গুর জালের দৃষ্টান্ত",
        "aliases": [
            "spider's house", "spider house", "parable of the spider", "web of the spider",
            "মাকড়সার ঘর", "মাকড়সার জাল", "মাকড়সার দৃষ্টান্ত", "بيت العنكبوت", "العنكبوت"
        ],
        "ayat": ["29:41"]
    },
    # Roots
    {
        "id": "root-r-h-m",
        "title_en": "Root R-H-M (Mercy / Compassion)",
        "title_ar": "جذر رحم",
        "title_bn": "রহম মূলশব্দ (দয়া ও অনুগ্রহ)",
        "aliases": ["رحم", "ر ح م", "root rahma", "root rahm", "rahma root"],
        "ayat": ["1:3", "55:1", "1:1", "2:163", "7:156"]
    }
]


def build():
    os.makedirs(SEARCH_DIR, exist_ok=True)

    # 1. Write knowledge.json
    knowledge_path = os.path.join(SEARCH_DIR, "knowledge.json")
    with open(knowledge_path, "w", encoding="utf-8") as f:
        json.dump(KNOWLEDGE_ENTRIES, f, ensure_ascii=False, indent=2)
    print(f"Wrote {len(KNOWLEDGE_ENTRIES)} knowledge entries to {knowledge_path}")

    # 2. Extract corpus from quran.sqlite
    db = sqlite3.connect(DB_PATH)
    c = db.cursor()

    c.execute("""
        SELECT a.surah, a.ayah, a.text_simple,
               COALESCE(te.text, ''),
               COALESCE(tb.text, ''),
               a.text_uthmani
        FROM ayah a
        LEFT JOIN text te ON te.surah = a.surah AND te.ayah = a.ayah AND te.source = 'qe-english-saheeh'
        LEFT JOIN text tb ON tb.surah = a.surah AND tb.ayah = a.ayah AND tb.source = 'qe-bengali-zakaria'
        ORDER BY a.surah, a.ayah
    """)

    corpus = []
    for s_id, a_num, ar_text, en_text, bn_text, uthmani_text in c.fetchall():
        tr_text = transliterate(uthmani_text)
        corpus.append({
            "s": s_id,
            "a": a_num,
            "ar": ar_text,
            "ar_u": uthmani_text,
            "en": en_text,
            "bn": bn_text,
            "tr": tr_text
        })

    corpus_path = os.path.join(SEARCH_DIR, "corpus.json")
    with open(corpus_path, "w", encoding="utf-8") as f:
        json.dump(corpus, f, ensure_ascii=False)
    print(f"Wrote {len(corpus)} ayat to {corpus_path} ({os.path.getsize(corpus_path) / (1024*1024):.2f} MB)")


if __name__ == "__main__":
    build()
