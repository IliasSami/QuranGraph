"""Curated Knowledge Base for QuranGraph.
Generates structured knowledge entities:
- people.json
- places.json
- nations.json
- names_of_allah.json
- unseen.json
- stories.json
- glossary.json
- learning_paths.json
"""
import json
import os

KB_DIR = os.path.dirname(os.path.abspath(__file__))

PEOPLE = [
    # 25 Prophets named in the Quran
    {"id": "adam", "name_en": "Adam (peace be upon him)", "name_ar": "آدم", "name_bn": "আদম (আলাইহিস সালাম)", "role": "prophet", "aliases": ["Adam"], "wikidata": "Q70899"},
    {"id": "idris", "name_en": "Idris (peace be upon him)", "name_ar": "إدريس", "name_bn": "ইদরীস (আলাইহিস সালাম)", "role": "prophet", "aliases": ["Idris", "Enoch"], "wikidata": "Q125556"},
    {"id": "nuh", "name_en": "Nuh (peace be upon him)", "name_ar": "نوح", "name_bn": "নূহ (আলাইহিস সালাম)", "role": "prophet", "aliases": ["Nuh", "Noah"], "wikidata": "Q81422"},
    {"id": "hud", "name_en": "Hud (peace be upon him)", "name_ar": "هود", "name_bn": "হুদ (আলাইহিস সালাম)", "role": "prophet", "aliases": ["Hud", "Heber"], "wikidata": "Q218413"},
    {"id": "salih", "name_en": "Salih (peace be upon him)", "name_ar": "صالح", "name_bn": "সালিহ (আলাইহিস সালাম)", "role": "prophet", "aliases": ["Salih", "Saleh"], "wikidata": "Q244243"},
    {"id": "ibrahim", "name_en": "Ibrahim (peace be upon him)", "name_ar": "إبراهيم", "name_bn": "ইবরাহীম (আলাইহিস সালাম)", "role": "prophet", "aliases": ["Ibrahim", "Abraham"], "wikidata": "Q9184"},
    {"id": "lut", "name_en": "Lut (peace be upon him)", "name_ar": "لوط", "name_bn": "লূত (আলাইহিস সালাম)", "role": "prophet", "aliases": ["Lut", "Lot"], "wikidata": "Q405414"},
    {"id": "ismail", "name_en": "Isma'il (peace be upon him)", "name_ar": "إسماعيل", "name_bn": "ইসমাঈল (আলাইহিস সালাম)", "role": "prophet", "aliases": ["Isma'il", "Ishmael"], "wikidata": "Q131590"},
    {"id": "ishaq", "name_en": "Ishaq (peace be upon him)", "name_ar": "إسحاق", "name_bn": "ইসহাক (আলাইহিস সালাম)", "role": "prophet", "aliases": ["Ishaq", "Isaac"], "wikidata": "Q131458"},
    {"id": "yaqub", "name_en": "Ya'qub (peace be upon him)", "name_ar": "يعقوب", "name_bn": "ইয়াকূব (আলাইহিস সালাম)", "role": "prophet", "aliases": ["Ya'qub", "Jacob", "Israel"], "wikidata": "Q131458"},
    {"id": "yusuf", "name_en": "Yusuf (peace be upon him)", "name_ar": "يوسف", "name_bn": "ইউসুফ (আলাইহিস সালাম)", "role": "prophet", "aliases": ["Yusuf", "Joseph"], "wikidata": "Q140124"},
    {"id": "ayyub", "name_en": "Ayyub (peace be upon him)", "name_ar": "أيوب", "name_bn": "আইয়ূব (আলাইহিস সালাম)", "role": "prophet", "aliases": ["Ayyub", "Job"], "wikidata": "Q180890"},
    {"id": "shuayb", "name_en": "Shu'ayb (peace be upon him)", "name_ar": "شعيب", "name_bn": "শু'আইব (আলাইহিস সালাম)", "role": "prophet", "aliases": ["Shu'ayb", "Jethro"], "wikidata": "Q244243"},
    {"id": "musa", "name_en": "Musa (peace be upon him)", "name_ar": "موسى", "name_bn": "মূসা (আলাইহিস সালাম)", "role": "prophet", "aliases": ["Musa", "Moses"], "wikidata": "Q9077"},
    {"id": "harun", "name_en": "Harun (peace be upon him)", "name_ar": "هارون", "name_bn": "হারূন (আলাইহিস সালাম)", "role": "prophet", "aliases": ["Harun", "Aaron"], "wikidata": "Q104523"},
    {"id": "dhul-kifl", "name_en": "Dhul-Kifl (peace be upon him)", "name_ar": "ذو الكفل", "name_bn": "যুল-কিফ্‌ল (আলাইহিস সালাম)", "role": "prophet", "aliases": ["Dhul-Kifl", "Ezekiel"], "wikidata": "Q193630"},
    {"id": "dawud", "name_en": "Dawud (peace be upon him)", "name_ar": "داود", "name_bn": "দাউদ (আলাইহিস সালাম)", "role": "prophet", "aliases": ["Dawud", "David"], "wikidata": "Q185527"},
    {"id": "sulayman", "name_en": "Sulayman (peace be upon him)", "name_ar": "سليمان", "name_bn": "সুলাইমান (আলাইহিস সালাম)", "role": "prophet", "aliases": ["Sulayman", "Solomon"], "wikidata": "Q218413"},
    {"id": "ilyas", "name_en": "Ilyas (peace be upon him)", "name_ar": "إلياس", "name_bn": "ইলিয়াস (আলাইহিস সালাম)", "role": "prophet", "aliases": ["Ilyas", "Elijah"], "wikidata": "Q218413"},
    {"id": "al-yasa", "name_en": "Al-Yasa' (peace be upon him)", "name_ar": "اليسع", "name_bn": "আল-ইয়াসা' (আলাইহিস সালাম)", "role": "prophet", "aliases": ["Al-Yasa", "Elisha"], "wikidata": "Q218413"},
    {"id": "yunus", "name_en": "Yunus (peace be upon him)", "name_ar": "يونس", "name_bn": "ইউনুস (আলাইহিস সালাম)", "role": "prophet", "aliases": ["Yunus", "Jonah", "Dhul-Nun"], "wikidata": "Q218413"},
    {"id": "zakariyya", "name_en": "Zakariyya (peace be upon him)", "name_ar": "زكريا", "name_bn": "যাকারিয়্যা (আলাইহিস সালাম)", "role": "prophet", "aliases": ["Zakariyya", "Zechariah"], "wikidata": "Q218413"},
    {"id": "yahya", "name_en": "Yahya (peace be upon him)", "name_ar": "يحيى", "name_bn": "ইয়াহইয়া (আলাইহিস সালাম)", "role": "prophet", "aliases": ["Yahya", "John the Baptist"], "wikidata": "Q218413"},
    {"id": "isa", "name_en": "Isa (peace be upon him)", "name_ar": "عيسى", "name_bn": "ঈসা (আলাইহিস সালাম)", "role": "prophet", "aliases": ["Isa", "Jesus", "Al-Masih"], "wikidata": "Q302"},
    {"id": "prophet-muhammad", "name_en": "Prophet Muhammad ﷺ", "name_ar": "محمد", "name_bn": "রাসূলুল্লাহ ﷺ", "role": "prophet", "aliases": ["Muhammad", "the Prophet ﷺ", "Ahmad", "Messenger of Allah"], "wikidata": "Q9458"},
    # Other figures mentioned in Quran and classic tafsir
    {"id": "maryam", "name_en": "Maryam (peace be upon her)", "name_ar": "مريم", "name_bn": "মারইয়াম (আলাইহাস সালাম)", "role": "righteous_woman", "aliases": ["Mary", "Maryam bint Imran"], "wikidata": "Q345"},
    {"id": "luqman", "name_en": "Luqman the Wise", "name_ar": "لقمان", "name_bn": "লুকমান হাকিম", "role": "wise_man", "aliases": ["Luqman"], "wikidata": "Q138382"},
    {"id": "pharaoh", "name_en": "Pharaoh (Fir'awn)", "name_ar": "فرعون", "name_bn": "ফেরাউন", "role": "tyrant", "aliases": ["Pharaoh", "Fir'awn"], "wikidata": "Q37110"},
    {"id": "haman", "name_en": "Haman", "name_ar": "هامان", "name_bn": "হামান", "role": "minister", "aliases": ["Haman"], "wikidata": "Q125556"},
    {"id": "qarun", "name_en": "Qarun (Korah)", "name_ar": "قارون", "name_bn": "কারূন", "role": "wealthy_rebel", "aliases": ["Qarun", "Korah"], "wikidata": "Q125556"},
    {"id": "abu-lahab", "name_en": "Abu Lahab", "name_ar": "أبو لهب", "name_bn": "আবু লাহাব", "role": "opponent", "aliases": ["Abu Lahab", "Abd al-Uzza"], "wikidata": "Q335345"},
    {"id": "abu-jahl", "name_en": "Abu Jahl", "name_ar": "أبو جهل", "name_bn": "আবু জাহল", "role": "opponent", "aliases": ["Abu Jahl", "Amr ibn Hisham"], "wikidata": "Q335345"},
    {"id": "abu-bakr", "name_en": "Abu Bakr as-Siddiq (may Allah be pleased with him)", "name_ar": "أبو بكر الصديق", "name_bn": "আবু বকর আস-সিদ্দীক (রাযিয়াল্লাহু আনহু)", "role": "companion", "aliases": ["Abu Bakr as-Siddiq", "Abu Bakr"], "wikidata": "Q39619"},
    {"id": "umar-ibn-al-khattab", "name_en": "'Umar ibn al-Khattab (may Allah be pleased with him)", "name_ar": "عمر بن الخطاب", "name_bn": "উমর ইবনুল খাত্তাব (রাযিয়াল্লাহু আনহু)", "role": "companion", "aliases": ["'Umar ibn al-Khattab", "Umar ibn al-Khattab", "Umar"], "wikidata": "Q8467"},
    {"id": "ali-ibn-abi-talib", "name_en": "'Ali ibn Abi Talib (may Allah be pleased with him)", "name_ar": "علي بن أبي طالب", "name_bn": "আলী ইবনে আবী তালিব (রাযিয়াল্লাহু আনহু)", "role": "companion", "aliases": ["'Ali ibn Abi Talib", "Ali ibn Abi Talib", "Ali"], "wikidata": "Q39619"},
    {"id": "aishah", "name_en": "'A'ishah (may Allah be pleased with her)", "name_ar": "عائشة بنت أبي بكر", "name_bn": "আয়িশা (রাযিয়াল্লাহু আনহা)", "role": "companion", "aliases": ["'A'ishah", "A'ishah", "Aisha"], "wikidata": "Q165714"},
    {"id": "khadijah", "name_en": "Khadijah bint Khuwaylid (may Allah be pleased with her)", "name_ar": "خديجة بنت خويلد", "name_bn": "খাদীজাহ (রাযিয়াল্লাহু আনহা)", "role": "companion", "aliases": ["Khadijah", "Khadija"], "wikidata": "Q42034"},
    {"id": "abdullah-ibn-umm-maktum", "name_en": "Abdullah ibn Umm Maktum (may Allah be pleased with him)", "name_ar": "عبد الله بن أم مكتوم", "name_bn": "আব্দুল্লাহ ইবনে উম্মে মাকতুম (রাযিয়াল্লাহু আনহু)", "role": "companion", "aliases": ["Abdullah ibn Umm Maktum", "Ibn Umm Maktum"], "wikidata": "Q125556"},
    {"id": "ibn-abbas", "name_en": "'Abdullah ibn 'Abbas (may Allah be pleased with him)", "name_ar": "عبد الله بن عباس", "name_bn": "আব্দুল্লাহ ইবনে আব্বাস (রাযিয়াল্লাহু আনহু)", "role": "companion", "aliases": ["Ibn 'Abbas", "Ibn Abbas"], "wikidata": "Q312484"},
    {"id": "ibn-masud", "name_en": "'Abdullah ibn Mas'ud (may Allah be pleased with him)", "name_ar": "عبد الله بن مسعود", "name_bn": "আব্দুল্লাহ ইবনে মাসউদ (রাযিয়াল্লাহু আনহু)", "role": "companion", "aliases": ["Ibn Mas'ud", "Ibn Masud"], "wikidata": "Q312484"},
    {"id": "bilal", "name_en": "Bilal ibn Rabah (may Allah be pleased with him)", "name_ar": "بلال بن رباح", "name_bn": "বিলাল ইবনে রাবাহ (রাযিয়াল্লাহু আনহু)", "role": "companion", "aliases": ["Bilal", "Bilal ibn Rabah"], "wikidata": "Q192994"},
    {"id": "abrahah", "name_en": "Abrahah al-Ashram", "name_ar": "أبرهة الأشرم", "name_bn": "আবরাহা আল-আশরাম", "role": "tyrant", "aliases": ["Abrahah"], "wikidata": "Q330691"},
    {"id": "abu-talib", "name_en": "Abu Talib", "name_ar": "أبو طالب", "name_bn": "আবু তালিব", "role": "figure", "aliases": ["Abu Talib"], "wikidata": "Q335345"},
    {"id": "dhul-qarnayn", "name_en": "Dhul-Qarnayn", "name_ar": "ذو القرنين", "name_bn": "যুল-কারনাইন", "role": "righteous_king", "aliases": ["Dhul-Qarnayn"], "wikidata": "Q125556"},
    {"id": "khidr", "name_en": "Al-Khidr", "name_ar": "الخضر", "name_bn": "আল-খিদর", "role": "righteous_servant", "aliases": ["Al-Khidr", "Khidr"], "wikidata": "Q125556"},
]

