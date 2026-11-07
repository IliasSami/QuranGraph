import surahsData from "./surahs.json" with { type: "json" };
import { arabicKey, asciiDigits, banglaKey, editDistance, latinFold, scriptOf } from "./normalize.ts";

export interface AyahReference {
  surah: number;
  ayah: number;
  ref: string; // "2:255"
}

export interface SurahInfo {
  id: number;
  name_ar: string;
  name_translit: string;
  name_en: string;
  name_bn: string;
  ayat: number;
  type?: string;
  revelation_order?: number;
  rukus?: number;
}

const SURAHS: SurahInfo[] = surahsData;

export function getSurahInfo(id: number): SurahInfo | undefined {
  return SURAHS[id - 1];
}

function cleanName(s: string): string {
  return latinFold(s)
    .replace(/^(surah|sura|chapter)\s+/i, "")
    .replace(/^(al|el|ar|as|at|ad|an|ash|az|adh|ath)[-\s]/i, "")
    .replace(/[^a-z0-9]/g, "");
}

function cleanAr(s: string): string {
  let k = arabicKey(s);
  if (k.startsWith("سوره") || k.startsWith("سورة")) {
    k = k.replace(/^سورة?/, "");
  }
  if (k.startsWith("ال")) k = k.slice(2);
  return k.trim();
}

function cleanBn(s: string): string {
  let k = banglaKey(s);
  if (k.startsWith("সুরা") || k.startsWith("সূরা")) {
    k = k.replace(/^(সুরা|সূরা)[-_\s]*/, "");
  }
  if (k.startsWith("আল") || k.startsWith("আর") || k.startsWith("আন") || k.startsWith("আশ") || k.startsWith("আদ")) {
    k = k.replace(/^(আল|আর|আন|আশ|আদ)[-_\s]*/, "");
  }
  return k.replace(/[-_\s]/g, "");
}

// Build fast lookup table
const nameToSurah = new Map<string, number>();

function registerSurahName(name: string, id: number) {
  if (!name) return;
  const sc = scriptOf(name);
  let k = "";
  if (sc === "bangla") {
    k = cleanBn(name);
  } else if (sc === "arabic") {
    k = cleanAr(name);
  } else {
    k = cleanName(name);
  }
  if (k) {
    nameToSurah.set(k, id);
  }
}

for (const s of SURAHS) {
  nameToSurah.set(String(s.id), s.id);
  registerSurahName(s.name_translit, s.id);
  registerSurahName(s.name_en, s.id);
  registerSurahName(s.name_ar, s.id);
  registerSurahName(s.name_bn, s.id);
}

