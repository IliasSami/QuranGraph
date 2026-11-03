"""Normalize entity and theme names in explanation JSON files against the curated Knowledge Base.
Preserves indentation, claims, and all other text verbatim.
"""
import glob
import json
import os

NORMALIZATIONS = {
    "events": {
        "the Day of Judgement": "Day of Judgement",
        "Day of Judgment": "Day of Judgement",
        "the Day of Judgment": "Day of Judgement",
        "the Day of Resurrection": "Day of Resurrection",
        "the Resurrection": "Day of Resurrection",
        "resurrection": "Day of Resurrection",
        "the resurrection": "Day of Resurrection",
        "the Day of Recompense": "Day of Recompense",
        "the Year of the Elephant": "Year of the Elephant",
        "the conquest of Makkah": "Conquest of Makkah",
        "conquest of Makkah": "Conquest of Makkah",
        "blowing of the Trumpet": "blowing of the Horn",
        "the blowing of the Horn": "blowing of the Horn",
        "the first revelation": "first revelation",
        "the drowning of Pharaoh": "drowning of Pharaoh",
    },
    "names_of_allah": {
        "Rabb": "Ar-Rabb",
        "Malik": "Al-Malik",
    },
    "people": {
        "Muhammad ﷺ": "Prophet Muhammad ﷺ",
        "the Prophet ﷺ": "Prophet Muhammad ﷺ",
        "Prophet Muhammad": "Prophet Muhammad ﷺ",
        "Abu Bakr": "Abu Bakr as-Siddiq",
        "Umar ibn al-Khattab": "'Umar ibn al-Khattab",
        "Ibn Abbas": "Ibn 'Abbas",
        "Hasan al-Basri": "al-Hasan al-Basri",
    },
    "things": {
        "Quran": "the Quran",
        "Torah": "the Torah",
        "Gospel": "the Gospel",
        "earth": "the earth",
        "sky": "the sky",
        "sun": "the sun",
        "moon": "the moon",
        "night": "the night",
        "day": "the day",
        "stars": "the stars",
        "mountains": "the mountains",
    },
    "unseen": {
        "soul": "the soul",
    }
}


def normalize_all():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pattern = os.path.join(base_dir, "content", "explain", "*", "*.json")
    files = sorted(glob.glob(pattern))

    modified = 0
    for path in files:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        ents = data.get("entities", {})
        file_changed = False

        for cat, mapping in NORMALIZATIONS.items():
            if cat in ents and isinstance(ents[cat], list):
                new_list = []
                for item in ents[cat]:
                    canonical = mapping.get(item, item)
                    if canonical != item:
                        file_changed = True
                    if canonical not in new_list:
                        new_list.append(canonical)
                ents[cat] = new_list

        if file_changed:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write("\n")
            modified += 1

    print(f"Normalized {modified} files out of {len(files)} total explanations.")


if __name__ == "__main__":
    normalize_all()
