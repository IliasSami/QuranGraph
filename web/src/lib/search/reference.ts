import surahsData from "./surahs.json" with { type: "json" };
import { arabicKey, asciiDigits, banglaKey, latinFold } from "./normalize.ts";

export interface AyahReference {
  surah: number;
  ayah: number;
  ref: string; // "2:255"
}

interface SurahInfo {
  id: number;
  name_ar: string;
  name_translit: string;
  name_en: string;
  name_bn: string;
  ayat: number;
}

const SURAHS: SurahInfo[] = surahsData;

function cleanName(s: string): string {
  return latinFold(s)
    .replace(/^(surah|sura|chapter)\s+/i, "")
    .replace(/^(al|el|ar|as|at|ad|an|ash|az)[-\s]/i, "")
    .replace(/[^a-z0-9]/g, "");
}

function cleanAr(s: string): string {
  let k = arabicKey(s);
  if (k.startsWith("ال")) k = k.slice(2);
  return k;
}

function cleanBn(s: string): string {
  let k = banglaKey(s);
  if (k.startsWith("আল") || k.startsWith("আর") || k.startsWith("আন") || k.startsWith("আশ")) {
    k = k.replace(/^(আল|আর|আন|আশ)[-_\s]*/, "");
  }
  return k.replace(/[-_\s]/g, "");
}

// Build fast lookup table
const nameToSurah = new Map<string, number>();

for (const s of SURAHS) {
  nameToSurah.set(String(s.id), s.id);
  nameToSurah.set(cleanName(s.name_translit), s.id);
  nameToSurah.set(cleanName(s.name_en), s.id);
  nameToSurah.set(cleanAr(s.name_ar), s.id);
  nameToSurah.set(cleanBn(s.name_bn), s.id);

  // Common aliases
  if (s.id === 1) {
    nameToSurah.set("fatiha", 1);
    nameToSurah.set("fatihah", 1);
  } else if (s.id === 2) {
    nameToSurah.set("baqara", 2);
    nameToSurah.set("baqarah", 2);
    nameToSurah.set("বাকারা", 2);
  } else if (s.id === 9) {
    nameToSurah.set("tawbah", 9);
    nameToSurah.set("tawba", 9);
    nameToSurah.set("baraat", 9);
  } else if (s.id === 36) {
    nameToSurah.set("yasin", 36);
    nameToSurah.set("yaseen", 36);
  } else if (s.id === 55) {
    nameToSurah.set("rahman", 55);
  } else if (s.id === 67) {
    nameToSurah.set("mulk", 67);
  } else if (s.id === 112) {
    nameToSurah.set("ikhlas", 112);
  }
}

/**
 * Parses queries like "2:255", "al-baqarah 255", "বাকারা ২৫৫", "البقرة ٢٥٥"
 * into a structured AyahReference or null.
 */
export function parseReference(query: string): AyahReference | null {
  const q = asciiDigits(query.trim()).normalize("NFC");

  // Pattern 1: Pure digits "2:255" or "2 255"
  const colonMatch = q.match(/^(\d{1,3})[:\s]+(\d{1,3})$/);
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

  // Pattern 2: Named surah + ayah number, e.g. "al-baqarah 255", "বাকারা ২৫৫", "البقرة ٢٥٥"
  const nameMatch = q.match(/^(.+?)[:\s]+(\d{1,3})$/);
  if (nameMatch) {
    const rawName = nameMatch[1].trim();
    const a = parseInt(nameMatch[2], 10);

    const sId =
      nameToSurah.get(cleanName(rawName)) ||
      nameToSurah.get(cleanAr(rawName)) ||
      nameToSurah.get(cleanBn(rawName));

    if (sId && sId >= 1 && sId <= 114) {
      const maxA = SURAHS[sId - 1].ayat;
      if (a >= 1 && a <= maxA) {
        return { surah: sId, ayah: a, ref: `${sId}:${a}` };
      }
    }
  }

  return null;
}
