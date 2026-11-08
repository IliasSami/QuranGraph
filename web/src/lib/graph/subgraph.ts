import entitiesData from "../../../../ingest/work/export/graph/entities.json" with { type: "json" };
import storiesData from "../../../../ingest/work/export/graph/stories.json" with { type: "json" };
import rootsData from "../../../../ingest/work/export/graph/roots.json" with { type: "json" };
import themesData from "../../../../ingest/work/export/graph/themes.json" with { type: "json" };
import similarData from "../../../../ingest/work/export/graph/similar_ayat.json" with { type: "json" };
import corpusData from "../search/corpus.json" with { type: "json" };
import surahsData from "../search/surahs.json" with { type: "json" };

export interface GraphNode {
  id: string;
  label: string;
  label_ar?: string;
  label_bn?: string;
  sublabel?: string;
  type:
    | "ayah"
    | "name_of_allah"
    | "person"
    | "place"
    | "nation"
    | "unseen"
    | "story"
    | "episode"
    | "root"
    | "theme"
    | "similar_ayah"
    | "glossary";
  category: string;
  color: string;
  radius: number;
  url: string;
  isCenter?: boolean;
  properties?: Record<string, any>;
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
}

export interface GraphEdge {
  source: string; // node id
  target: string; // node id
  type: string;
  label: string;
}

export interface StoryEpisode {
  id: string;
  title_en: string;
  title_bn?: string;
  ayat: string;
}

export interface StoryContext {
  storyId: string;
  slug: string;
  title_en: string;
  title_bn?: string;
  activeEpisodes: StoryEpisode[];
  allEpisodes: StoryEpisode[];
}

export interface ConnectedEntityItem {
  id: string;
  slug: string;
  type: string;
  label_en: string;
  label_ar?: string;
  label_bn?: string;
}

export interface ConnectedStoryItem {
  storyId: string;
  slug: string;
  title_en: string;
  title_bn?: string;
  episodes: StoryEpisode[];
}

export interface AyahSubgraph {
  ref: string;
  surahId: number;
  ayahNum: number;
  surahName: string;
  surahNameBn: string;
  arabicSnippet: string;
  englishSnippet: string;
  nodes: GraphNode[];
  edges: GraphEdge[];
  storyContext: StoryContext | null;
  connectedEntities: ConnectedEntityItem[];
  connectedStories: ConnectedStoryItem[];
}

export const NODE_PALETTE: Record<string, { color: string; label: string; icon: string }> = {
  ayah: { color: "#0f766e", label: "Verse", icon: "📖" },
  name_of_allah: { color: "#d97706", label: "Divine Name", icon: "✨" },
  person: { color: "#059669", label: "Prophet / Figure", icon: "👤" },
  place: { color: "#2563eb", label: "Sacred Place", icon: "📍" },
  nation: { color: "#7c3aed", label: "Nation / People", icon: "🏛️" },
  unseen: { color: "#8b5cf6", label: "Unseen Realm", icon: "🌌" },
  story: { color: "#f59e0b", label: "Story Arc", icon: "📜" },
  episode: { color: "#ea580c", label: "Story Episode", icon: "🎬" },
  root: { color: "#0891b2", label: "Arabic Root", icon: "🔤" },
  theme: { color: "#a855f7", label: "Quranic Theme", icon: "💡" },
  similar_ayah: { color: "#64748b", label: "Shared Lemma Verse", icon: "🔗" },
  glossary: { color: "#0284c7", label: "Theological Term", icon: "🏷️" }
};

// Sluggify entity id
export function entityIdToSlug(id: string): string {
  return id
    .replace(/[:\/]+/g, "-")
    .replace(/[^a-zA-Z0-9_\-\u0980-\u09FF\u0600-\u06FF]+/g, "-")
    .replace(/-+/g, "-")
    .replace(/^-|-$/g, "");
}

// Fast lookups built once at module initialization
export const corpusMap = new Map<string, any>();
for (const c of corpusData) {
  corpusMap.set(`${c.s}:${c.a}`, c);
}

export const surahMap = new Map<number, any>();
for (const s of surahsData) {
  surahMap.set(s.id, s);
}

// Inverted entity index by ayah ref
const entitiesByAyah = new Map<string, Array<{ eid: string; ent: any; slug: string; type: string; palette: any }>>();
for (const [eid, ent] of Object.entries(entitiesData as Record<string, any>)) {
  const type = ent.type || "glossary";
  const slug = entityIdToSlug(eid);
  const palette = NODE_PALETTE[type] || NODE_PALETTE.glossary;
  const item = { eid, ent, slug, type, palette };
  for (const ref of (ent.ayat || [])) {
    let list = entitiesByAyah.get(ref);
    if (!list) {
      list = [];
      entitiesByAyah.set(ref, list);
    }
    list.push(item);
  }
}

