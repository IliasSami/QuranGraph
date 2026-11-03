"""Rule-based Latin transliteration from vocalised Arabic (Tanzil Uthmani).

Standard scholarly Latin transliteration (ALA-LC / DMG style):
- Consonants: ' b t th j ḥ kh d dh r z s sh ṣ ḍ ṭ ẓ ‘ gh f q k l m n h w y
- Long vowels: ā, ī, ū
- Short vowels: a, i, u, with nunation: an, in, un
- Gemination: shadda doubles the consonant
- Sun letter assimilation for the definite article: ar-raḥmān, ash-shams
"""
import re

AR_CONSONANTS = {
    "\u0621": "'",       # ء hamza
    "\u0623": "'",       # أ alif with hamza above
    "\u0625": "'",       # إ alif with hamza below
    "\u0624": "'",       # ؤ waw with hamza above
    "\u0626": "'",       # ئ ya with hamza above
    "\u0628": "b",       # ب
    "\u062a": "t",       # ت
    "\u062b": "th",      # ث
    "\u062c": "j",       # ج
    "\u062d": "ḥ",       # ح
    "\u062e": "kh",      # خ
    "\u062f": "d",       # د
    "\u0630": "dh",      # ذ
    "\u0631": "r",       # ر
    "\u0632": "z",       # ز
    "\u0633": "s",       # س
    "\u0634": "sh",      # ش
    "\u0635": "ṣ",       # ص
    "\u0636": "ḍ",       # ض
    "\u0637": "ṭ",       # ط
    "\u0638": "ẓ",       # ظ
    "\u0639": "‘",       # ع 'ayn
    "\u063a": "gh",      # غ
    "\u0641": "f",       # ف
    "\u0642": "q",       # ق
    "\u0643": "k",       # ك
    "\u0644": "l",       # ل
    "\u0645": "m",       # م
    "\u0646": "n",       # ن
    "\u0647": "h",       # ه
    "\u0648": "w",       # و
    "\u064a": "y",       # ي
}

# Sun letters (huruf shamsiyyah)
SUN_LETTERS = {
    "\u062a": "t", "\u062b": "th", "\u062f": "d", "\u0630": "dh", "\u0631": "r",
    "\u0632": "z", "\u0633": "s", "\u0634": "sh", "\u0635": "ṣ", "\u0636": "ḍ",
    "\u0637": "ṭ", "\u0638": "ẓ", "\u0644": "l", "\u0646": "n",
}

# Quranic recitation marks and zero-width characters to strip
QURANIC_MARKS = set("\u06d6\u06d7\u06d8\u06d9\u06da\u06db\u06dc\u06df\u06e0\u06e2\u06e3\u06e5\u06e6\u06e8\u06ea\u06eb\u06ec\u06ed\u200c\u200d\u200e\u200f")


def clean_arabic(text: str) -> str:
    """Remove decorative Quranic pause marks, sajda markers, and normalize spaces."""
    res = "".join(c for c in text if c not in QURANIC_MARKS)
    return re.sub(r"\s+", " ", res).strip()