PLACES = [
    {"id": "makkah", "name_en": "Makkah", "name_ar": "مكة", "name_bn": "মক্কা", "aliases": ["Mecca", "Bakkah", "Umm al-Qura"], "wikidata": "Q5806", "lat": 21.4225, "lon": 39.8262},
    {"id": "madinah", "name_en": "Madinah", "name_ar": "المدينة المنورة", "name_bn": "মদিনা", "aliases": ["Medina", "Yathrib"], "wikidata": "Q35484", "lat": 24.4672, "lon": 39.6111},
    {"id": "al-quds", "name_en": "Jerusalem (Al-Quds / Al-Masjid al-Aqsa)", "name_ar": "القدس / المسجد الأقصى", "name_bn": "বায়তুল মুকাদ্দাস / আল-আকসা", "aliases": ["Jerusalem", "Al-Aqsa"], "wikidata": "Q1218", "lat": 31.7761, "lon": 35.2358},
    {"id": "tur-sina", "name_en": "Mount Sinai (Tur Sina)", "name_ar": "طور سيناء", "name_bn": "তূর পাহাড়", "aliases": ["Mount Sinai", "Mount At-Tur"], "wikidata": "Q377485", "lat": 28.5397, "lon": 33.9753},
    {"id": "jabal-judi", "name_en": "Mount Judi", "name_ar": "الجودي", "name_bn": "জুদি পর্বত", "aliases": ["Mount Judi"], "wikidata": "Q1143899", "lat": 37.3833, "lon": 42.4833},
    {"id": "badr", "name_en": "Badr", "name_ar": "بدر", "name_bn": "বদর", "aliases": ["Badr"], "wikidata": "Q816822", "lat": 23.7833, "lon": 38.7833},
    {"id": "kaabah", "name_en": "The Ka'bah", "name_ar": "الكعبة", "name_bn": "কা'বা শরীফ", "aliases": ["the Ka'bah", "al-Bayt al-Haram"], "wikidata": "Q42488", "lat": 21.4225, "lon": 39.8262},
    {"id": "sijjin", "name_en": "Sijjin", "name_ar": "سجين", "name_bn": "সিজ্জীন", "aliases": ["Sijjin"], "wikidata": "Q125556"},
    {"id": "illiyyun", "name_en": "'Illiyyun", "name_ar": "عليون", "name_bn": "ইল্লিয়্যূন", "aliases": ["'Illiyyun", "Illiyin"], "wikidata": "Q125556"},
]