// Inverted story index by surahId
interface IndexedStoryEpisode {
  story: any;
  storySlug: string;
  episode: StoryEpisode;
  surahId: number;
  start: number;
  end: number;
}
const episodesBySurah = new Map<number, IndexedStoryEpisode[]>();
for (const s of (storiesData as any[])) {
  const storySlug = s.id.replace("story-", "");
  for (const ep of (s.episodes || [])) {
    const [sPart, aPart] = (ep.ayat || "").split(":");
    const surahId = parseInt(sPart, 10);
    if (!surahId) continue;
    let start = 0, end = 0;
    if (aPart && aPart.includes("-")) {
      const [st, en] = aPart.split("-").map(Number);
      start = st;
      end = en;
    } else {
      start = parseInt(aPart, 10);
      end = start;
    }
    let list = episodesBySurah.get(surahId);
    if (!list) {
      list = [];
      episodesBySurah.set(surahId, list);
    }
    list.push({ story: s, storySlug, episode: ep, surahId, start, end });
  }
}

// Inverted roots index by ayah ref
const rootsByAyah = new Map<string, Array<{ root: string; data: any }>>();
for (const [rk, r] of Object.entries(rootsData as Record<string, any>)) {
  const item = { root: rk, data: r };
  for (const ref of (r.ayat || [])) {
    let list = rootsByAyah.get(ref);
    if (!list) {
      list = [];
      rootsByAyah.set(ref, list);
    }
    list.push(item);
  }
}
for (const [_, list] of rootsByAyah) {
  list.sort((a, b) => (a.data.occurrences || 9999) - (b.data.occurrences || 9999));
}

// Inverted themes index by ayah ref
const themesByAyah = new Map<string, Array<{ tid: string; theme: any }>>();
for (const [tid, t] of Object.entries(themesData as Record<string, any>)) {
  const item = { tid, theme: t };
  for (const ref of (t.ayat || [])) {
    let list = themesByAyah.get(ref);
    if (!list) {
      list = [];
      themesByAyah.set(ref, list);
    }
    list.push(item);
  }
}

/**
 * Extract an exact, contextual subgraph for a verse reference (e.g. "2:255" or "12:4")
 */
