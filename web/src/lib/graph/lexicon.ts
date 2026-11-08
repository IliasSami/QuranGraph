/**
 * Quranic Root Lexicon, Transliteration & Ontological Mappings
 * Provides standard academic transliteration, English conceptual glosses,
 * and Bengali translations for roots, themes, and entities.
 */

// Arabic letter to scholarly transliteration table
const ARABIC_CHAR_TRANSLIT: Record<string, string> = {
  "ء": "’", "آ": "ā", "أ": "’", "إ": "’", "ا": "a", "ب": "b", "ت": "t",
  "ث": "th", "ج": "j", "ح": "ḥ", "خ": "kh", "د": "d", "ذ": "dh", "ر": "r",
  "ز": "z", "س": "s", "ش": "sh", "ص": "ṣ", "ض": "ḍ", "ط": "ṭ", "ظ": "ẓ",
  "ع": "‘", "غ": "gh", "ف": "f", "ق": "q", "ك": "k", "ل": "l", "م": "m",
  "ن": "n", "ه": "h", "ة": "h", "و": "w", "ي": "y", "ى": "ā"
};

/**
 * Transliterates an Arabic triliteral or quadriliteral root (e.g. "علم" -> "‘-l-m")
 */
export function transliterateRoot(arabicRoot: string): string {
  if (!arabicRoot) return "";
  const clean = arabicRoot.replace(/[\u064B-\u065F\u0670\s]/g, "");
  const chars: string[] = [];
  for (const ch of clean) {
    chars.push(ARABIC_CHAR_TRANSLIT[ch] || ch);
  }
  return chars.join("-");
}

export interface RootGloss {
  translit: string;
  en: string;
  bn: string;
}

/**
 * High-frequency & theological root dictionary
 */
