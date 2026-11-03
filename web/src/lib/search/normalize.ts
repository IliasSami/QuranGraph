// Text analysis shared by the index builder, the in-browser search engine AND the Python pipeline
// (ingest/core/normalize.py calls this file through Node), so documents and queries are always analysed
// identically. One implementation, no Python/TypeScript drift.
//
// Scripts: Arabic (Quranic Uthmani or simple), Bangla, Latin (English + transliteration).

export type Script = "arabic" | "bangla" | "latin";

const ARABIC_LETTER = /[ؠ-يٮ-ۓەۺ-ۿݐ-ݿﭐ-﷿ﹰ-﻿]/;
const BANGLA_LETTER = /[ঀ-৿]/;

export function scriptOf(token: string): Script {
  if (ARABIC_LETTER.test(token)) return "arabic";
  if (BANGLA_LETTER.test(token)) return "bangla";
  return "latin";
}

/** Arabic-Indic, Persian and Bangla digits -> 0-9 ("২:২৫৫", "٢:٢٥٥" work like "2:255"). */
export function asciiDigits(s: string): string {
  return s
    .replace(/[٠-٩]/g, (d) => String(d.charCodeAt(0) - 0x0660))
    .replace(/[۰-۹]/g, (d) => String(d.charCodeAt(0) - 0x06F0))
    .replace(/[০-৯]/g, (d) => String(d.charCodeAt(0) - 0x09E6));
}

// ------------------------------------------------------------------------------------------------- Arabic
/**
 * Arabic search key. Works the same on Uthmani (Tanzil/KFGQPC) and simple text:
 * drops harakat, tanwin, shadda, sukun, Quranic annotation marks (small high letters, pause marks, rub/sajda signs),
 * tatweel; superscript (dagger) alif -> alif; small waw/ya -> waw/ya; alef wasla and hamza seats -> bare letters;
 * ta marbuta -> ha; alif maqsura -> ya. Keeps the consonantal skeleton, which is what people type.
 */
export function arabicKey(s: string): string {
  return s
    .normalize("NFC")
    .replace(/ٰ/g, "ا")                 // dagger alif -> alif (رَحْمَٰن -> رحمان ... see below)
    .replace(/[ۥ]/g, "و")               // small waw
    .replace(/[ۦ]/g, "ي")               // small ya
    .replace(/[ً-ٟۖ-ۭـ࣓-ࣿ]/g, "")  // marks, tatweel
    .replace(/[آأإٱٲٳ]/g, "ا")     // آ أ إ ٱ -> ا
    .replace(/ؤ/g, "و")                 // ؤ -> و
    .replace(/ئ/g, "ي")                 // ئ -> ي
    .replace(/ة/g, "ه")                 // ة -> ه
    .replace(/[ىی]/g, "ي")         // ى ی -> ي
    .replace(/ک/g, "ك")                 // ک -> ك
    .replace(/[^ء-ي]/g, "");
}

/** The same word with and without the dagger-alif letter: Uthmani "رحمٰن" and simple "رحمن" must meet. */
export function arabicSkeleton(key: string): string {
  // long-a written as a full alif in simple spelling but as a dagger alif in Uthmani: drop medial alifs
  return key.length > 3 ? key[0] + key.slice(1, -1).replace(/ا/g, "") + key[key.length - 1] : key;
}

/** Common attached prefixes: و ف ب ك ل (+ ال), and لل. Returns the stripped forms (longest first). */
export function arabicVariants(key: string): string[] {
  const out = new Set<string>();
  let w = key;
  for (let i = 0; i < 2 && w.length > 3 && /^[وف]/.test(w); i++) { w = w.slice(1); out.add(w); }
  for (const p of ["بال", "كال", "فال", "وال", "لل", "ال", "ب", "ك", "ل", "س"]) {
    if (w.startsWith(p) && w.length - p.length >= 2) out.add(w.slice(p.length));
  }
  out.delete(key);
  return [...out].sort((a, b) => b.length - a.length);
}

// ------------------------------------------------------------------------------------------------- Bangla
/**
 * Bangla search key: NFC, nukta/precomposed letters unified (ড় ঢ় য়), ZWJ/ZWNJ and hasanta-joiners removed,
 * khanda ta -> ta, chandrabindu dropped, vowel-length folded (ই/ঈ, উ/ঊ and their signs), common spelling
 * variants of Islamic loanwords unified (ঈ/ই, শ/স/ষ only at search time via banglaPhonetic).
 */