export function extractAyahSubgraph(ref: string, explanation?: any): AyahSubgraph {
  const parts = ref.split(":");
  const surahId = parseInt(parts[0], 10);
  const ayahNum = parseInt(parts[1], 10);

  const surah = surahMap.get(surahId) || { name_translit: `Surah ${surahId}`, name_bn: "" };
  const ayahRecord = corpusMap.get(ref) || { ar: "", en: "", bn: "" };

  const centerId = `ayah:${ref}`;
  const nodes: GraphNode[] = [];
  const edges: GraphEdge[] = [];
  const seenNodes = new Set<string>();

  function addNode(node: GraphNode) {
    if (!seenNodes.has(node.id)) {
      seenNodes.add(node.id);
      nodes.push(node);
    }
  }

  function addEdge(edge: GraphEdge) {
    edges.push(edge);
  }

  // 1. Center Verse Node
  addNode({
    id: centerId,
    label: `${surah.name_translit} ${ref}`,
    label_ar: ayahRecord.ar?.slice(0, 40) + (ayahRecord.ar?.length > 40 ? "..." : ""),
    label_bn: `${surah.name_bn} (${ref})`,
    sublabel: "Active Verse",
    type: "ayah",
    category: "center",
    color: "#0f766e",
    radius: 28,
    url: `/ayah/${surahId}/${ayahNum}`,
    isCenter: true,
    properties: {
      ref,
      surah: surah.name_translit,
      translation_en: ayahRecord.en,
      translation_bn: ayahRecord.bn
    }
  });

  // 2. Connected Entities (Divine Names, Prophets, Places, Nations, Unseen, Glossary) - O(1)
  const connectedEntities: ConnectedEntityItem[] = [];
  const verseEntities = entitiesByAyah.get(ref) || [];
  for (const { eid, ent, slug, type, palette } of verseEntities) {
    addNode({
      id: eid,
      label: ent.label_en || eid,
      label_ar: ent.label_ar || "",
      label_bn: ent.label_bn || "",
      sublabel: palette.label,
      type: type as any,
      category: type,
      color: palette.color,
      radius: type === "name_of_allah" ? 22 : type === "person" ? 20 : 18,
      url: `/entity/${slug}`,
      properties: ent.properties
    });

    addEdge({
      source: centerId,
      target: eid,
      type: `mentions_${type}`,
      label: palette.label
    });

    connectedEntities.push({
      id: eid,
      slug,
      type,
      label_en: ent.label_en || eid,
      label_ar: ent.label_ar,
      label_bn: ent.label_bn
    });
  }

  // 3. Story Narrative Arc & Episodes - Indexed by Surah
  let storyContext: StoryContext | null = null;
  const connectedStories: ConnectedStoryItem[] = [];
  const surahEpisodes = episodesBySurah.get(surahId) || [];

  const matchedByStory = new Map<string, { story: any; storySlug: string; episodes: StoryEpisode[] }>();
  for (const epItem of surahEpisodes) {
    if (ayahNum >= epItem.start && ayahNum <= epItem.end) {
      let group = matchedByStory.get(epItem.story.id);
      if (!group) {
        group = { story: epItem.story, storySlug: epItem.storySlug, episodes: [] };
        matchedByStory.set(epItem.story.id, group);
      }
      group.episodes.push(epItem.episode);
    }
  }

  for (const { story: s, storySlug, episodes: matchedEpisodes } of matchedByStory.values()) {
    const eps: StoryEpisode[] = s.episodes || [];
    connectedStories.push({
      storyId: s.id,
      slug: storySlug,
      title_en: s.title_en,
      title_bn: s.title_bn,
      episodes: matchedEpisodes
    });

    if (!storyContext) {
      storyContext = {
        storyId: s.id,
        slug: storySlug,
        title_en: s.title_en,
        title_bn: s.title_bn,
        activeEpisodes: matchedEpisodes,
        allEpisodes: eps
      };
    }

    // Add Story Arc Node
    addNode({
      id: s.id,
      label: s.title_en,
      label_bn: s.title_bn,
      sublabel: "Quranic Narrative Arc",
      type: "story",
      category: "story",
      color: NODE_PALETTE.story.color,
      radius: 24,
      url: `/story/${storySlug}`,
      properties: { episodes_count: eps.length }
    });

    addEdge({
      source: centerId,
      target: s.id,
      type: "in_story",
      label: "Story Arc"
    });

    // Add Active Episode Nodes
    for (const ep of matchedEpisodes) {
      const epNodeId = `episode:${ep.id}`;
      addNode({
        id: epNodeId,
        label: ep.title_en,
        label_bn: ep.title_bn,
        sublabel: `Active Episode (${ep.ayat})`,
        type: "episode",
        category: "episode",
        color: NODE_PALETTE.episode.color,
        radius: 19,
        url: `/story/${storySlug}`,
        properties: { ayat: ep.ayat }
      });

      addEdge({
        source: s.id,
        target: epNodeId,
        type: "has_episode",
        label: "Episode"
      });

      addEdge({
        source: centerId,
        target: epNodeId,
        type: "active_episode",
        label: "Current Scene"
      });
    }
  }

  // 4. Linguistic Roots (Pre-sorted by rarity) - O(1)
  const verseRoots = rootsByAyah.get(ref) || [];
  for (const item of verseRoots.slice(0, 5)) {
    const rootId = `root:${item.root}`;
    const occ = item.data.occurrences || 1;
    const rarityLabel = occ === 1 ? "1x in Quran (Hapax)" : `${occ}x in Quran`;

    addNode({
      id: rootId,
      label: item.root,
      label_ar: item.root,
      sublabel: rarityLabel,
      type: "root",
      category: "root",
      color: NODE_PALETTE.root.color,
      radius: 17,
      url: `/root/${encodeURIComponent(item.root)}`,
      properties: {
        occurrences: occ,
        lemmas: item.data.lemmas
      }
    });

    addEdge({
      source: centerId,
      target: rootId,
      type: "has_root",
      label: "Root"
    });
  }

  // 5. Quranic Themes - O(1)
  const verseThemes = themesByAyah.get(ref) || [];
  let themeCount = Math.min(verseThemes.length, 4);
  for (const { tid, theme: t } of verseThemes.slice(0, 4)) {
    addNode({
      id: tid,
      label: t.label_en || tid.replace("theme:", "").replace(/-/g, " "),
      sublabel: "Moral Theme",
      type: "theme",
      category: "theme",
      color: NODE_PALETTE.theme.color,
      radius: 16,
      url: `/search?q=${encodeURIComponent(t.label_en || tid)}`,
      properties: { ayat_count: t.ayat_count }
    });

    addEdge({
      source: centerId,
      target: tid,
      type: "teaches_theme",
      label: "Theme"
    });
  }

  // 6. Explanation metadata overlay (if available)
  if (explanation) {
    // If explanation has themes not yet added
    if (Array.isArray(explanation.themes)) {
      for (const tName of explanation.themes) {
        if (themeCount >= 5) break;
        const tid = `theme-exp:${tName.toLowerCase().replace(/\s+/g, "-")}`;
        if (!seenNodes.has(tid)) {
          addNode({
            id: tid,
            label: tName,
            sublabel: "Ayah Explanation Theme",
            type: "theme",
            category: "theme",
            color: NODE_PALETTE.theme.color,
            radius: 15,
            url: `/search?q=${encodeURIComponent(tName)}`
          });
          addEdge({
            source: centerId,
            target: tid,
            type: "teaches_theme",
            label: "Theme"
          });
          themeCount++;
        }
      }
    }
  }

  // 7. Similar Verses (Lexical & Lemma Overlap)
  const similarMap = similarData as Record<string, any[]>;
  const similarVerses = similarMap[ref] || [];
  for (const sim of similarVerses.slice(0, 3)) {
    const simRef = sim.ayah;
    const [sPart, aPart] = simRef.split(":");
    const simS = parseInt(sPart, 10);
    const simSurah = surahMap.get(simS);
    const simNodeId = `ayah:${simRef}`;
    const overlapPct = Math.round((sim.score || 0) * 100);

    addNode({
      id: simNodeId,
      label: `${simSurah ? simSurah.name_translit : `Surah ${simS}`} ${simRef}`,
      sublabel: `${overlapPct}% shared lemmas (${(sim.shared_lemmas || []).slice(0, 2).join(", ")})`,
      type: "similar_ayah",
      category: "similar_ayah",
      color: NODE_PALETTE.similar_ayah.color,
      radius: 17,
      url: `/ayah/${sPart}/${aPart}`,
      properties: {
        score: sim.score,
        shared_lemmas: sim.shared_lemmas
      }
    });

    addEdge({
      source: centerId,
      target: simNodeId,
      type: "similar_ayah",
      label: `Overlap ${overlapPct}%`
    });
  }

  return {
    ref,
    surahId,
    ayahNum,
    surahName: surah.name_translit,
    surahNameBn: surah.name_bn,
    arabicSnippet: ayahRecord.ar || "",
    englishSnippet: ayahRecord.en || "",
    nodes,
    edges,
    storyContext,
    connectedEntities,
    connectedStories
  };
}