NATIONS = [
    {"id": "quraysh", "name_en": "Quraysh", "name_ar": "قريش", "name_bn": "কুরাইশ", "aliases": ["Quraysh"], "wikidata": "Q234553"},
    {"id": "bani-israil", "name_en": "Children of Israel (Bani Isra'il)", "name_ar": "بنو إسرائيل", "name_bn": "বনী ইসরাঈল", "aliases": ["Bani Isra'il", "Children of Israel", "Jews"], "wikidata": "Q131458"},
    {"id": "ad", "name_en": "People of 'Ad", "name_ar": "عاد", "name_bn": "'আদ জাতি", "aliases": ["'Ad", "Ad"], "wikidata": "Q218413"},
    {"id": "thamud", "name_en": "People of Thamud", "name_ar": "ثمود", "name_bn": "সামূদ জাতি", "aliases": ["Thamud"], "wikidata": "Q244243"},
    {"id": "madyan", "name_en": "People of Madyan (Midian)", "name_ar": "مدين", "name_bn": "মাদইয়ানবাসী", "aliases": ["Madyan", "Midian"], "wikidata": "Q218413"},
    {"id": "ashab-al-ukhdud", "name_en": "People of the Ditch (Ashab al-Ukhdud)", "name_ar": "أصحاب الأخدود", "name_bn": "আসহাবুল উখদূদ (গর্তওয়ালা)", "aliases": ["People of the Ditch", "Ashab al-Ukhdud"], "wikidata": "Q125556"},
    {"id": "ashab-al-fil", "name_en": "People of the Elephant (Ashab al-Fil)", "name_ar": "أصحاب الفيل", "name_bn": "আসহাবুল ফীল (হাতিওয়ালা)", "aliases": ["People of the Elephant", "Ashab al-Fil"], "wikidata": "Q125556"},
    {"id": "rum", "name_en": "The Romans (Byzantines)", "name_ar": "الروم", "name_bn": "রোমবাসী", "aliases": ["Ar-Rum", "the Romans"], "wikidata": "Q125556"},
    {"id": "christians", "name_en": "Christians (An-Nasara)", "name_ar": "النصارى", "name_bn": "নাসারা (খ্রিস্টান)", "aliases": ["Christians", "Nasara"], "wikidata": "Q5043"},
    {"id": "people-of-the-book", "name_en": "People of the Book (Ahl al-Kitab)", "name_ar": "أهل الكتاب", "name_bn": "আহলে কিতাব", "aliases": ["People of the Book", "Ahl al-Kitab"], "wikidata": "Q125556"},
    {"id": "iram", "name_en": "Iram of the Pillars", "name_ar": "إرم ذات العماد", "name_bn": "ইরাম নগরী", "aliases": ["Iram"], "wikidata": "Q125556"},
    {"id": "abyssinians", "name_en": "Abyssinians", "name_ar": "الحبشة", "name_bn": "হাবশী জাতি", "aliases": ["Abyssinians", "Habasha"], "wikidata": "Q125556"},
]