// Comprehensive aliases, common phonetic variations & English meanings
const ALIASES: Record<number, string[]> = {
  1: ["fatiha", "fatihah", "fateha", "alfatiha", "alfatihah", "hamd", "opening", "আল ফাতিহা", "ফাতিহা"],
  2: ["baqara", "baqarah", "baqra", "bakara", "cow", "বাকারা", "গাভী"],
  3: ["imran", "aliimran", "alimran", "aalimran", "aleimran", "family of imran", "ইমরান", "আলে ইমরান"],
  4: ["nisa", "nisaa", "annisa", "women", "নিসা", "নারী"],
  5: ["maidah", "maida", "maydah", "almaidah", "table", "মাইদাহ", "খাবার পাত্র"],
  6: ["anam", "anam", "alan'am", "alanam", "cattle", "আনআম", "গৃহপালিত পশু"],
  7: ["araf", "araf", "al-araf", "alaraf", "heights", "আরাফ", "উঁচু স্থানসমূহ"],
  8: ["anfal", "alanfal", "spoils of war", "আনফাল", "যুদ্ধলব্ধ ধন-সম্পদ"],
  9: ["tawbah", "tawba", "tauba", "taubah", "baraat", "baraah", "repentance", "তাওবাহ", "তাওবা", "অনুশোচনা"],
  10: ["yunus", "jonah", "ইউনুস"],
  11: ["hud", "হুদ"],
  12: ["yusuf", "yousuf", "joseph", "ইউসুফ"],
  13: ["rad", "rad", "arrad", "thunder", "রাদ", "বজ্রনাদ"],
  14: ["ibrahim", "abraham", "ইব্রাহিম", "ইবরাহিম"],
  15: ["hijr", "alhijr", "rocky tract", "হিজর"],
  16: ["nahl", "annahl", "bee", "bees", "নাহল", "মৌমাছি"],
  17: ["isra", "alisra", "baniisrail", "baniisrael", "night journey", "ইসরা", "বনী ইসরাঈল"],
  18: ["kahf", "kahaf", "alkahf", "cave", "কাহফ", "কাহাফ", "গুহা"],
  19: ["maryam", "mariam", "mariyam", "mary", "মারইয়াম", "মরিয়ম"],
  20: ["taha", "taha", "তা-হা", "ত্বাহা"],
  21: ["anbiya", "anbiyaa", "alanbiya", "prophets", "আম্বিয়া", "নবীগণ"],
  22: ["hajj", "alhajj", "pilgrimage", "হজ্ব", "হজ"],
  23: ["muminun", "muminun", "believers", "মুমিনুন", "বিশ্বাসীগণ"],
  24: ["nur", "noor", "annur", "light", "নূর", "নুর", "আলো"],
  25: ["furqan", "alfurqan", "criterion", "ফুরকান"],
  26: ["shuara", "ashshu'ara", "poets", "শুআরা", "কবিগণ"],
  27: ["naml", "annaml", "ant", "ants", "নমল", "পিপীলিকা"],
  28: ["qasas", "alqasas", "stories", "কাসাস", "কাহিনি"],
  29: ["ankabut", "ankaboot", "spider", "আনকাবুত", "মাকড়সা"],
  30: ["rum", "room", "arrum", "romans", "রুম", "রোমানগণ"],
  31: ["luqman", "lokman", "লুকমান"],
  32: ["sajdah", "sajda", "prostration", "সাজদাহ", "সেজদা"],
  33: ["ahzab", "alahzab", "confederates", "আহযাব"],
  34: ["saba", "sheba", "সাবা"],
  35: ["fatir", "alfatir", "originator", "ফাতির"],
  36: ["yasin", "yaseen", "yasin", "ya-sin", "ইয়াসিন", "ইয়াসীন"],
  37: ["saffat", "assaffat", "সফফাত"],
  38: ["sad", "saad", "সোয়াদ", "সাদ"],
  39: ["zumar", "azzumar", "groups", "যুমার"],
  40: ["ghafir", "alghafir", "mumin", "forgiver", "গাফির", "মুমিন"],
  41: ["fussilat", "hamimsajdah", "ফুসসিলাত"],
  42: ["shura", "ashshura", "consultation", "শুরা"],
  43: ["zukhruf", "azzukhruf", "gold", "যুখরুফ"],
  44: ["dukhan", "addukhan", "smoke", "দুখান", "ধোঁয়া"],
  45: ["jathiyah", "jathiya", "kneeling", "জাসিয়াহ"],
  46: ["ahqaf", "alahqaf", "sand dunes", "আহকাফ"],
  47: ["muhammad", "mohammad", "মুহাম্মদ"],
  48: ["fath", "alfath", "victory", "ফাতহ", "বিজয়"],
  49: ["hujurat", "alhujurat", "apartments", "হুজুরাত"],
  50: ["qaf", "qaaf", "কাফ"],
  51: ["dhariyat", "adhdhariyat", "যারিয়াত"],
  52: ["tur", "toor", "attur", "mount", "তূর", "তুর"],
  53: ["najm", "annajm", "star", "নাজম", "তারা"],
  54: ["qamar", "alqamar", "moon", "ক্বামার", "চাঁদ"],
  55: ["rahman", "rehman", "arrahman", "beneficent", "merciful", "রহমান", "পরম করুণাময়"],
  56: ["waqia", "waqiah", "waqea", "alwaqiah", "inevitable", "ওয়াকিয়াহ", "ওয়াকিয়া", "সংঘটিত ঘটনা"],
  57: ["hadid", "hadeed", "alhadid", "iron", "হাদীদ", "লোহা"],
  58: ["mujadila", "almujadila", "মুজাদালাহ"],
  59: ["hashr", "alhashr", "exile", "হাশর", "সমাবেশ"],
  60: ["mumtahanah", "almumtahanah", "মুমতাহিনা"],
  61: ["saff", "assaff", "ranks", "সফ", "সারিবদ্ধ"],
  62: ["jumuah", "jumua", "jummah", "friday", "জুমুআহ", "জুমা"],
  63: ["munafiqun", "hypocrites", "মুনাফিকুন"],
  64: ["taghabun", "attaghabun", "তাগাবুন"],
  65: ["talaq", "attalaq", "divorce", "তালাক"],
  66: ["tahrim", "attahrim", "prohibition", "তাহরীম"],
  67: ["mulk", "almulk", "molk", "dominion", "sovereignty", "মুলক", "সার্বভৌমত্ব"],
  68: ["qalam", "alqalam", "noon", "pen", "কলম"],
  69: ["haqqah", "alhaqqah", "reality", "হাক্কাহ"],
  70: ["maarij", "almaarij", "মাআরিজ"],
  71: ["nuh", "nooh", "noah", "নূহ"],
  72: ["jinn", "aljinn", "জিন"],
  73: ["muzzammil", "almuzzammil", "enshrouded", "মুযযাম্মিল"],
  74: ["muddathir", "almuddathir", "cloaked", "মুদ্দাসসির"],
  75: ["qiyamah", "qiyama", "resurrection", "কিয়ামাহ", "পুনরুত্থান"],
  76: ["insan", "dahr", "alinsan", "man", "মানুষ", "ইনসান"],
  77: ["mursalat", "almursalat", "মুরসালাত"],
  78: ["naba", "annaba", "tidings", "নাবা", "মহাসংবাদ"],
  79: ["naziat", "annaziat", "নাযিআত"],
  80: ["abasa", "frowned", "আবাসা"],
  81: ["takwir", "attakwir", "overthrowing", "তাকভীর"],
  82: ["infitar", "alinfitar", "cleaving", "ইনফিতার"],
  83: ["mutaffifin", "defrauders", "মুতাফফিফীন"],
  84: ["inshiqaq", "alinshiqaq", "splitting", "ইনশিকাক"],
  85: ["buruj", "alburuj", "constellations", "বুরুজ"],
  86: ["tariq", "attariq", "night comer", "তারিক"],
  87: ["ala", "ala", "alala", "most high", "আলা"],
  88: ["ghashiyah", "ghashiya", "overwhelming", "গাশিয়াহ"],
  89: ["fajr", "alfajr", "dawn", "ফজর", "ভোর"],
  90: ["balad", "albalad", "city", "বালাদ", "নগরী"],
  91: ["shams", "ashshams", "sun", "শামস", "সূর্য"],
  92: ["layl", "lail", "allayl", "night", "লাইল", "রাত"],
  93: ["duha", "adduha", "morning", "দোহা", "পূর্বাহ্ণ"],
  94: ["sharh", "inshirah", "relief", "ইনশিরাহ", "বক্ষ প্রশস্তকরণ"],
  95: ["tin", "teen", "attin", "fig", "তীন", "ডুমুর"],
  96: ["alaq", "alalaq", "clot", "iqra", "আলাক", "ইকরা", "রক্তপিণ্ড"],
  97: ["qadr", "alqadr", "power", "decree", "কদর", "মহিমান্বিত রাত"],
  98: ["bayyinah", "bayyina", "clear evidence", "বাইয়্যিনাহ"],
  99: ["zalzalah", "zilzal", "earthquake", "যিলযাল", "ভূমিকম্প"],
  100: ["adiyat", "aladiyat", "chargers", "আদিয়াত"],
  101: ["qariah", "alqariah", "calamity", "কারিআহ"],
  102: ["takathur", "attakathur", "rivalry", "তাকাসুর"],
  103: ["asr", "alasr", "time", "আসর", "কাল"],
  104: ["humazah", "alhumazah", "slanderer", "হুমাযাহ"],
  105: ["fil", "feel", "alfil", "elephant", "ফীল", "হাতি"],
  106: ["quraysh", "quraish", "কুরাইশ"],
  107: ["maun", "maun", "small kindnesses", "মাউন"],
  108: ["kawthar", "kauthar", "abundance", "কাউসার"],
  109: ["kafirun", "disbelievers", "কাফিরুন"],
  110: ["nasr", "annasr", "victory", "help", "নাসর", "সাহায্য"],
  111: ["masad", "lahab", "almasad", "palm fiber", "লাহাব", "মাসাদ"],
  112: ["ikhlas", "alikhlas", "sincerity", "oneness", "ইখলাস"],
  113: ["falaq", "alfalaq", "daybreak", "ফালাক"],
  114: ["nas", "naas", "annas", "mankind", "নাস", "মানুষজাতি"]
};