export const CORE_ROOT_GLOSSES: Record<string, RootGloss> = {
  "أله": { translit: "’-l-h", en: "Divinity / Worship (Allah)", bn: "উপাসনা ও আল্লাহ" },
  "ربب": { translit: "r-b-b", en: "Lordship & Sustenance (Rabb)", bn: "প্রতিপালন ও প্রভুত্ব" },
  "أمن": { translit: "’-m-n", en: "Faith, Security & Trust (Iman)", bn: "ঈমান, নিরাপত্তা ও বিশ্বাস" },
  "علم": { translit: "‘-l-m", en: "Knowledge & Knowing (‘Ilm)", bn: "জ্ঞান ও জানা" },
  "قول": { translit: "q-w-l", en: "Speech & Saying (Qawl)", bn: "কথা ও বাণী" },
  "كون": { translit: "k-w-n", en: "Being & Existence (Kana)", bn: "হওয়া ও অস্তিত্ব" },
  "أنس": { translit: "’-n-s", en: "Humankind & Fellowship (Insan)", bn: "মানবজাতি ও মানুষ" },
  "سفه": { translit: "s-f-h", en: "Foolishness & Impudence (Safih)", bn: "নির্বুদ্ধিতা ও মূর্খতা" },
  "رحم": { translit: "r-ḥ-m", en: "Mercy & Compassion (Rahmah)", bn: "দয়া ও অনুগ্রহ" },
  "كفر": { translit: "k-f-r", en: "Disbelief & Ingratitude (Kufr)", bn: "অস্বীকৃতি ও কুফরি" },
  "حمد": { translit: "ḥ-m-d", en: "Praise & Gratitude (Hamd)", bn: "প্রশংসা ও কৃতজ্ঞতা" },
  "صبر": { translit: "ṣ-b-r", en: "Patience & Steadfastness (Sabr)", bn: "ধৈর্য ও সহনশীলতা" },
  "هدى": { translit: "h-d-y", en: "Guidance & Direction (Huda)", bn: "হিদায়াত ও পথপ্রদর্শন" },
  "نفق": { translit: "n-f-q", en: "Hypocrisy & Spending (Nifaq)", bn: "মুনাফেকি ও অর্থব্যয়" },
  "كبر": { translit: "k-b-r", en: "Greatness & Arrogance (Kibr)", bn: "মহত্ত্ব ও অহংকার" },
  "ظلم": { translit: "ẓ-l-m", en: "Injustice & Darkness (Zulm)", bn: "অন্যায়, জুলুম ও অন্ধকার" },
  "حقق": { translit: "ḥ-q-q", en: "Truth & Right (Haqq)", bn: "সত্য ও অধিকার" },
  "سمع": { translit: "s-m-‘", en: "Hearing & Listening (Sam‘)", bn: "শ্রবণ ও শোনা" },
  "بصر": { translit: "b-ṣ-r", en: "Sight & Insight (Basar)", bn: "দৃষ্টি ও অন্তর্দৃষ্টি" },
  "عمل": { translit: "‘-m-l", en: "Deeds & Action (‘Amal)", bn: "কর্ম ও আমল" },
  "كتب": { translit: "k-t-b", en: "Writing & Decree (Kitab)", bn: "কিতাব ও বিধান" },
  "خلق": { translit: "kh-l-q", en: "Creation & Origin (Khalq)", bn: "সৃষ্টি ও উৎপত্তি" },
  "عبد": { translit: "‘-b-d", en: "Servitude & Worship (‘Ibadah)", bn: "দাসত্ব ও উপাসনা" },
  "شكر": { translit: "sh-k-r", en: "Thankfulness & Gratitude (Shukr)", bn: "শোকর ও কৃতজ্ঞতা" },
  "ذكر": { translit: "dh-k-r", en: "Remembrance & Reminder (Dhikr)", bn: "স্মরণ ও উপদেশ" },
  "نصر": { translit: "n-ṣ-r", en: "Aid & Victory (Nasr)", bn: "সাহায্য ও বিজয়" },
  "خوف": { translit: "kh-w-f", en: "Fear & Reverence (Khawf)", bn: "ভয় ও আশঙ্কা" },
  "توب": { translit: "t-w-b", en: "Repentance & Return (Tawbah)", bn: "তওবা ও প্রত্যাবর্তন" },
  "صدق": { translit: "ṣ-d-q", en: "Truthfulness & Sincerity (Sidq)", bn: "সত্যবাদিতা ও সততা" },
  "كذب": { translit: "k-dh-b", en: "Falsehood & Denial (Kidhb)", bn: "মিথ্যা ও অসত্য" },
  "غفر": { translit: "gh-f-r", en: "Forgiveness & Pardon (Maghfirah)", bn: "ক্ষমা ও মার্জনা" },
  "ملك": { translit: "m-l-k", en: "Sovereignty & Kingdom (Mulk)", bn: "রাজত্ব ও আধিপত্য" },
  "رسل": { translit: "r-s-l", en: "Messengership & Message (Risalah)", bn: "রাসূল ও পয়গাম" },
  "نزل": { translit: "n-z-l", en: "Revelation & Descent (Tanzil)", bn: "নাযিল ও অবতীর্ণ" },
  "أمر": { translit: "’-m-r", en: "Command & Affair (Amr)", bn: "আদেশ ও নির্দেশ" },
  "نهي": { translit: "n-h-y", en: "Prohibition & Restraint (Nahy)", bn: "নিষেধ ও বারণ" },
  "خير": { translit: "kh-y-r", en: "Goodness & Virtue (Khayr)", bn: "কল্যাণ ও উত্তম" },
  "شرر": { translit: "sh-r-r", en: "Evil & Harm (Sharr)", bn: "মন্দ ও অকল্যাণ" },
  "حكم": { translit: "ḥ-k-m", en: "Wisdom & Judgment (Hikmah)", bn: "প্রজ্ঞা ও ফায়সালা" },
  "عدل": { translit: "‘-d-l", en: "Justice & Balance (‘Adl)", bn: "ন্যায়বিচার ও ইনসাফ" },
  "قسط": { translit: "q-s-ṭ", en: "Equity & Fairness (Qist)", bn: "ন্যায়পরায়ণতা" },
  "جنن": { translit: "j-n-n", en: "Paradise & Hidden (Jannah)", bn: "জান্নাত ও গোপনীয়" },
  "نور": { translit: "n-w-r", en: "Light & Illumination (Nur)", bn: "আলো ও নূর" },
  "نار": { translit: "n-w-r", en: "Fire & Hellfire (Nar)", bn: "আগুন ও জাহান্নাম" },
  "موت": { translit: "m-w-t", en: "Death & Mortality (Mawt)", bn: "মৃত্যু ও মরণ" },
  "حيي": { translit: "ḥ-y-y", en: "Life & Vivacity (Hayat)", bn: "জীবন ও হায়াত" },
  "روح": { translit: "r-w-ḥ", en: "Spirit & Comfort (Ruh)", bn: "আত্মা ও শান্তি" },
  "قلب": { translit: "q-l-b", en: "Heart & Turning (Qalb)", bn: "অন্তর ও হৃদয়" },
  "نفس": { translit: "n-f-s", en: "Soul, Self & Desire (Nafs)", bn: "নফস ও আত্মা" },
  "يوم": { translit: "y-w-m", en: "Day & Era (Yawm)", bn: "দিন ও কাল" },
  "سجد": { translit: "s-j-d", en: "Prostration & Submission (Sujud)", bn: "সিজদা ও আনুগত্য" },
  "صلي": { translit: "ṣ-l-w", en: "Prayer & Connection (Salah)", bn: "নামায ও সংযোগ" },
  "زكو": { translit: "z-k-w", en: "Purity & Charity (Zakah)", bn: "পবিত্রতা ও যাকাত" },
  "صوم": { translit: "ṣ-w-m", en: "Fasting & Restraint (Sawm)", bn: "রোজা ও সংযম" },
  "حجج": { translit: "ḥ-j-j", en: "Pilgrimage & Argument (Hajj)", bn: "হজ ও বিতর্ক" },
  "جهد": { translit: "j-h-d", en: "Striving & Struggle (Jihad)", bn: "প্রচেষ্টা ও সাধনা" },
  "فتن": { translit: "f-t-n", en: "Trial, Test & Tribulation (Fitnah)", bn: "পরীক্ষা ও ফিতনা" },
  "أود": { translit: "’-w-d", en: "To Burden / Burdening (Hapax 2:255)", bn: "কষ্টসাধ্য হওয়া / বোঝা হওয়া" }
};