UNSEEN = [
    {"id": "paradise", "name_en": "Paradise (Jannah)", "name_ar": "الجنة", "name_bn": "জান্নাত", "type": "realm", "aliases": ["Paradise", "Jannah", "Gardens of Eden"], "wikidata": "Q218413"},
    {"id": "hell", "name_en": "Hell (Jahannam)", "name_ar": "جهنم", "name_bn": "জাহান্নাম", "type": "realm", "aliases": ["Hell", "Jahannam", "the Fire"], "wikidata": "Q218413"},
    {"id": "angels", "name_en": "The Angels (Mala'ikah)", "name_ar": "الملائكة", "name_bn": "ফেরেশতাগণ", "type": "beings", "aliases": ["angels", "Mala'ikah"], "wikidata": "Q218413"},
    {"id": "jibril", "name_en": "Angel Jibril (peace be upon him)", "name_ar": "جبريل", "name_bn": "জিবরীল (আলাইহিস সালাম)", "type": "angel", "aliases": ["Jibril", "Gabriel", "the Holy Spirit", "Ruh al-Qudus"], "wikidata": "Q43668"},
    {"id": "mikail", "name_en": "Angel Mika'il (peace be upon him)", "name_ar": "ميكائيل", "name_bn": "মীকাঈল (আলাইহিস সালাম)", "type": "angel", "aliases": ["Mika'il", "Michael"], "wikidata": "Q218413"},
    {"id": "israfil", "name_en": "Angel Israfil (peace be upon him)", "name_ar": "إسرافيل", "name_bn": "ইসরাফীল (আলাইহিস সালাম)", "type": "angel", "aliases": ["Israfil", "the Angel of the Trumpet"], "wikidata": "Q218413"},
    {"id": "malik", "name_en": "Angel Malik (Keeper of Hell)", "name_ar": "مالك", "name_bn": "মালিক (জাহান্নামের দারোয়ান)", "type": "angel", "aliases": ["Malik"], "wikidata": "Q218413"},
    {"id": "satan", "name_en": "Satan (Shaytan / Iblis)", "name_ar": "الشيطان / إبليس", "name_bn": "শয়তান / ইবলিস", "type": "jinn", "aliases": ["Satan", "Shaytan", "Iblis"], "wikidata": "Q35442"},
    {"id": "jinn", "name_en": "The Jinn", "name_ar": "الجن", "name_bn": "জ্বিন জাতি", "type": "beings", "aliases": ["jinn", "Al-Jinn"], "wikidata": "Q218413"},
    {"id": "throne", "name_en": "The Throne of Allah (Al-'Arsh)", "name_ar": "العرش", "name_bn": "আল্লাহর আরশ", "type": "unseen_creation", "aliases": ["the Throne", "Al-'Arsh"], "wikidata": "Q218413"},
    {"id": "kursi", "name_en": "The Footstool (Al-Kursi)", "name_ar": "الكرسي", "name_bn": "কুরসী", "type": "unseen_creation", "aliases": ["the Kursi", "Al-Kursi"], "wikidata": "Q218413"},
    {"id": "preserved-tablet", "name_en": "The Preserved Tablet (Al-Lawh al-Mahfuz)", "name_ar": "اللوح المحفوظ", "name_bn": "লওহে মাহফুজ", "type": "unseen_creation", "aliases": ["the Preserved Tablet", "Al-Lawh al-Mahfuz"], "wikidata": "Q125556"},
    {"id": "recording-angels", "name_en": "The Noble Recording Angels (Al-Kiram al-Katibin)", "name_ar": "الكرام الكاتبين", "name_bn": "সম্মানিত লেখক ফেরেশতাগণ", "type": "angel", "aliases": ["recording angels", "Kiram Katibin"], "wikidata": "Q125556"},
    {"id": "zabaniyah", "name_en": "Az-Zabaniyah (Angels of Hellfire)", "name_ar": "الزبانية", "name_bn": "জাহান্নামের কঠোর প্রহরী ফেরেশতা", "type": "angel", "aliases": ["Zabaniyah"], "wikidata": "Q125556"},
    {"id": "al-kawthar", "name_en": "Al-Kawthar (River of Abundance in Paradise)", "name_ar": "الكوثر", "name_bn": "আল-কাওসার", "type": "realm_feature", "aliases": ["al-Kawthar", "river in Paradise"], "wikidata": "Q125556"},
    {"id": "tasnim", "name_en": "Tasnim (Spring in Paradise)", "name_ar": "تسنيم", "name_bn": "তাসনীম", "type": "realm_feature", "aliases": ["Tasnim"], "wikidata": "Q125556"},
    {"id": "the-scale", "name_en": "The Scale of Deeds (Al-Mizan)", "name_ar": "الميزان", "name_bn": "মিযান (আমলের পাল্লা)", "type": "unseen_creation", "aliases": ["the Scale", "Al-Mizan"], "wikidata": "Q125556"},
    {"id": "record-of-deeds", "name_en": "The Record of Deeds (Kitab al-A'mal)", "name_ar": "صحائف الأعمال", "name_bn": "আমলনামা", "type": "unseen_creation", "aliases": ["record of deeds", "books of deeds"], "wikidata": "Q125556"},
]