for (const [sIdStr, list] of Object.entries(ALIASES)) {
  const sId = parseInt(sIdStr, 10);
  for (const alias of list) {
    registerSurahName(alias, sId);
  }
}

function resolveSurahName(raw: string): number | null {
  if (!raw) return null;
  const sc = scriptOf(raw);
  let k = "";
  if (sc === "bangla") {
    k = cleanBn(raw);
  } else if (sc === "arabic") {
    k = cleanAr(raw);
  } else {
    k = cleanName(raw);
  }
  if (!k) return null;

  let sId = nameToSurah.get(k);
  if (sId) return sId;

  // Fuzzy fallback: editDistance <= 1 for terms of length >= 4
  if (k.length >= 4) {
    for (const [key, id] of nameToSurah.entries()) {
      if (key.length >= 4 && editDistance(k, key, 1) <= 1) {
        return id;
      }
    }
  }

  return null;
}

/**
 * Parses queries that specify ONLY a Surah (e.g. "baqarah", "surah yasin", "al mulk", "সূরা কাহাফ", "سورة الكهف", "surah 18")
 * Returns surah ID (1-114) or null.
 */
export function parseSurahOnly(rawQuery: string): number | null {
  if (!rawQuery) return null;
  // Clean surrounding punctuation
  const q = asciiDigits(rawQuery.trim().replace(/^[\s\p{P}]+|[\s\p{P}]+$/gu, "")).normalize("NFC");

  // Pattern: "surah 18", "chapter 18", "সূরা ১৮", "سورة 18"
  const numMatch = q.match(/^(?:surah|sura|chapter|সূরা|সুরা|سورة|سوره)\s*(\d{1,3})$/i);
  if (numMatch) {
    const sId = parseInt(numMatch[1], 10);
    if (sId >= 1 && sId <= 114) return sId;
  }

  // Pure digits if exactly in range 1-114
  if (/^\d{1,3}$/.test(q)) {
    const num = parseInt(q, 10);
    // Only treat as surah if user explicitly asked or small number
    if (num >= 1 && num <= 114) return num;
  }

  // Name match
  const stripped = q.replace(/^(?:surah|sura|chapter|সূরা|সুরা|سورة|سوره)\s+/i, "");
  return resolveSurahName(stripped);
}