export function banglaKey(s: string): string {
  return s
    .normalize("NFC")
    .replace(/ড়/g, "ড়").replace(/ঢ়/g, "ঢ়").replace(/য়/g, "য়")
    .replace(/[‌‍]/g, "")
    .replace(/ৎ/g, "ত")                 // ৎ -> ত
    .replace(/ঁ/g, "")                       // chandrabindu
    .replace(/ঈ/g, "ই").replace(/ঊ/g, "উ")       // ঈ -> ই, ঊ -> উ
    .replace(/ী/g, "ি").replace(/ূ/g, "ু")       // ী -> ি, ূ -> ু
    .replace(/[^ঀ-৿]/g, "")
    .replace(/্+$/, "");
}

const BN_SUFFIXES = ["গুলোকে", "গুলোর", "দেরকে", "গুলো", "গুলি", "দের", "দিগকে", "েরা", "য়ের", "ের", "কে", "রা", "টি", "টা", "খানা", "তে", "য়", "র", "ে"];

/** Light Bangla stemmer: removes one inflectional suffix (case/plural/classifier) when a stem of 2+ letters remains. */
export function banglaStem(key: string): string {
  let k = key;
  for (const suf of BN_SUFFIXES) {
    if (k.endsWith(suf) && [...k].length - [...suf].length >= 2) { k = k.slice(0, k.length - suf.length); break; }
  }
  return k.replace(/্+$/, "");   // "আল্লাহ্" = "আল্লাহ"
}

/** Bangla written phonetically -> a rough Latin sound key, so "রহমান", "রাহমান", "rahman" meet. */
const BN_LATIN: Record<string, string> = {
  "অ": "a", "আ": "a", "ই": "i", "উ": "u", "ঋ": "ri", "এ": "e", "ঐ": "oi", "ও": "o", "ঔ": "ou",
  "া": "a", "ি": "i", "ু": "u", "ৃ": "ri", "ে": "e", "ৈ": "oi", "ো": "o", "ৌ": "ou",
  "ক": "k", "খ": "kh", "গ": "g", "ঘ": "gh", "ঙ": "ng", "চ": "ch", "ছ": "ch", "জ": "j", "ঝ": "jh", "ঞ": "n",
  "ট": "t", "ঠ": "th", "ড": "d", "ঢ": "dh", "ণ": "n", "ত": "t", "থ": "th", "দ": "d", "ধ": "dh", "ন": "n",
  "প": "p", "ফ": "f", "ব": "b", "ভ": "bh", "ম": "m", "য": "j", "র": "r", "ল": "l", "শ": "sh", "ষ": "sh", "স": "s",
  "হ": "h", "ড়": "r", "ঢ়": "rh", "য়": "y", "ং": "ng", "ঃ": "h", "্": "",
};
const BN_CONSONANT = /[ক-হড়ঢ়য়]/;
export function banglaToLatin(key: string): string {
  const cs = [...key];
  let out = "";
  cs.forEach((ch, i) => {
    out += BN_LATIN[ch] ?? "";
    // inherent vowel: a consonant followed directly by another consonant (no vowel sign, no hasanta) is spoken with "a"
    if (BN_CONSONANT.test(ch) && i + 1 < cs.length && BN_CONSONANT.test(cs[i + 1])) out += "a";
  });
  return out;
}