NAMES_OF_ALLAH = [
    {"id": "allah", "name_en": "Allah", "name_ar": "الله", "name_bn": "আল্লাহ", "meaning_en": "The One and Only God", "meaning_bn": "একমাত্র সত্য উপাস্য"},
    {"id": "ar-rabb", "name_en": "Ar-Rabb", "name_ar": "الرب", "name_bn": "রব্ব", "meaning_en": "The Lord, Creator, Sustainer and Master", "meaning_bn": "পালনকর্তা ও প্রভু"},
    {"id": "ar-rahman", "name_en": "Ar-Rahman", "name_ar": "الرحمن", "name_bn": "আর-রহমান", "meaning_en": "The Entirely Merciful", "meaning_bn": "অনন্ত করুণাময়"},
    {"id": "ar-rahim", "name_en": "Ar-Rahim", "name_ar": "الرحيم", "name_bn": "আর-রহীম", "meaning_en": "The Especially Merciful", "meaning_bn": "পরম দয়ালু"},
    {"id": "al-malik", "name_en": "Al-Malik", "name_ar": "الملك", "name_bn": "আল-মালিক", "meaning_en": "The Sovereign, The True King", "meaning_bn": "সার্বভৌম অধিপতি"},
    {"id": "al-quddus", "name_en": "Al-Quddus", "name_ar": "القدوس", "name_bn": "আল-কুদ্দূস", "meaning_en": "The Most Sacred, Free from all imperfections", "meaning_bn": "মহা পবিত্র"},
    {"id": "as-salam", "name_en": "As-Salam", "name_ar": "السلام", "name_bn": "আস-সালাম", "meaning_en": "The Source of Peace and Safety", "meaning_bn": "শান্তিদাতা"},
    {"id": "al-mumin", "name_en": "Al-Mu'min", "name_ar": "المؤمن", "name_bn": "আল-মু'মিন", "meaning_en": "The Granter of Security and Faith", "meaning_bn": "নিরাপত্তাদাতা ও ঈমানদানকারী"},
    {"id": "al-muhaymin", "name_en": "Al-Muhaymin", "name_ar": "المهيمن", "name_bn": "আল-মুহাইমিন", "meaning_en": "The Guardian, The Overseer", "meaning_bn": "মহা অভিভাবক ও পর্যবেক্ষণকারী"},
    {"id": "al-aziz", "name_en": "Al-'Aziz", "name_ar": "العزيز", "name_bn": "আল-'আযীয", "meaning_en": "The All-Mighty, The Invincible", "meaning_bn": "মহা পরাক্রমশালী"},
    {"id": "al-jabbar", "name_en": "Al-Jabbar", "name_ar": "الجبار", "name_bn": "আল-জাব্বার", "meaning_en": "The Compeller, The Restorer", "meaning_bn": "প্রবল প্রতাপশালী"},
    {"id": "al-mutakabbir", "name_en": "Al-Mutakabbir", "name_ar": "المتكبر", "name_bn": "আল-মুতাকাব্বির", "meaning_en": "The Supremely Great", "meaning_bn": "অসীম শ্রেষ্ঠত্বের অধিকারী"},
    {"id": "al-khaliq", "name_en": "Al-Khaliq", "name_ar": "الخالق", "name_bn": "আল-খালিক", "meaning_en": "The Creator", "meaning_bn": "সৃষ্টিকর্তা"},
    {"id": "al-bari", "name_en": "Al-Bari'", "name_ar": "البارئ", "name_bn": "আল-বারী", "meaning_en": "The Originator, The Evolver", "meaning_bn": "উদ্ভাবনকারী"},
    {"id": "al-musawwir", "name_en": "Al-Musawwir", "name_ar": "المصور", "name_bn": "আল-মুসাওয়ির", "meaning_en": "The Fashioner of Forms", "meaning_bn": "রূপদানকারী"},
    {"id": "al-ghaffar", "name_en": "Al-Ghaffar", "name_ar": "الغفار", "name_bn": "আল-গাফফার", "meaning_en": "The Constant Forgiver", "meaning_bn": "মহা ক্ষমাশীল"},
    {"id": "al-qahhar", "name_en": "Al-Qahhar", "name_ar": "القهار", "name_bn": "আল-কাহহার", "meaning_en": "The Subduer, The All-Dominant", "meaning_bn": "মহাপরাক্রমশালী দমনকারী"},
    {"id": "al-wahhab", "name_en": "Al-Wahhab", "name_ar": "الوهاب", "name_bn": "আল-ওয়াহহাব", "meaning_en": "The Giver of All, The Bestower", "meaning_bn": "মহা দানশীল"},
    {"id": "ar-razzaq", "name_en": "Ar-Razzaq", "name_ar": "الرزاق", "name_bn": "আর-রাজ্জাক", "meaning_en": "The Sustainer, The Provider", "meaning_bn": "রিযিকদাতা"},
    {"id": "al-fattah", "name_en": "Al-Fattah", "name_ar": "الفتاح", "name_bn": "আল-ফাত্তাহ", "meaning_en": "The Opener, The Supreme Judge", "meaning_bn": "বিজয় ও উন্মুক্তকারী"},
    {"id": "al-alim", "name_en": "Al-'Alim", "name_ar": "العليم", "name_bn": "আল-'আলীম", "meaning_en": "The All-Knowing", "meaning_bn": "সর্বজ্ঞাত"},
    {"id": "as-sami", "name_en": "As-Sami'", "name_ar": "السميع", "name_bn": "আস-সামী'", "meaning_en": "The All-Hearing", "meaning_bn": "সর্বশ্রোতা"},
    {"id": "al-basir", "name_en": "Al-Basir", "name_ar": "البصير", "name_bn": "আল-বাসীর", "meaning_en": "The All-Seeing", "meaning_bn": "সর্বদ্রষ্টা"},
    {"id": "al-hakim", "name_en": "Al-Hakim", "name_ar": "الحكيم", "name_bn": "আল-হাকীম", "meaning_en": "The All-Wise", "meaning_bn": "মহাপ্রজ্ঞাময়"},
    {"id": "al-wadud", "name_en": "Al-Wadud", "name_ar": "الودود", "name_bn": "আল-ওয়াদূদ", "meaning_en": "The Most Loving", "meaning_bn": "পরম স্নেহশীল"},
    {"id": "al-ghafur", "name_en": "Al-Ghafur", "name_ar": "الغفور", "name_bn": "আল-গাফূর", "meaning_en": "The Forgiving", "meaning_bn": "পরম ক্ষমাশীল"},
    {"id": "ash-shakur", "name_en": "Ash-Shakur", "name_ar": "الشكور", "name_bn": "আশ-শাকূর", "meaning_en": "The Most Appreciative", "meaning_bn": "গুণগ্রাহী"},
    {"id": "al-aliyy", "name_en": "Al-'Aliyy", "name_ar": "العلي", "name_bn": "আল-'আলী", "meaning_en": "The Most High", "meaning_bn": "সর্বোচ্চ মর্যাদাপূর্ণ"},
    {"id": "al-ala", "name_en": "Al-A'la", "name_ar": "الأعلى", "name_bn": "আল-আ'লা", "meaning_en": "The Most High, Above All", "meaning_bn": "সর্বোচ্চ ও সর্বশ্রেষ্ঠ"},
    {"id": "al-kabir", "name_en": "Al-Kabir", "name_ar": "الكبير", "name_bn": "আল-কাবীর", "meaning_en": "The Most Great", "meaning_bn": "সবচেয়ে বড় ও মহান"},
    {"id": "al-hafiz", "name_en": "Al-Hafiz", "name_ar": "الحفيظ", "name_bn": "আল-হাফীয", "meaning_en": "The Preserver, The Protector", "meaning_bn": "মহা সংরক্ষক"},
    {"id": "al-karim", "name_en": "Al-Karim", "name_ar": "الكريم", "name_bn": "আল-কারীম", "meaning_en": "The Most Generous", "meaning_bn": "মহা দয়ালু ও সম্মানিত"},
    {"id": "al-akram", "name_en": "Al-Akram", "name_ar": "الأكرم", "name_bn": "আল-আকরাম", "meaning_en": "The Most Bounteous and Generous", "meaning_bn": "মহা মহিমান্বিত ও পরম অনুগ্রহশীল"},
    {"id": "al-haqq", "name_en": "Al-Haqq", "name_ar": "الحق", "name_bn": "আল-হাক্ক", "meaning_en": "The Absolute Truth", "meaning_bn": "চিরন্তন সত্য"},
    {"id": "al-wakil", "name_en": "Al-Wakil", "name_ar": "الوكيل", "name_bn": "আল-ওয়াকীল", "meaning_en": "The Trustee, The Dependable", "meaning_bn": "উত্তম কর্মবিধায়ক"},
    {"id": "al-qawiyy", "name_en": "Al-Qawiyy", "name_ar": "القوي", "name_bn": "আল-কাউয়্যি", "meaning_en": "The All-Strong", "meaning_bn": "মহা শক্তিধর"},
    {"id": "al-matin", "name_en": "Al-Matin", "name_ar": "المتين", "name_bn": "আল-মাতীন", "meaning_en": "The Firm, The Steadfast", "meaning_bn": "সুদৃঢ় ও অটল"},
    {"id": "al-waliyy", "name_en": "Al-Waliyy", "name_ar": "الولي", "name_bn": "আল-ওয়ালীয়্য", "meaning_en": "The Protecting Friend, The Ally", "meaning_bn": "অভিভাবক ও সাহায্যকারী"},
    {"id": "al-hamid", "name_en": "Al-Hamid", "name_ar": "الحميد", "name_bn": "আল-হামীদ", "meaning_en": "The All-Praiseworthy", "meaning_bn": "সকল প্রশংসার একমাত্র যোগ্য"},
    {"id": "al-hayy", "name_en": "Al-Hayy", "name_ar": "الحي", "name_bn": "আল-হাই", "meaning_en": "The Ever-Living", "meaning_bn": "চিরঞ্জীব"},
    {"id": "al-qayyum", "name_en": "Al-Qayyum", "name_ar": "القيوم", "name_bn": "আল-কাইয়ূম", "meaning_en": "The Sustainer of All Existence", "meaning_bn": "সকল সৃষ্টির ধারক ও চিরস্থায়ী"},
    {"id": "al-ahad", "name_en": "Al-Ahad", "name_ar": "الأحد", "name_bn": "আল-আহাদ", "meaning_en": "The Unique One", "meaning_bn": "অদ্বিতীয় ও একক"},
    {"id": "as-samad", "name_en": "As-Samad", "name_ar": "الصمد", "name_bn": "আস-সামাদ", "meaning_en": "The Eternal Refuge, Self-Sufficient upon whom all depend", "meaning_bn": "অমুখাপেক্ষী, যার উপর সবাই নির্ভরশীল"},
    {"id": "al-qadir", "name_en": "Al-Qadir", "name_ar": "القادر", "name_bn": "আল-কাদির", "meaning_en": "The All-Capable", "meaning_bn": "সর্বশক্তিমান"},
    {"id": "at-tawwab", "name_en": "At-Tawwab", "name_ar": "التواب", "name_bn": "আত-তাওয়াব", "meaning_en": "The Accepter of Repentance", "meaning_bn": "তওবা কবুলকারী"},
    {"id": "ar-rauf", "name_en": "Ar-Ra'uf", "name_ar": "الرؤوف", "name_bn": "আর-রাউফ", "meaning_en": "The Most Kind, The Compassionate", "meaning_bn": "মমতাময় ও কোমল হৃদয়ের দাতা"},
    {"id": "al-ghaniyy", "name_en": "Al-Ghaniyy", "name_ar": "الغني", "name_bn": "আল-গানীয়্য", "meaning_en": "The Self-Sufficient, Free of All Need", "meaning_bn": "সম্পদশালী ও অভাবমুক্ত"},
    {"id": "an-nur", "name_en": "An-Nur", "name_ar": "النور", "name_bn": "আন-নূর", "meaning_en": "The Light", "meaning_bn": "জ্যোতিময় প্রকাশকারী"},
    {"id": "al-hadi", "name_en": "Al-Hadi", "name_ar": "الهادي", "name_bn": "আল-হাদী", "meaning_en": "The Guide", "meaning_bn": "পথপ্রদর্শক"},
    {"id": "al-khabir", "name_en": "Al-Khabir", "name_ar": "الخبير", "name_bn": "আল-খাবীর", "meaning_en": "The All-Aware", "meaning_bn": "সর্বজ্ঞাত ও সম্যক অবহিত"},
    {"id": "al-majid", "name_en": "Al-Majid", "name_ar": "المجيد", "name_bn": "আল-মাজীদ", "meaning_en": "The All-Glorious, The Majestic", "meaning_bn": "মহিমান্বিত ও মর্যাদাবান"},
    {"id": "ash-shahid", "name_en": "Ash-Shahid", "name_ar": "الشهيد", "name_bn": "আশ-শাহীদ", "meaning_en": "The All-Witnessing", "meaning_bn": "সর্বপ্রত্যক্ষকারী"},
    {"id": "al-afuw", "name_en": "Al-'Afuw", "name_ar": "العفو", "name_bn": "আল-'আফূও", "meaning_en": "The Ever-Pardoning, The Effacer of Sins", "meaning_bn": "পরম ক্ষমাশীল ও পাপ মোচনকারী"},
    {"id": "al-ilah", "name_en": "Al-Ilah", "name_ar": "الإله", "name_bn": "আল-ইলাহ", "meaning_en": "The One Truly Worthy of Worship", "meaning_bn": "একমাত্র সত্য উপাস্য"},
    {"id": "ahkam-al-hakimin", "name_en": "Ahkam al-Hakimin", "name_ar": "أحكم الحاكمين", "name_bn": "আহকামুল হাকিমীন", "meaning_en": "The Most Just of All Judges", "meaning_bn": "সর্বশ্রেষ্ঠ সুবিচারক"},
    {"id": "rabb-al-alamin", "name_en": "Rabb al-'Alamin", "name_ar": "رب العالمين", "name_bn": "রব্বুল আলামীন", "meaning_en": "Lord of all the Worlds and Creations", "meaning_bn": "সকল সৃষ্টির প্রতিপালক ও প্রভু"},
]