/**
 * Returns formatted root label with transliteration and English conceptual meaning
 */
export function getRootGloss(root: string): { label_en: string; label_ar: string; label_bn: string } {
  const gloss = CORE_ROOT_GLOSSES[root];
  const translit = gloss ? gloss.translit : transliterateRoot(root);
  const label_ar = root.split("").join(" ");
  if (gloss) {
    return {
      label_en: `${translit} · ${gloss.en}`,
      label_ar,
      label_bn: gloss.bn
    };
  }
  return {
    label_en: `Root ${translit}`,
    label_ar,
    label_bn: `আরবি মূলশব্দ (${translit})`
  };
}

/**
 * Theme to Arabic Islamic terminology and Bengali translations
 */
export const THEME_DICTIONARY: Record<string, { ar: string; bn: string; enTitle: string }> = {
  "knowledge": { ar: "العلم والمعرفة", bn: "জ্ঞান ও প্রজ্ঞা", enTitle: "Knowledge & Understanding" },
  "faith": { ar: "الإيمان واليقين", bn: "ঈমান ও সুদৃঢ় বিশ্বাস", enTitle: "Faith & Conviction" },
  "hypocrisy": { ar: "النفاق والمنافقون", bn: "মুনাফেকি ও কপটতা", enTitle: "Hypocrisy (Nifaq)" },
  "arrogance": { ar: "الكبر والغرور", bn: "অহংকার ও দাম্ভিকতা", enTitle: "Arrogance & Pride (Kibr)" },
  "patience": { ar: "الصبر والتحمل", bn: "ধৈর্য ও দৃঢ়তা", enTitle: "Patience & Perseverance (Sabr)" },
  "gratitude": { ar: "الشكر والاعتراف", bn: "কৃতজ্ঞতা ও শোকর", enTitle: "Gratitude & Thanksgiving" },
  "tawhid": { ar: "توحيد الله تعالى", bn: "আল্লাহর একত্ববাদ (তাওহীদ)", enTitle: "Oneness of God (Tawhid)" },
  "guidance": { ar: "الهداية والرشاد", bn: "হিদায়াত ও সঠিক পথ", enTitle: "Divine Guidance (Hidayah)" },
  "justice": { ar: "العدل والقسط", bn: "ন্যায়বিচার ও ইনসাফ", enTitle: "Justice & Fairness (‘Adl)" },
  "creation": { ar: "خلق السموات والأرض", bn: "মহাবিশ্ব ও মানব সৃষ্টি", enTitle: "Creation of the Cosmos" },
  "the-last-day": { ar: "اليوم الآخر والبعث", bn: "কিয়ামত ও পরকাল", enTitle: "The Day of Resurrection" },
  "judgment": { ar: "الحساب والجزاء", bn: "হিসাব ও প্রতিদান", enTitle: "Divine Reckoning & Judgment" },
  "remembrance-of-allah": { ar: "ذكر الله وتسبيحه", bn: "আল্লাহর জিকির ও স্মরণ", enTitle: "Remembrance of Allah (Dhikr)" },
  "allah's-mercy": { ar: "رحمة الله الواسعة", bn: "আল্লাহর প্রশস্ত রহমত", enTitle: "The Boundless Mercy of Allah" },
  "allah's-power": { ar: "قدرة الله وسلطانه", bn: "আল্লাহর কুদরত ও মহিমা", enTitle: "Divine Power & Sovereignty" },
  "worship": { ar: "عبادة الله وإخلاص الدين", bn: "আল্লাহর একনিষ্ঠ ইবাদত", enTitle: "Sincere Worship & Devotion" },
  "repentance": { ar: "التوبة والاستغفار", bn: "তওবা ও ক্ষমা প্রার্থনা", enTitle: "Repentance & Forgiveness" },
  "charity": { ar: "الإنفاق في سبيل الله", bn: "আল্লাহর পথে দান", enTitle: "Charity & Spending (Infaq)" },
  "prayer": { ar: "إقامة الصلاة", bn: "নামায কায়েম করা", enTitle: "Establishing Prayer (Salah)" },
  "prophethood": { ar: "الرسالة والنبوة", bn: "রিসালাত ও নবুওয়াত", enTitle: "Prophethood & Revelation" },
  "truth": { ar: "الحق والصدق", bn: "সত্য ও ন্যায়নিষ্ঠতা", enTitle: "Truth & Sincerity (Haqq)" },
  "piety": { ar: "التقوى ومخافة الله", bn: "তাকওয়া ও আল্লাহভীতি", enTitle: "Piety & God-Consciousness (Taqwa)" },
  "story-of-yusuf": { ar: "قصة يوسف عليه السلام", bn: "ইউসুফ (আ.)-এর ধারাবাহিক ঘটনা", enTitle: "Narrative of Prophet Yusuf" },
  "prophetic-dream": { ar: "الرؤيا الصادقة", bn: "সত্য স্বপ্ন ও তার তাৎপর্য", enTitle: "Prophetic True Dreams" },
  "father-and-son": { ar: "بر الوالدين والعلاقة الأسرية", bn: "পিতা-পুত্রের সম্মান ও সম্পর্ক", enTitle: "Father-Son Reverence" },
  "respectful-speech": { ar: "أدب الحديث والقول السديد", bn: "উত্তম ও মার্জিত বাক্য", enTitle: "Speech Etiquette & Kindness" }
};