/**
 * Extract an entity-centric subgraph (e.g. for Prophet Yusuf or Al-Hayy)
 */
export function extractEntitySubgraph(entityQuery: string): {
  entity: any;
  nodes: GraphNode[];
  edges: GraphEdge[];
} | null {
  const entities = entitiesData as Record<string, any>;
  const normalizedQuery = entityQuery.toLowerCase().replace(/^(person|place|name_of_allah|unseen|nation|glossary)[:\-]/, "").trim();

  // Find entity matching id, slug, or label
  let matchedEid = "";
  let matchedEntity: any = null;

  for (const [eid, ent] of Object.entries(entities)) {
    const slug = entityIdToSlug(eid).toLowerCase();
    const cleanId = eid.toLowerCase();
    const label = (ent.label_en || "").toLowerCase();

    if (
      cleanId === entityQuery.toLowerCase() ||
      slug === entityQuery.toLowerCase() ||
      slug === `person-${normalizedQuery}` ||
      slug === `name_of_allah-${normalizedQuery}` ||
      slug === `place-${normalizedQuery}` ||
      label === normalizedQuery ||
      label.includes(normalizedQuery)
    ) {
      matchedEid = eid;
      matchedEntity = ent;
      break;
    }
  }

  if (!matchedEntity) {
    return null;
  }

  const type = matchedEntity.type || "glossary";
  const palette = NODE_PALETTE[type] || NODE_PALETTE.glossary;
  const centerId = matchedEid;
  const nodes: GraphNode[] = [];
  const edges: GraphEdge[] = [];
  const seenNodes = new Set<string>();

  function addNode(node: GraphNode) {
    if (!seenNodes.has(node.id)) {
      seenNodes.add(node.id);
      nodes.push(node);
    }
  }

  // 1. Center Entity Node
  addNode({
    id: centerId,
    label: matchedEntity.label_en,
    label_ar: matchedEntity.label_ar,
    label_bn: matchedEntity.label_bn,
    sublabel: `${palette.label} (${(matchedEntity.ayat || []).length} verses)`,
    type: type as any,
    category: "center",
    color: palette.color,
    radius: 30,
    url: `/entity/${entityIdToSlug(centerId)}`,
    isCenter: true,
    properties: matchedEntity.properties
  });

  // 2. Connected Top Ayat (up to 8 key verses)
  const ayatList: string[] = matchedEntity.ayat || [];
  for (const ref of ayatList.slice(0, 8)) {
    const [sPart, aPart] = ref.split(":");
    const sId = parseInt(sPart, 10);
    const surah = surahMap.get(sId);
    const ayahNodeId = `ayah:${ref}`;

    addNode({
      id: ayahNodeId,
      label: `${surah ? surah.name_translit : `Surah ${sId}`} ${ref}`,
      sublabel: `Verse in Quran`,
      type: "ayah",
      category: "ayah",
      color: NODE_PALETTE.ayah.color,
      radius: 18,
      url: `/ayah/${sPart}/${aPart}`
    });

    edges.push({
      source: centerId,
      target: ayahNodeId,
      type: "mentions_in",
      label: "Mentions"
    });
  }

  // 3. Co-occurring Entities (Prophets, Places, Divine Names appearing in the same verses)
  const coOccurringCount = new Map<string, number>();
  for (const ref of ayatList) {
    for (const [eid, ent] of Object.entries(entities)) {
      if (eid !== centerId && ent.ayat && ent.ayat.includes(ref)) {
        coOccurringCount.set(eid, (coOccurringCount.get(eid) || 0) + 1);
      }
    }
  }

  const sortedCo = Array.from(coOccurringCount.entries()).sort((a, b) => b[1] - a[1]);
  for (const [eid, count] of sortedCo.slice(0, 7)) {
    const ent = entities[eid];
    const entType = ent.type || "glossary";
    const entPalette = NODE_PALETTE[entType] || NODE_PALETTE.glossary;

    addNode({
      id: eid,
      label: ent.label_en,
      label_ar: ent.label_ar,
      label_bn: ent.label_bn,
      sublabel: `${entPalette.label} (Co-occurs ${count}x)`,
      type: entType as any,
      category: entType,
      color: entPalette.color,
      radius: 19,
      url: `/entity/${entityIdToSlug(eid)}`
    });

    edges.push({
      source: centerId,
      target: eid,
      type: "co_occurs_with",
      label: `Co-occurs (${count}x)`
    });
  }

  // 4. Connected Story if applicable
  const stories = storiesData as any[];
  for (const s of stories) {
    // Check if story references this entity
    const storyIdLower = s.id.toLowerCase();
    const entityNameLower = matchedEntity.label_en.toLowerCase();
    if (storyIdLower.includes(normalizedQuery) || entityNameLower.includes(s.title_en.toLowerCase().replace(/the story of /, "").split(" ")[0])) {
      const storySlug = s.id.replace("story-", "");
      addNode({
        id: s.id,
        label: s.title_en,
        sublabel: "Connected Quranic Story",
        type: "story",
        category: "story",
        color: NODE_PALETTE.story.color,
        radius: 24,
        url: `/story/${storySlug}`
      });

      edges.push({
        source: centerId,
        target: s.id,
        type: "protagonist_in",
        label: "Story Arc"
      });
    }
  }

  return {
    entity: matchedEntity,
    nodes,
    edges
  };
}