GLOSSARY = [
    {"id": "tawhid", "term_en": "Tawhid", "term_ar": "التوحيد", "term_bn": "তাওহীদ", "def_en": "The core Islamic belief in the absolute oneness of Allah in His Lordship, worship, and perfect names and attributes.", "def_bn": "আল্লাহর রুবূবিয়্যাত, উলূহিয়্যাত এবং নাম ও গুণাবলীতে তাঁর নিরঙ্কুশ একত্ববাদের বিশ্বাস।"},
    {"id": "shirk", "term_en": "Shirk", "term_ar": "الشرك", "term_bn": "শিরক", "def_en": "Associating partners with Allah in worship, Lordship, or divine attributes; the unforgivable sin if one dies without repentance.", "def_bn": "আল্লাহর সাথে ইবাদতে, প্রভুত্বে বা গুণে কাউকে অংশীদার স্থির করা; সবচেয়ে বড় অবিচার ও গুনাহ।"},
    {"id": "iman", "term_en": "Iman", "term_ar": "الإيمان", "term_bn": "ঈমান", "def_en": "True faith: belief in the heart, declaration with the tongue, and action with the limbs.", "def_bn": "অন্তর দিয়ে বিশ্বাস, মুখে স্বীকার এবং অঙ্গ-প্রত্যঙ্গ দিয়ে আমল করার সমষ্টি।"},
    {"id": "taqwa", "term_en": "Taqwa", "term_ar": "التقوى", "term_bn": "তাকওয়া", "def_en": "God-consciousness: protecting oneself from Allah's punishment by obeying His commands and avoiding His prohibitions.", "def_bn": "আল্লাহভীতি ও সচেতনতা: আল্লাহর আদেশ পালন ও নিষেধ বর্জনের মাধ্যমে তাঁর অসন্তুষ্টি থেকে আত্মরক্ষা।"},
    {"id": "kufr", "term_en": "Kufr", "term_ar": "الكفر", "term_bn": "কুফর", "def_en": "Disbelief; ingratitude towards Allah and intentional denial or rejection of divine truth.", "def_bn": "আল্লাহ ও তাঁর পাঠানো সত্যকে অস্বীকার করা, অবাধ্য হওয়া কিংবা অকৃতজ্ঞতা প্রকাশ করা।"},
    {"id": "nifaq", "term_en": "Nifaq", "term_ar": "النفاق", "term_bn": "নিফাক (কপটতা)", "def_en": "Hypocrisy: pretending outward belief while harboring disbelief or deceit in the heart.", "def_bn": "অন্তরে কুফর বা কপটতা লুকিয়ে রেখে মুখে ঈমানের বাহ্যিক প্রকাশ করা।"},
    {"id": "sabr", "term_en": "Sabr", "term_ar": "الصبر", "term_bn": "সবর (ধৈর্য)", "def_en": "Patient perseverance: holding oneself firm in obeying Allah, restraining from sin, and enduring life's trials without despair.", "def_bn": "ধৈর্য ও অবিচলতা: আল্লাহর আনুগত্যে অবিচল থাকা, পাপাচার থেকে বিরত থাকা এবং বিপদে অস্থির না হওয়া।"},
    {"id": "shukr", "term_en": "Shukr", "term_ar": "الشكر", "term_bn": "শুকর (কৃতজ্ঞতা)", "def_en": "Gratitude to Allah with the heart, tongue, and deeds for all His blessings.", "def_bn": "আল্লাহর প্রদত্ত সকল নিয়ামতের জন্য অন্তর, মুখ ও কর্মের মাধ্যমে কৃতজ্ঞতা প্রকাশ করা।"},
    {"id": "tawakkul", "term_en": "Tawakkul", "term_ar": "التوكل", "term_bn": "তাওয়াক্কুল (ভরসা)", "def_en": "Complete reliance and trust in Allah while taking the necessary and lawful practical steps.", "def_bn": "প্রয়োজনীয় বৈধ মাধ্যম ও প্রচেষ্টা গ্রহণ করার পাশাপাশি ফলাফলের জন্য সম্পূর্ণভাবে আল্লাহর উপর নির্ভর করা।"},
    {"id": "tawbah", "term_en": "Tawbah", "term_ar": "التوبة", "term_bn": "তওবা (অনুশোচনা)", "def_en": "Sincere repentance: turning back to Allah with regret over past sins, stopping them immediately, and resolving never to return to them.", "def_bn": "গুনাহের জন্য লজ্জিত হয়ে তা বর্জন করা এবং আর কখনো না করার দৃঢ় প্রতিজ্ঞা নিয়ে আল্লাহর দিকে ফিরে আসা।"},
    {"id": "akhirah", "term_en": "Akhirah", "term_ar": "الآخرة", "term_bn": "আখিরাত (পরকাল)", "def_en": "The eternal afterlife following this worldly life, encompassing the resurrection, judgment, Paradise, and Hell.", "def_bn": "দুনিয়ার জীবনের পর অনন্তকালের পরকালীন জীবন, যার মধ্যে পুনরুত্থান, হিসাব-নিকাশ, জান্নাত ও জাহান্নাম অন্তর্ভুক্ত।"},
]

