import corpusData from "./corpus.json" with { type: "json" };
import knowledgeData from "./knowledge.json" with { type: "json" };
import { parseReference } from "./reference.ts";
import {
  arabicKey,
  arabicSkeleton,
  banglaKey,
  banglaStem,
  editDistance,
  latinFold,
  scriptOf,
  tokenize,
  translitKey
} from "./normalize.ts";

export interface SearchResult {
  ref: string; // "surah:ayah"
  score: number;
  matchType: "reference" | "entity" | "arabic" | "phrase" | "concept" | "text";
  title?: string;
}

interface AyahRecord {
  s: number;
  a: number;
  ar: string;
  en: string;
  bn: string;
}

interface KnowledgeEntry {
  id: string;
  title_en: string;
  title_ar: string;
  title_bn: string;
  aliases: string[];
  ayat: string[];
}

const CORPUS: AyahRecord[] = corpusData;
const KNOWLEDGE: KnowledgeEntry[] = knowledgeData;

// Precompute normalised forms for knowledge entries
interface IndexedKnowledge {
  entry: KnowledgeEntry;
  latinAliases: string[];
  arabicAliases: string[];
  banglaAliases: string[];
  translitAliases: string[];
}

const INDEXED_KNOWLEDGE: IndexedKnowledge[] = KNOWLEDGE.map((entry) => {
  const latinAliases: string[] = [];
  const arabicAliases: string[] = [];
  const banglaAliases: string[] = [];
  const translitAliases: string[] = [];

  for (const a of entry.aliases) {
    const sc = scriptOf(a);
    if (sc === "arabic") {
      arabicAliases.push(arabicKey(a));
    } else if (sc === "bangla") {
      banglaAliases.push(banglaKey(a));
      banglaAliases.push(banglaStem(banglaKey(a)));
    } else {
      latinAliases.push(latinFold(a));
      translitAliases.push(translitKey(a));
    }
  }

  return {
    entry,
    latinAliases,
    arabicAliases,
    banglaAliases,
    translitAliases
  };
});

// Precompute corpus search keys
const CORPUS_KEYS = CORPUS.map((rec) => ({
  ref: `${rec.s}:${rec.a}`,
  arKey: arabicKey(rec.ar),
  arSkel: arabicSkeleton(arabicKey(rec.ar)),
  enLower: rec.en.toLowerCase(),
  enFold: latinFold(rec.en),
  bnKey: banglaKey(rec.bn),
  bnStemmed: banglaStem(banglaKey(rec.bn))
}));

/**
 * Searches the Quran by reference, entity, concept, Arabic text, English/Bangla translations, or transliteration.
 */
export function search(rawQuery: string, limit = 10): SearchResult[] {
  const query = rawQuery.trim();
  if (!query) return [];

  // Channel 1: Reference Parser ("2:255", "al-baqarah 255", "বাকারা ২৫৫", "البقرة ٢٥٥")
  const refMatch = parseReference(query);
  if (refMatch) {
    return [
      {
        ref: refMatch.ref,
        score: 1000,
        matchType: "reference"
      }
    ];
  }

  const scores = new Map<string, { score: number; matchType: SearchResult["matchType"]; title?: string }>();
  const addScore = (ref: string, points: number, type: SearchResult["matchType"], title?: string) => {
    const existing = scores.get(ref);
    if (!existing || points > existing.score) {
      scores.set(ref, { score: points, matchType: type, title: title || existing?.title });
    } else if (existing) {
      existing.score += points * 0.2; // cumulative boost
    }
  };

  const qScript = scriptOf(query);
  const qLatin = latinFold(query);
  const qTranslit = translitKey(query);
  const qArabic = arabicKey(query);
  const qArabicSkel = arabicSkeleton(qArabic);
  const qBangla = banglaKey(query);
  const qBanglaStem = banglaStem(qBangla);

  // Channel 2: Curated Knowledge & Named Passages & Concepts
  for (const ik of INDEXED_KNOWLEDGE) {
    let matched = false;
    let rankScore = 0;

    if (qScript === "arabic") {
      for (const al of ik.arabicAliases) {
        if (qArabic === al || qArabic.includes(al) || al.includes(qArabic)) {
          matched = true;
          rankScore = 800;
          break;
        }
      }
    } else if (qScript === "bangla") {
      for (const al of ik.banglaAliases) {
        if (qBangla === al || qBanglaStem === al || qBangla.includes(al) || al.includes(qBangla)) {
          matched = true;
          rankScore = 800;
          break;
        }
      }
    } else {
      // Latin / English / Transliteration
      for (const al of ik.latinAliases) {
        if (qLatin === al || (al.length >= 4 && qLatin.includes(al)) || (qLatin.length >= 4 && al.includes(qLatin))) {
          matched = true;
          rankScore = 800;
          break;
        }
      }
      if (!matched && qTranslit.length >= 3) {
        for (const al of ik.translitAliases) {
          if (qTranslit === al || editDistance(qTranslit, al, 1) <= 1) {
            matched = true;
            rankScore = 750;
            break;
          }
        }
      }
    }

    if (matched) {
      // Add ayat in knowledge order, decaying slightly for lower ranked ayat
      ik.entry.ayat.forEach((ayahRef, idx) => {
        const decay = Math.max(10, 50 - idx * 10);
        addScore(ayahRef, rankScore + decay, "concept", ik.entry.title_en);
      });
    }
  }

  // Channel 3: Corpus Text Search (Arabic, English, Bangla)
  const tokens = tokenize(query).filter((t) => !t.stop);
  const qTerms = tokens.map((t) => t.term);

  for (let i = 0; i < CORPUS_KEYS.length; i++) {
    const ck = CORPUS_KEYS[i];
    let ayahScore = 0;
    let matchType: SearchResult["matchType"] = "text";

    if (qScript === "arabic") {
      if (qArabic.length >= 3) {
        if (ck.arKey.includes(qArabic)) {
          ayahScore = 500 + qArabic.length * 10;
          matchType = "arabic";
        } else if (qArabicSkel.length >= 3 && ck.arSkel.includes(qArabicSkel)) {
          ayahScore = 400 + qArabicSkel.length * 10;
          matchType = "arabic";
        }
      }
    } else if (qScript === "bangla") {
      // Bangla translation search
      if (qBangla.length >= 3 && ck.bnKey.includes(qBangla)) {
        ayahScore = 450 + qBangla.length * 5;
        matchType = "phrase";
      } else if (tokens.length > 0) {
        let matchCount = 0;
        for (const t of qTerms) {
          if (ck.bnStemmed.includes(t)) matchCount++;
        }
        if (matchCount > 0) {
          ayahScore = matchCount * 60;
        }
      }
    } else {
      // Latin script: English translation or transliteration
      // Check exact phrase in English
      if (qLatin.length >= 4 && ck.enFold.includes(qLatin)) {
        ayahScore = 450 + qLatin.length * 5;
        matchType = "phrase";
      } else if (tokens.length > 0) {
        let matchCount = 0;
        for (const t of qTerms) {
          if (ck.enFold.includes(t)) matchCount++;
        }
        if (matchCount > 0) {
          const ratio = matchCount / tokens.length;
          ayahScore = ratio * 150 + matchCount * 30;
        }
      }
    }

    if (ayahScore > 0) {
      addScore(ck.ref, ayahScore, matchType);
    }
  }

  // Sort by score descending
  const results: SearchResult[] = Array.from(scores.entries()).map(([ref, data]) => ({
    ref,
    score: Math.round(data.score),
    matchType: data.matchType,
    title: data.title
  }));

  results.sort((a, b) => b.score - a.score);
  return results.slice(0, limit);
}