/**
 * Extract a story-centric narrative subgraph
 */
export function extractStorySubgraph(storyQuery: string): {
  story: any;
  nodes: GraphNode[];
  edges: GraphEdge[];
} | null {
  const stories = storiesData as any[];
  const normalized = storyQuery.toLowerCase().replace(/^story-/, "").trim();

  const story = stories.find(
    (s) =>
      s.id.toLowerCase() === storyQuery.toLowerCase() ||
      s.id.replace("story-", "").toLowerCase() === normalized ||
      s.title_en.toLowerCase().includes(normalized)
  );

  if (!story) return null;

  const centerId = story.id;
  const nodes: GraphNode[] = [];
  const edges: GraphEdge[] = [];
  const seenNodes = new Set<string>();

  function addNode(node: GraphNode) {
    if (!seenNodes.has(node.id)) {
      seenNodes.add(node.id);
      nodes.push(node);
    }
  }

  // 1. Center Story Arc Node
  const storySlug = story.id.replace("story-", "");
  addNode({
    id: centerId,
    label: story.title_en,
    label_bn: story.title_bn,
    sublabel: `Quranic Story Arc (${(story.episodes || []).length} Episodes)`,
    type: "story",
    category: "center",
    color: NODE_PALETTE.story.color,
    radius: 30,
    url: `/story/${storySlug}`,
    isCenter: true
  });

  // 2. Episodes in chronological sequence
  const episodes: StoryEpisode[] = story.episodes || [];
  let prevEpId: string | null = null;

  for (let i = 0; i < episodes.length; i++) {
    const ep = episodes[i];
    const epId = `episode:${ep.id}`;

    addNode({
      id: epId,
      label: `Part ${i + 1}: ${ep.title_en}`,
      label_bn: ep.title_bn,
      sublabel: `Episode · Ayat ${ep.ayat}`,
      type: "episode",
      category: "episode",
      color: NODE_PALETTE.episode.color,
      radius: 20,
      url: `/story/${storySlug}`,
      properties: { ayat: ep.ayat }
    });

    edges.push({
      source: centerId,
      target: epId,
      type: "has_episode",
      label: `Act ${i + 1}`
    });

    // Chronological narrative link between consecutive episodes
    if (prevEpId) {
      edges.push({
        source: prevEpId,
        target: epId,
        type: "leads_to",
        label: "Next Episode →"
      });
    }
    prevEpId = epId;

    // Add first anchor verse for this episode
    const firstRef = ep.ayat.split("-")[0];
    const [sPart, aPart] = firstRef.split(":");
    const sId = parseInt(sPart, 10);
    const surah = surahMap.get(sId);
    const ayahNodeId = `ayah:${firstRef}`;

    addNode({
      id: ayahNodeId,
      label: `${surah ? surah.name_translit : `Surah ${sId}`} ${firstRef}`,
      sublabel: `Opening Ayah of Episode ${i + 1}`,
      type: "ayah",
      category: "ayah",
      color: NODE_PALETTE.ayah.color,
      radius: 16,
      url: `/ayah/${sPart}/${aPart}`
    });

    edges.push({
      source: epId,
      target: ayahNodeId,
      type: "begins_with",
      label: "Key Ayah"
    });
  }

  return {
    story,
    nodes,
    edges
  };
}

