// Bridge for the Python pipeline: reads a JSON array of strings on stdin, writes a JSON array of token lists
// ([[term, surface, script, stop, skeleton], ...] per input) to stdout.
// Pure ECMAScript implementation runnable on ANY Node.js version (18, 20, 22, 24+) without compilation or flags.

const ARABIC_LETTER = /[ؠ-يٮ-ۓەۺ-ۿݐ-ݿﭐ-﷿ﹰ-﻿]/;
const BANGLA_LETTER = /[ঀ-৿]/;

function scriptOf(token) {
  if (ARABIC_LETTER.test(token)) return "arabic";
  if (BANGLA_LETTER.test(token)) return "bangla";
  return "latin";
}

function asciiDigits(s) {
  return s
    .replace(/[٠-٩]/g, (d) => String(d.charCodeAt(0) - 0x0660))
    .replace(/[۰-۹]/g, (d) => String(d.charCodeAt(0) - 0x06F0))
    .replace(/[০-৯]/g, (d) => String(d.charCodeAt(0) - 0x09E6));
}

function arabicKey(s) {
  return s
    .normalize("NFC")
    .replace(/ٰ/g, "ا")
    .replace(/[ۥ]/g, "و")
    .replace(/[ۦ]/g, "ي")
    .replace(/[ً-ٟۖ-ۭـ࣓-ࣿ]/g, "")
    .replace(/[آأإٱٲٳ]/g, "ا")
    .replace(/ؤ/g, "و")
    .replace(/ئ/g, "ي")
    .replace(/ة/g, "ه")
    .replace(/[ىی]/g, "ي")
    .replace(/ک/g, "ك")
    .replace(/[^ء-ي]/g, "");
}

function arabicSkeleton(key) {
  return key.length > 3 ? key[0] + key.slice(1, -1).replace(/ا/g, "") + key[key.length - 1] : key;
}

function banglaKey(s) {
  return s
    .normalize("NFC")
    .replace(/ড়/g, "ড়").replace(/ঢ়/g, "ঢ়").replace(/য়/g, "য়")
    .replace(/[‌‍]/g, "")
    .replace(/ৎ/g, "ত")
    .replace(/ঁ/g, "")
    .replace(/ঈ/g, "ই").replace(/ঊ/g, "উ")
    .replace(/ী/g, "ি").replace(/ূ/g, "ু")
    .replace(/[^ঀ-৿]/g, "")
    .replace(/্+$/, "");
}

const BN_SUFFIXES = ["গুলোকে", "গুলোর", "দেরকে", "গুলো", "গুলি", "দের", "দিগকে", "েরা", "য়ের", "ের", "কে", "রা", "টি", "টা", "খানা", "তে", "য়", "র", "ে"];

function banglaStem(key) {
  let k = key;
  for (const suf of BN_SUFFIXES) {
    if (k.endsWith(suf) && [...k].length - [...suf].length >= 2) {
      k = k.slice(0, k.length - suf.length);
      break;
    }
  }
  return k.replace(/্+$/, "");
}

function latinFold(s) {
  return s.normalize("NFD").replace(/\p{Mn}/gu, "").replace(/[ʿʾ‘’'`]/g, "").toLowerCase();
}

function stem(w) {
  if (w.length <= 4) return w;
  if (w.endsWith("ies") && w.length > 5) return w.slice(0, -3) + "y";
  if (w.endsWith("ing") && w.length > 6) return w.slice(0, -3);
  if (w.endsWith("ed") && w.length > 5) return w.slice(0, -2);
  if (w.endsWith("es") && /(ss|x|ch|sh)es$/.test(w)) return w.slice(0, -2);
  if (w.endsWith("s") && !/(ss|us|is)$/.test(w)) return w.slice(0, -1);
  return w;
}

const STOPWORDS = new Set(
  ("a an and are as at be been but by can did do does for from had has have he her him his how i if in into is it its me my " +
    "no not of on or our she so that the their them then there these they this those to us was we were what when where which " +
    "who whom why will with you your thou thee thy ye unto shall verse verses ayah ayat surah sura surahs chapter chapters " +
    "say says said tell tells tellme about find show search meaning mean means").split(" ")
);
const BN_STOP = new Set(["ও", "এবং", "যে", "এই", "সে", "তার", "তা", "কি", "কী", "না", "হয়", "করে", "থেকে", "জন্য", "আর", "এর", "একটি", "সূরা", "সুরা", "আয়াত", "আয়াত", "পারা", "সম্পর্কে", "বলা", "কোথায়", "কোথায়"].map(banglaKey));
const AR_STOP = new Set(["في", "من", "علي", "الي", "ان", "عن", "ما", "لا", "و", "ثم", "او", "ذلك", "هذا", "التي", "الذي", "الذين"]);

function tokenize(text) {
  const out = [];
  const s = asciiDigits(text.normalize("NFC"));
  for (const m of s.matchAll(/[\p{L}\p{M}\p{N}‌‍'’ʿʾ]+/gu)) {
    const surface = m[0];
    const script = scriptOf(surface);
    let term;
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

let input = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", (c) => (input += c));
process.stdin.on("end", () => {
  const texts = JSON.parse(input);
  const out = texts.map((t) =>
    tokenize(t).map((k) => [
      k.term,
      k.surface,
      k.script,
      k.stop ? 1 : 0,
      k.script === "arabic" ? arabicSkeleton(k.term) : k.term
    ])
  );
  process.stdout.write(JSON.stringify(out));
});