/**
 * Parses queries like:
 * - "2:255", "2 255", "2/255"
 * - "surah 2 verse 255", "chapter 2 verse 255"
 * - "verse 255 of surah 2", "ayah 255 of baqarah"
 * - "al-baqarah 255", "yasin 12", "kahf 10"
 * - "বাকারা ২৫৫", "সুরা ২ আয়াত ২৫৫", "সূরা বাকারা ২৫৫"
 * - "البقرة ٢٥٥", "سورة البقرة اية 255"
 * into a structured AyahReference or null.
 */
export function parseReference(rawQuery: string): AyahReference | null {
  if (!rawQuery) return null;

  // Clean surrounding punctuation like "?", "!", ".", "(", ")", quotes
  const q = asciiDigits(rawQuery.trim().replace(/^[\s\p{P}]+|[\s\p{P}]+$/gu, "")).normalize("NFC");

  // Pattern 1: Pure digits "2:255" or "2 255" or "2/255" or "2-255"
  const colonMatch = q.match(/^(\d{1,3})[:\/\s-]+(\d{1,3})$/);
  if (colonMatch) {
    const s = parseInt(colonMatch[1], 10);
    const a = parseInt(colonMatch[2], 10);
    if (s >= 1 && s <= 114) {
      const maxA = SURAHS[s - 1].ayat;
      if (a >= 1 && a <= maxA) {
        return { surah: s, ayah: a, ref: `${s}:${a}` };
      }
    }
  }

  // Pattern 2: Natural language English: "surah 2 verse 255", "surah 2 ayah 255", "chapter 2 verse 255"
  const nlEnMatch = q.match(/^(?:surah|sura|chapter)\s+(\d{1,3})\s+(?:verse|ayah|ayat|v|a)\s+(\d{1,3})$/i);
  if (nlEnMatch) {
    const s = parseInt(nlEnMatch[1], 10);
    const a = parseInt(nlEnMatch[2], 10);
    if (s >= 1 && s <= 114 && a >= 1 && a <= SURAHS[s - 1].ayat) {
      return { surah: s, ayah: a, ref: `${s}:${a}` };
    }
  }

  // Pattern 3: Natural language reverse: "verse 255 of surah 2", "ayah 255 surah 2"
  const nlRevMatch = q.match(/^(?:verse|ayah|ayat|v|a)\s+(\d{1,3})\s+(?:of|in|from)?\s*(?:surah|sura|chapter)?\s*(\d{1,3})$/i);
  if (nlRevMatch) {
    const a = parseInt(nlRevMatch[1], 10);
    const s = parseInt(nlRevMatch[2], 10);
    if (s >= 1 && s <= 114 && a >= 1 && a <= SURAHS[s - 1].ayat) {
      return { surah: s, ayah: a, ref: `${s}:${a}` };
    }
  }

  // Pattern 4: Named surah with natural language verse: "surah baqarah verse 255", "baqarah ayah 255"
  const namedNlMatch = q.match(/^(?:surah|sura|chapter)?\s*([a-zA-Z\s'-]+?)\s+(?:verse|ayah|ayat|v|a)\s+(\d{1,3})$/i);
  if (namedNlMatch) {
    const sId = resolveSurahName(namedNlMatch[1].trim());
    const a = parseInt(namedNlMatch[2], 10);
    if (sId && sId >= 1 && sId <= 114 && a >= 1 && a <= SURAHS[sId - 1].ayat) {
      return { surah: sId, ayah: a, ref: `${sId}:${a}` };
    }
  }

  // Pattern 5: Reverse named: "verse 255 of baqarah", "ayah 255 surah yasin"
  const revNamedMatch = q.match(/^(?:verse|ayah|ayat|v|a)\s+(\d{1,3})\s+(?:of|in|from)?\s*(?:surah|sura)?\s*([a-zA-Z\s'-]+)$/i);
  if (revNamedMatch) {
    const a = parseInt(revNamedMatch[1], 10);
    const sId = resolveSurahName(revNamedMatch[2].trim());
    if (sId && sId >= 1 && sId <= 114 && a >= 1 && a <= SURAHS[sId - 1].ayat) {
      return { surah: sId, ayah: a, ref: `${sId}:${a}` };
    }
  }

  // Pattern 6a: Bangla digits: "সুরা ২ আয়াত ২৫৫", "সুরা ২ ২৫৫"
  const bnDigitsMatch = q.match(/^(?:সূরা|সুরা)\s*(\d{1,3})\s*(?:আয়াত|আয়াত|নং)?\s*(\d{1,3})$/);
  if (bnDigitsMatch) {
    const sId = parseInt(bnDigitsMatch[1], 10);
    const a = parseInt(bnDigitsMatch[2], 10);
    if (sId >= 1 && sId <= 114 && a >= 1 && a <= SURAHS[sId - 1].ayat) {
      return { surah: sId, ayah: a, ref: `${sId}:${a}` };
    }
  }

  // Pattern 6b: Bangla named surah: "সুরা বাকারা আয়াত ২৫৫", "সূরা বাকারা ২৫৫"
  const bnNlMatch = q.match(/^(?:সূরা|সুরা)?\s*([^\d]+?)\s*(?:আয়াত|আয়াত|নং)?\s*(\d{1,3})$/);
  if (bnNlMatch) {
    const raw = bnNlMatch[1].trim();
    const a = parseInt(bnNlMatch[2], 10);
    const sId = /^\d+$/.test(raw) ? parseInt(raw, 10) : resolveSurahName(raw);
    if (sId && sId >= 1 && sId <= 114 && a >= 1 && a <= SURAHS[sId - 1].ayat) {
      return { surah: sId, ayah: a, ref: `${sId}:${a}` };
    }
  }

  // Pattern 7: Arabic natural language: "سورة البقرة اية 255", "البقرة 255"
  const arNlMatch = q.match(/^(?:سورة|سوره)?\s*([^\d]+?)\s*(?:اية|آية)?\s*(\d{1,3})$/);
  if (arNlMatch) {
    const raw = arNlMatch[1].trim();
    const a = parseInt(arNlMatch[2], 10);
    const sId = resolveSurahName(raw);
    if (sId && sId >= 1 && sId <= 114 && a >= 1 && a <= SURAHS[sId - 1].ayat) {
      return { surah: sId, ayah: a, ref: `${sId}:${a}` };
    }
  }

  // Pattern 8: Generic named surah + ayah number: "al-baqarah 255", "বাকারা ২৫৫", "البقرة ٢٥٥"
  const nameMatch = q.match(/^(.+?)[:\s]+(\d{1,3})$/);
  if (nameMatch) {
    const rawName = nameMatch[1].trim();
    const a = parseInt(nameMatch[2], 10);
    const sId = resolveSurahName(rawName);

    if (sId && sId >= 1 && sId <= 114) {
      const maxA = SURAHS[sId - 1].ayat;
      if (a >= 1 && a <= maxA) {
        return { surah: sId, ayah: a, ref: `${sId}:${a}` };
      }
    }
  }

  return null;
}