/**
 * Curated Macro Network representing the Quran's central ontological hubs
 */
export function getMacroGraph(): { nodes: GraphNode[]; edges: GraphEdge[] } {
  const nodes: GraphNode[] = [
    // --- Divine Names ---
    { id: "allah", label: "Allah (الله)", label_ar: "الله", type: "name_of_allah", category: "name_of_allah", color: "#d97706", radius: 30, url: "/entity/name_of_allah-allah", sublabel: "The Supreme Name" },
    { id: "ar-rahman", label: "Ar-Rahman (الرحمن)", label_ar: "الرحمن", type: "name_of_allah", category: "name_of_allah", color: "#d97706", radius: 22, url: "/entity/name_of_allah-ar-rahman", sublabel: "The Entirely Merciful" },
    { id: "ar-rahim", label: "Ar-Rahim (الرحيم)", label_ar: "الرحيم", type: "name_of_allah", category: "name_of_allah", color: "#d97706", radius: 22, url: "/entity/name_of_allah-ar-rahim", sublabel: "The Especially Merciful" },
    { id: "al-hayy", label: "Al-Hayy (الحي)", label_ar: "الحي", type: "name_of_allah", category: "name_of_allah", color: "#d97706", radius: 20, url: "/entity/name_of_allah-al-hayy", sublabel: "The Ever-Living" },
    { id: "al-qayyum", label: "Al-Qayyum (القيوم)", label_ar: "القيوم", type: "name_of_allah", category: "name_of_allah", color: "#d97706", radius: 20, url: "/entity/name_of_allah-al-qayyum", sublabel: "The Sustainer" },
    { id: "al-hakim", label: "Al-Hakim (الحكيم)", label_ar: "الحكيم", type: "name_of_allah", category: "name_of_allah", color: "#d97706", radius: 19, url: "/entity/name_of_allah-al-hakim", sublabel: "The All-Wise" },
    { id: "al-aziz", label: "Al-Aziz (العزيز)", label_ar: "العزيز", type: "name_of_allah", category: "name_of_allah", color: "#d97706", radius: 19, url: "/entity/name_of_allah-al-aziz", sublabel: "The Almighty" },

    // --- Major Prophets & Figures ---
    { id: "muhammad", label: "Muhammad ﷺ", label_ar: "محمد", type: "person", category: "person", color: "#059669", radius: 28, url: "/entity/person-muhammad", sublabel: "Final Messenger" },
    { id: "ibrahim", label: "Ibrahim (Abraham)", label_ar: "إبراهيم", type: "person", category: "person", color: "#059669", radius: 25, url: "/entity/person-ibrahim", sublabel: "Friend of Allah (Khalil)" },
    { id: "musa", label: "Musa (Moses)", label_ar: "موسى", type: "person", category: "person", color: "#059669", radius: 25, url: "/entity/person-musa", sublabel: "Spoken to by Allah (Kalim)" },
    { id: "isa", label: "Isa (Jesus)", label_ar: "عيسى", type: "person", category: "person", color: "#059669", radius: 23, url: "/entity/person-isa", sublabel: "Word & Spirit from Allah" },
    { id: "nuh", label: "Nuh (Noah)", label_ar: "نوح", type: "person", category: "person", color: "#059669", radius: 21, url: "/entity/person-nuh", sublabel: "The Ark Builder" },
    { id: "adam", label: "Adam", label_ar: "آدم", type: "person", category: "person", color: "#059669", radius: 22, url: "/entity/person-adam", sublabel: "Father of Humanity" },
    { id: "yusuf", label: "Yusuf (Joseph)", label_ar: "يوسف", type: "person", category: "person", color: "#059669", radius: 22, url: "/entity/person-yusuf", sublabel: "Prophet of Patience & Beauty" },
    { id: "yaqub", label: "Yaqub (Jacob)", label_ar: "يعقوب", type: "person", category: "person", color: "#059669", radius: 20, url: "/entity/person-yaqub-peace-be-upon-him", sublabel: "Father of the Tribes" },
    { id: "ismail", label: "Ismail (Ishmael)", label_ar: "إسماعيل", type: "person", category: "person", color: "#059669", radius: 20, url: "/entity/person-ismail", sublabel: "The Sacrificed Son" },
    { id: "dawud", label: "Dawud (David)", label_ar: "داود", type: "person", category: "person", color: "#059669", radius: 20, url: "/entity/person-dawud", sublabel: "Prophet-King & Zabur" },
    { id: "sulayman", label: "Sulayman (Solomon)", label_ar: "سليمان", type: "person", category: "person", color: "#059669", radius: 20, url: "/entity/person-sulayman", sublabel: "Sovereignty & Wisdom" },
    { id: "maryam", label: "Maryam (Mary)", label_ar: "مريم", type: "person", category: "person", color: "#059669", radius: 22, url: "/entity/person-maryam", sublabel: "Mother of Isa" },

    // --- Sacred Places & Landmarks ---
    { id: "makkah", label: "Makkah", label_ar: "مكة", type: "place", category: "place", color: "#2563eb", radius: 22, url: "/entity/place-makkah", sublabel: "The Sacred Sanctuary" },
    { id: "kaabah", label: "The Ka'bah", label_ar: "الكعبة", type: "place", category: "place", color: "#2563eb", radius: 21, url: "/entity/place-kaabah", sublabel: "First House of Worship" },
    { id: "al-quds", label: "Al-Aqsa / Bayt al-Maqdis", label_ar: "المسجد الأقصى", type: "place", category: "place", color: "#2563eb", radius: 20, url: "/entity/place-al-quds", sublabel: "The Blessed Sanctuary" },
    { id: "tur-sina", label: "Mount Sinai (Tur Sina)", label_ar: "طور سيناء", type: "place", category: "place", color: "#2563eb", radius: 19, url: "/entity/place-tur-sina", sublabel: "Mountain of Revelation" },
    { id: "madinah", label: "Madinah (Yathrib)", label_ar: "المدينة", type: "place", category: "place", color: "#2563eb", radius: 19, url: "/entity/place-madinah", sublabel: "City of the Prophet ﷺ" },

    // --- Major Story Narrative Arcs ---
    { id: "story-yusuf", label: "Story of Yusuf", label_bn: "ইউসুফের কাহিনী", type: "story", category: "story", color: "#f59e0b", radius: 24, url: "/story/yusuf", sublabel: "Ahsan al-Qasas (Best of Stories)" },
    { id: "story-musa", label: "Story of Musa", label_bn: "মুসার কাহিনী", type: "story", category: "story", color: "#f59e0b", radius: 24, url: "/story/musa", sublabel: "Pharaoh, Exodus & Sinai" },
    { id: "story-ibrahim", label: "Story of Ibrahim", label_bn: "ইব্রাহিমের কাহিনী", type: "story", category: "story", color: "#f59e0b", radius: 23, url: "/story/ibrahim", sublabel: "Search for Truth & Monotheism" },
    { id: "story-fil", label: "People of the Elephant", label_bn: "আসহাবুল ফিল", type: "story", category: "story", color: "#f59e0b", radius: 20, url: "/story/fil", sublabel: "Protection of the Ka'bah" },

    // --- Core Thematic Concepts & Unseen ---
    { id: "tawhid", label: "Tawhid (Absolute Oneness)", label_ar: "التوحيد", type: "theme", category: "theme", color: "#a855f7", radius: 25, url: "/search?q=tawhid", sublabel: "Central Core of Islam" },
    { id: "akhirah", label: "Akhirah (The Hereafter)", label_ar: "الآخرة", type: "theme", category: "theme", color: "#a855f7", radius: 23, url: "/search?q=akhirah", sublabel: "Resurrection & Accountability" },
    { id: "sabr", label: "Sabr (Patience & Steadfastness)", label_ar: "الصبر", type: "theme", category: "theme", color: "#a855f7", radius: 21, url: "/search?q=patience", sublabel: "Key Moral Virtue" },
    { id: "salah", label: "Salah (Prayer)", label_ar: "الصلاة", type: "theme", category: "theme", color: "#a855f7", radius: 21, url: "/search?q=salah", sublabel: "Pillar of Worship" },
    { id: "jannah", label: "Jannah (Paradise)", label_ar: "الجنة", type: "unseen", category: "unseen", color: "#8b5cf6", radius: 22, url: "/entity/unseen-jannah", sublabel: "Gardens of Eternal Delight" },
    { id: "jahannam", label: "Jahannam (Hellfire)", label_ar: "جهنم", type: "unseen", category: "unseen", color: "#8b5cf6", radius: 20, url: "/entity/unseen-jahannam", sublabel: "The Fire of Retribution" },
    { id: "al-kursi", label: "Al-Kursi (The Footstool)", label_ar: "الكرسي", type: "unseen", category: "unseen", color: "#8b5cf6", radius: 21, url: "/entity/unseen-kursi", sublabel: "Verse 2:255" }
  ];

  const edges: GraphEdge[] = [
    // Allah connections
    { source: "allah", target: "ar-rahman", type: "divine_attribute", label: "Attribute" },
    { source: "allah", target: "ar-rahim", type: "divine_attribute", label: "Attribute" },
    { source: "allah", target: "al-hayy", type: "divine_attribute", label: "Attribute" },
    { source: "allah", target: "al-qayyum", type: "divine_attribute", label: "Attribute" },
    { source: "allah", target: "al-hakim", type: "divine_attribute", label: "Attribute" },
    { source: "allah", target: "al-aziz", type: "divine_attribute", label: "Attribute" },
    { source: "allah", target: "tawhid", type: "core_doctrine", label: "Monotheism" },
    { source: "al-hayy", target: "al-kursi", type: "celebrated_in", label: "Ayat al-Kursi (2:255)" },
    { source: "al-qayyum", target: "al-kursi", type: "celebrated_in", label: "Ayat al-Kursi (2:255)" },

    // Prophets lineage & fraternity
    { source: "adam", target: "nuh", type: "ancestor_of", label: "Early Prophets" },
    { source: "nuh", target: "ibrahim", type: "ancestor_of", label: "Prophetic Lineage" },
    { source: "ibrahim", target: "ismail", type: "father_of", label: "Father of Ismail" },
    { source: "ibrahim", target: "yaqub", type: "grandfather_of", label: "Lineage of Yaqub" },
    { source: "yaqub", target: "yusuf", type: "father_of", label: "Father of Yusuf" },
    { source: "ismail", target: "muhammad", type: "ancestor_of", label: "Arabian Lineage" },
    { source: "ibrahim", target: "musa", type: "lineage", label: "Prophets of the Book" },
    { source: "musa", target: "dawud", type: "succession", label: "Israelite Prophets" },
    { source: "dawud", target: "sulayman", type: "father_of", label: "Father of Sulayman" },
    { source: "sulayman", target: "isa", type: "lineage", label: "Israelite Prophethood" },
    { source: "maryam", target: "isa", type: "mother_of", label: "Virgin Birth" },
    { source: "isa", target: "muhammad", type: "glad_tidings_of", label: "Prophecy of Ahmad" },

    // Geography & Places
    { source: "ibrahim", target: "kaabah", type: "built", label: "Raised Foundation" },
    { source: "ismail", target: "kaabah", type: "co_builder", label: "Raised Foundation" },
    { source: "kaabah", target: "makkah", type: "located_in", label: "Heart of Makkah" },
    { source: "muhammad", target: "makkah", type: "birthplace", label: "Birthplace" },
    { source: "muhammad", target: "madinah", type: "hijrah", label: "The City of Hijrah" },
    { source: "muhammad", target: "al-quds", type: "isra_miraj", label: "Night Journey (17:1)" },
    { source: "musa", target: "tur-sina", type: "communed_with_allah", label: "Spoken to at Mount Tur" },
    { source: "dawud", target: "al-quds", type: "sanctuary", label: "Bayt al-Maqdis" },
    { source: "sulayman", target: "al-quds", type: "sanctuary", label: "Mihrab & Temple" },

    // Stories & Prophets
    { source: "story-yusuf", target: "yusuf", type: "protagonist", label: "Main Subject" },
    { source: "story-yusuf", target: "yaqub", type: "character", label: "Father's Grief & Reunion" },
    { source: "story-yusuf", target: "sabr", type: "moral_theme", label: "Sabrun Jamil" },
    { source: "story-musa", target: "musa", type: "protagonist", label: "Main Subject" },
    { source: "story-musa", target: "tur-sina", type: "setting", label: "Sacred Valley Tuwa" },
    { source: "story-ibrahim", target: "ibrahim", type: "protagonist", label: "Iconoclast & Builder" },
    { source: "story-ibrahim", target: "tawhid", type: "moral_theme", label: "Hanif Monotheism" },
    { source: "story-fil", target: "kaabah", type: "defended_sanctuary", label: "Miraculous Defense" },

    // Themes & Concepts
    { source: "tawhid", target: "akhirah", type: "fundamental_belief", label: "Pillars of Faith" },
    { source: "tawhid", target: "salah", type: "manifestation", label: "Devotional Worship" },
    { source: "sabr", target: "salah", type: "commanded_together", label: "Seek Help (2:45)" },
    { source: "akhirah", target: "jannah", type: "destination", label: "Reward of Righteous" },
    { source: "akhirah", target: "jahannam", type: "destination", label: "Warning for Injustice" }
  ];

  return { nodes, edges };
}