def transliterate_word(word: str) -> str:
    """Transliterate a single fully vocalised Arabic word into standard Latin."""
    if not word:
        return ""

    word = clean_arabic(word)
    if not word:
        return ""

    # Special case: Allah with various prefixes
    # e.g., ٱللَّهِ, لِلَّهِ, بِٱللَّهِ, وَٱللَّهُ
    if "\u0644\u0644\u0651\u064e\u0670\u0647" in word or "\u0644\u0651\u064e\u0647" in word:
        last_harakah = word[-1]
        vowel_end = {"\u0650": "i", "\u064e": "a", "\u064f": "u"}.get(last_harakah, "")
        if word.startswith(("\u0671\u0644\u0644\u0651", "\u0627\u0644\u0644\u0651")):
            return f"Allāh{vowel_end}"
        if word.startswith("\u0644\u0650\u0644\u0651"):
            return f"lillāh{vowel_end}"
        if word.startswith("\u0628\u0650\u0671\u0644\u0644\u0651"):
            return f"bi-llāh{vowel_end}"
        if word.startswith("\u0648\u064e\u0671\u0644\u0644\u0651"):
            return f"wa-llāh{vowel_end}"
        if word.startswith("\u0641\u064e\u0671\u0644\u0644\u0651"):
            return f"fa-llāh{vowel_end}"

    chars = list(word)
    n = len(chars)
    out = []
    i = 0

    # Definite article handling at start of word:
    # ٱلْ or ٱل or الْ or ال
    if n >= 2 and chars[0] in ("\u0627", "\u0671") and chars[1] == "\u0644":
        if n >= 4 and chars[2] in SUN_LETTERS and chars[3] == "\u0651":
            sun_char = chars[2]
            sun_lat = SUN_LETTERS[sun_char]
            out.append(f"a{sun_lat}-{sun_lat}")
            i = 4  # skip alif, lam, sun_letter, shadda
        elif n >= 3 and chars[2] in SUN_LETTERS and chars[2] == "\u0644":
            out.append("al-")
            i = 2
        elif n >= 3 and chars[2] == "\u0652":  # sukun on lam -> moon letter
            out.append("al-")
            i = 3
        else:
            out.append("al-")
            i = 2

    # Hamzat wasl at word beginning without lam: e.g. ٱهْدِ -> ihdi
    elif chars[0] == "\u0671":
        out.append("i")
        i = 1

    while i < n:
        c = chars[i]

        # Tashkeel marks
        if c == "\u064e":       # Fatha
            # Look ahead for dagger alif or bare alif
            if i + 1 < n and chars[i + 1] == "\u0670":  # fatha + dagger alif
                out.append("ā")
                i += 2
                continue
            if i + 1 < n and chars[i + 1] == "\u0627":   # fatha + alif
                out.append("ā")
                i += 2
                continue
            if i + 1 < n and chars[i + 1] == "\u0649" and (i + 2 == n or chars[i + 2] not in ("\u064e", "\u064f", "\u0650")):  # alif maqsura
                out.append("ā")
                i += 2
                continue
            out.append("a")
            i += 1
            continue

        if c == "\u064f":       # Damma
            # Look ahead for waw of prolongation
            if i + 1 < n and chars[i + 1] == "\u0648" and (i + 2 == n or chars[i + 2] not in ("\u064e", "\u064f", "\u0650")):
                out.append("ū")
                i += 2
                # Check for silent alif after waw (waw al-jama'ah e.g. qālū)
                if i < n and chars[i] == "\u0627":
                    i += 1
                continue
            out.append("u")
            i += 1
            continue

        if c == "\u0650":       # Kasra
            # Look ahead for ya of prolongation
            if i + 1 < n and chars[i + 1] == "\u064a" and (i + 2 == n or chars[i + 2] not in ("\u064e", "\u064f", "\u0650")):
                out.append("ī")
                i += 2
                continue
            out.append("i")
            i += 1
            continue

        if c == "\u064b":       # Fathatan
            out.append("an")
            i += 1
            if i < n and chars[i] in ("\u0627", "\u0649"):
                i += 1
            continue

        if c == "\u064c":       # Dammatan
            out.append("un")
            i += 1
            continue

        if c == "\u064d":       # Kasratan
            out.append("in")
            i += 1
            continue

        if c == "\u0652":       # Sukun
            i += 1
            continue

        if c == "\u0651":       # Shadda (gemination of previous consonant)
            if out:
                prev = out[-1]
                if prev in ("th", "sh", "kh", "dh", "gh"):
                    out[-1] = prev[0] + prev
                elif len(prev) == 1 and prev.isalpha():
                    out.append(prev)
            i += 1
            continue

        if c == "\u0670":       # Dagger alif (without fatha)
            if out and out[-1] == "a":
                out[-1] = "ā"
            else:
                out.append("ā")
            i += 1
            continue

        if c == "\u0627":       # Bare alif
            if not out:
                out.append("a")
            elif out[-1] == "a":
                out[-1] = "ā"
            i += 1
            continue

        if c == "\u0649":       # Alif maqsura
            if out and out[-1] == "a":
                out[-1] = "ā"
            else:
                out.append("ā")
            i += 1
            continue

        if c == "\u0629":       # Ta marbuta
            has_vowel = (i + 1 < n and chars[i + 1] in ("\u064e", "\u064f", "\u0650", "\u064b", "\u064c", "\u064d"))
            out.append("t" if has_vowel else "h")
            i += 1
            continue

        # Regular consonants
        mapped = AR_CONSONANTS.get(c, "")
        out.append(mapped)
        i += 1

    return "".join(out)


def transliterate(text: str) -> str:
    """Transliterate a full Arabic sentence or ayah into Latin script."""
    words = clean_arabic(text).split()
    return " ".join(transliterate_word(w) for w in words)