STORIES = [
    {
        "id": "story-yusuf",
        "title_en": "The Story of Yusuf (peace be upon him)",
        "title_bn": "ইউসুফ (আলাইহিস সালাম)-এর কাহিনী",
        "surah_refs": ["12:1-111"],
        "episodes": [
            {"id": "yusuf-dream", "title_en": "The Dream of Eleven Stars", "title_bn": "এগারো নক্ষত্রের স্বপ্ন", "ayat": "12:4-6"},
            {"id": "yusuf-well", "title_en": "Betrayal and the Well", "title_bn": "ভাইদের ষড়যন্ত্র ও কূপে নিক্ষেপ", "ayat": "12:7-20"},
            {"id": "yusuf-house", "title_en": "Trial in the Minister's Household", "title_bn": "আযীযের ঘরে কঠিন পরীক্ষা", "ayat": "12:21-34"},
            {"id": "yusuf-prison", "title_en": "In Prison and Interpreting Dreams", "title_bn": "কারাগারে দাওয়াত ও স্বপ্নের ব্যাখ্যা", "ayat": "12:35-53"},
            {"id": "yusuf-ruler", "title_en": "Vindication and Authority in Egypt", "title_bn": "নির্দোষ প্রমাণ ও মিশরের অর্থভাণ্ডারের দায়িত্ব", "ayat": "12:54-57"},
            {"id": "yusuf-reunion", "title_en": "The Brothers Return and the Reunion", "title_bn": "ভাইদের আগমন ও পারিবারিক মিলন", "ayat": "12:58-101"}
        ]
    },
    {
        "id": "story-musa",
        "title_en": "The Story of Musa (peace be upon him)",
        "title_bn": "মূসা (আলাইহিস সালাম)-এর কাহিনী",
        "surah_refs": ["20:9-98", "26:10-68", "28:3-43"],
        "episodes": [
            {"id": "musa-birth", "title_en": "Birth and the River", "title_bn": "জন্ম ও নদীতে ভাসিয়ে দেওয়া", "ayat": "28:7-13"},
            {"id": "musa-midian", "title_en": "Escape to Midian and Marriage", "title_bn": "মাদইয়ানে পলায়ন ও বসবাস", "ayat": "28:20-28"},
            {"id": "musa-fire", "title_en": "The Burning Bush and Prophethood", "title_bn": "তূর পর্বতে আগুন ও নবুওয়াত লাভ", "ayat": "20:9-36"},
            {"id": "musa-pharaoh", "title_en": "Confronting Pharaoh and the Magicians", "title_bn": "ফেরাউনের দরবারে দাওয়াত ও জাদুকরদের ঈমান", "ayat": "20:42-76"},
            {"id": "musa-exodus", "title_en": "Parting of the Sea and Drowning of Pharaoh", "title_bn": "সাগর পাড়ি ও ফেরাউনের সলিলসমাধি", "ayat": "26:60-68"},
            {"id": "musa-calf", "title_en": "Mount Sinai and the Golden Calf Trial", "title_bn": "তূর পাহাড়ে তাওরাত লাভ ও বাছুর পূজার ফিতনা", "ayat": "20:83-98"},
            {"id": "musa-khidr", "title_en": "Journey of Knowledge with Al-Khidr", "title_bn": "খিদর (আ.)-এর সাথে জ্ঞানের সফর", "ayat": "18:60-82"}
        ]
    },
    {
        "id": "story-ibrahim",
        "title_en": "The Story of Ibrahim (peace be upon him)",
        "title_bn": "ইবরাহীম (আলাইহিস সালাম)-এর কাহিনী",
        "surah_refs": ["6:74-83", "19:41-50", "21:51-73", "37:83-113"],
        "episodes": [
            {"id": "ibrahim-youth", "title_en": "Reflecting on Stars and Calling His Father", "title_bn": "নক্ষত্র দেখে চিন্তাভাবনা ও পিতাকে দাওয়াত", "ayat": "6:74-83"},
            {"id": "ibrahim-idols", "title_en": "Breaking the Idols and the Blazing Fire", "title_bn": "মূর্তি ভাঙা ও অগ্নিকুণ্ডে নিক্ষেপ", "ayat": "21:51-70"},
            {"id": "ibrahim-sacrifice", "title_en": "The Great Vision and Sacrifice", "title_bn": "স্বপ্নে নির্দেশ ও কুরবানীর মহা পরীক্ষা", "ayat": "37:100-111"},
            {"id": "ibrahim-kaabah", "title_en": "Building the Ka'bah with Isma'il", "title_bn": "পুত্র ইসমাঈলকে নিয়ে কা'বা পুনর্নির্মাণ", "ayat": "2:125-129"}
        ]
    },
    {
        "id": "story-ukhdud",
        "title_en": "The People of the Ditch (Ashab al-Ukhdud)",
        "title_bn": "আসহাবুল উখদূদ (গর্তওয়ালাদের ঘটনা)",
        "surah_refs": ["85:4-9"],
        "episodes": [
            {"id": "ukhdud-persecution", "title_en": "Persecution of the Believing People", "title_bn": "বিশ্বাসী মুমিনদের অগ্নিকুণ্ডে পুড়িয়ে হত্যা", "ayat": "85:4-8"}
        ]
    },
    {
        "id": "story-fil",
        "title_en": "The People of the Elephant (Ashab al-Fil)",
        "title_bn": "আসহাবুল ফীল (হাতিওয়ালাদের ধ্বংসের ঘটনা)",
        "surah_refs": ["105:1-5"],
        "episodes": [
            {"id": "fil-destruction", "title_en": "Destruction of the Army of the Elephant", "title_bn": "ঝাঁকে ঝাঁকে পাখি ও পোড়ামাটির পাথরে সেনাদল ধ্বংস", "ayat": "105:1-5"}
        ]
    },
    {
        "id": "story-ad-thamud",
        "title_en": "The Destruction of 'Ad and Thamud",
        "title_bn": "'আদ ও সামূদ জাতির পরিণতি",
        "surah_refs": ["89:6-14", "91:11-15"],
        "episodes": [
            {"id": "ad-thamud-warning", "title_en": "Defiance and Punishment of Ancient Tyrants", "title_bn": "অহংকার ও খোদায়ী আযাবের বাস্তব নিদর্শন", "ayat": "89:6-14"}
        ]
    }
]