/**
 * Entity Arabic and Bengali fallbacks for missing values
 */
export const ENTITY_FALLBACKS: Record<string, { ar: string; bn: string }> = {
  "person:the-companions": { ar: "الصحابة الكرام", bn: "সাহাবায়ে কেরাম (রা.)" },
  "person:the-righteous": { ar: "الصالحون", bn: "নেককার বান্দাগণ" },
  "nation:people-of-makkah": { ar: "أهل مكة", bn: "মক্কার কুরাইশ সমাজ" },
  "nation:court-of-pharaoh": { ar: "ملأ فرعون", bn: "ফেরাউনের রাজদরবার" },
  "nation:sabbath-violators": { ar: "أصحاب السبت", bn: "শনিবারের সীমালঙ্ঘনকারী সম্প্রদায়" },
  "unseen:judgment-hour": { ar: "قيام الساعة", bn: "কিয়ামত ও হিসাবের ক্ষণ" },
  "unseen:the-pond-al-hawd": { ar: "حوض الكوثر", bn: "হাওযে কাউসার" },
  "unseen:records-of-deeds": { ar: "صحائف الأعمال", bn: "আমলনামা" },
  "unseen:noble-throne": { ar: "العرش المجيد", bn: "সম্মানিত আরশ" },
  "unseen:devils-shayatin": { ar: "الشياطين", bn: "শয়তানের দল" },
  "place:junction-of-the-two-seas": { ar: "مجمع البحرين", bn: "দুই সাগরের মিলনস্থল" },
  "unseen:al-kursi": { ar: "الكرسي", bn: "কুরসী (আল্লাহর আসন)" },
  "unseen:al-arsh": { ar: "العرش العظيم", bn: "মহা আরশ" }
};

/**
 * Returns localized theme metadata
 */
export function getThemeGloss(themeId: string, labelEn?: string): { en: string; ar: string; bn: string } {
  const cleanKey = themeId.toLowerCase().replace(/^(theme|theme-exp)[:\-]/, "").trim();
  const entry = THEME_DICTIONARY[cleanKey];
  if (entry) {
    return {
      en: entry.enTitle,
      ar: entry.ar,
      bn: entry.bn
    };
  }
  const title = labelEn || cleanKey.replace(/-/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
  return {
    en: title,
    ar: "مفهوم قرآني",
    bn: "কুরআনিক বিষয়বস্তু"
  };
}