// ------------------------------------------------------------------------------------------------- Latin
export function latinFold(s: string): string {
  return s.normalize("NFD").replace(/\p{Mn}/gu, "").replace(/[ʿʾ‘’'`]/g, "").toLowerCase();
}

/**
 * Sound-alike key for transliterated Arabic in Latin script: "Ar-Raḥmān", "rahmaan", "rehman", "al rahman" -> "rhmn"-like
 * skeleton with stable vowels. Used for names, Arabic words and Bangla phonetic spellings (via banglaToLatin).
 */
export function translitKey(s: string): string {
  let k = latinFold(s).replace(/[^a-z]/g, "");
  k = k.replace(/^(al|el|ar|as|at|ad|an|ash|az|ul)(?=[a-z]{3})/, "");     // article: al-, ar-, as- ...
  for (const [a, b] of [["sch", "sh"], ["kh", "h"], ["gh", "g"], ["ch", "h"], ["th", "s"], ["dh", "z"], ["ph", "f"],
    ["ee", "i"], ["oo", "u"], ["ou", "u"], ["aa", "a"], ["q", "k"], ["c", "k"], ["w", "v"], ["y", "i"], ["e", "a"], ["o", "u"]] as const) {
    k = k.split(a).join(b);
  }
  k = k.replace(/(.)\1+/g, "$1").replace(/h$/, "");
  return k;
}

/**
 * Consonant skeleton of a sound key: "rahman" / "rahaman" -> "rhmn". Bangla script drops or keeps inherent vowels
 * unpredictably, so Bangla-phonetic queries are matched to Latin/Arabic names on consonants (first vowel kept).
 */
export function consonantKey(s: string): string {
  const k = translitKey(s);
  return k.slice(0, 1) + k.slice(1).replace(/[aiu]/g, "");
}

/** Light English stemmer (plural / -ing / -ed), enough for "prophets" = "prophet", "believing" ~ "believe". */
export function stem(w: string): string {
  if (w.length <= 4) return w;
  if (w.endsWith("ies") && w.length > 5) return w.slice(0, -3) + "y";
  if (w.endsWith("ing") && w.length > 6) return w.slice(0, -3);
  if (w.endsWith("ed") && w.length > 5) return w.slice(0, -2);
  if (w.endsWith("es") && /(ss|x|ch|sh)es$/.test(w)) return w.slice(0, -2);
  if (w.endsWith("s") && !/(ss|us|is)$/.test(w)) return w.slice(0, -1);
  return w;
}

export const STOPWORDS = new Set(
  ("a an and are as at be been but by can did do does for from had has have he her him his how i if in into is it its me my " +
    "no not of on or our she so that the their them then there these they this those to us was we were what when where which " +
    "who whom why will with you your thou thee thy ye unto shall verse ayah ayat surah sura meaning mean means").split(" "),
);
const BN_STOP = new Set(["ও", "এবং", "যে", "এই", "সে", "তার", "তা", "কি", "কী", "না", "হয়", "করে", "থেকে", "জন্য", "আর", "এর", "একটি"].map(banglaKey));
const AR_STOP = new Set(["في", "من", "علي", "الي", "ان", "عن", "ما", "لا", "و", "ثم", "او", "ذلك", "هذا", "التي", "الذي", "الذين"]);

export interface Token { term: string; surface: string; script: Script; stop: boolean }

/** Tokenise any mix of Arabic, Bangla and Latin into normalised index terms. */
export function tokenize(text: string): Token[] {
  const out: Token[] = [];
  const s = asciiDigits(text.normalize("NFC"));
  for (const m of s.matchAll(/[\p{L}\p{M}\p{N}‌‍'’ʿʾ]+/gu)) {
    const surface = m[0];
    const script = scriptOf(surface);
    let term: string;
    let stop = false;
    if (script === "arabic") {
      term = arabicKey(surface);
      stop = AR_STOP.has(term);
    } else if (script === "bangla") {
      term = banglaStem(banglaKey(surface));
      stop = BN_STOP.has(banglaKey(surface));
    } else {
      const f = latinFold(surface).replace(/['’]/g, "");
      stop = STOPWORDS.has(f);
      term = /^\d+$/.test(f) ? f : stem(f);
    }
    if (term) out.push({ term, surface, script, stop });
  }
  return out;
}

/** Bounded Damerau-Levenshtein (adjacent transposition), returns maxD+1 early when over the bound. */
export function editDistance(a: string, b: string, maxD = 2): number {
  if (Math.abs(a.length - b.length) > maxD) return maxD + 1;
  const A = [...a], B = [...b];
  let prev2: number[] = [];
  let prev = Array.from({ length: B.length + 1 }, (_, j) => j);
  for (let i = 1; i <= A.length; i++) {
    const cur = [i];
    let best = i;
    for (let j = 1; j <= B.length; j++) {
      let v = Math.min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (A[i - 1] === B[j - 1] ? 0 : 1));
      if (i > 1 && j > 1 && A[i - 1] === B[j - 2] && A[i - 2] === B[j - 1]) v = Math.min(v, prev2[j - 2] + 1);
      cur.push(v);
      if (v < best) best = v;
    }
    if (best > maxD) return maxD + 1;
    prev2 = prev;
    prev = cur;
  }
  return prev[B.length];
}