LEARNING_PATHS = [
    {
        "id": "path-foundations",
        "title_en": "Foundations of Faith (Iman & Tawhid)",
        "title_bn": "ঈমান ও তাওহীদের মূল ভিত্তি",
        "description_en": "A step-by-step beginner journey through the Quranic ayat defining faith in Allah, His angels, books, messengers, and the Last Day.",
        "description_bn": "আল্লাহ, তাঁর ফেরেশতাগণ, কিতাবসমূহ, রাসূলগণ ও পরকালে বিশ্বাস স্থাপনকারী মৌলিক আয়াতসমূহের সহজ পাঠ।",
        "steps": ["1:1-7", "2:1-5", "2:255", "2:285-286", "112:1-4", "113:1-5", "114:1-6"]
    },
    {
        "id": "path-akhlaq",
        "title_en": "Character & Everyday Ethics in the Quran",
        "title_bn": "উত্তম চরিত্র ও দৈনন্দিন শিষ্টাচার",
        "description_en": "Core Quranic principles on speech, honesty, modesty, treating parents, and fulfilling trusts.",
        "description_bn": "কথা বলার শালীনতা, সততা, পিতা-মাতার খেদমত ও আমানত রক্ষার বিষয়ে কুরআনের অমূল্য দিকনির্দেশনা।",
        "steps": ["17:23-24", "49:10-12", "103:1-3", "104:1-9", "107:1-7"]
    },
    {
        "id": "path-prophets",
        "title_en": "Lessons from the Lives of the Prophets",
        "title_bn": "নবীদের জীবন থেকে শিক্ষণীয় ঘটনা",
        "description_en": "Explore how Ibrahim, Musa, Yusuf, and Prophet Muhammad ﷺ navigated trials with unwavering trust in Allah.",
        "description_bn": "কঠিনতম পরীক্ষায় নবীদের অপরিসীম ধৈর্য ও আল্লাহর উপর তাওয়াক্কুলের বাস্তব দৃষ্টান্ত।",
        "steps": ["12:1-20", "20:9-36", "21:51-70", "93:1-11", "94:1-8"]
    }
]


def main():
    datasets = [
        ("people.json", PEOPLE),
        ("places.json", PLACES),
        ("nations.json", NATIONS),
        ("unseen.json", UNSEEN),
        ("names_of_allah.json", NAMES_OF_ALLAH),
        ("glossary.json", GLOSSARY),
        ("stories.json", STORIES),
        ("learning_paths.json", LEARNING_PATHS),
    ]
    for filename, data in datasets:
        path = os.path.join(KB_DIR, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Generated {filename} ({len(data)} items)")


if __name__ == "__main__":
    main()
