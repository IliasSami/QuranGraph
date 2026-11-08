import { test } from "node:test";
import assert from "node:assert/strict";
import {
  extractAyahSubgraph,
  extractEntitySubgraph,
  extractStorySubgraph,
  getMacroGraph,
  entityIdToSlug
} from "../src/lib/graph/subgraph.ts";

test("extractAyahSubgraph: Ayat al-Kursi (2:255)", () => {
  const sub = extractAyahSubgraph("2:255");
  assert.equal(sub.ref, "2:255");
  assert.equal(sub.surahId, 2);
  assert.equal(sub.ayahNum, 255);
  assert.ok(sub.surahName.includes("Baqar"));

  // Center node must be the verse itself
  const center = sub.nodes.find((n) => n.isCenter);
  assert.ok(center);
  assert.equal(center?.id, "ayah:2:255");

  // Check connected Divine Names
  const divineNames = sub.nodes.filter((n) => n.type === "name_of_allah");
  assert.ok(divineNames.length >= 3, `Expected at least 3 divine names, got ${divineNames.length}`);
  const divineLabels = divineNames.map((d) => d.label);
  assert.ok(divineLabels.some((l) => l.includes("Hayy")));
  assert.ok(divineLabels.some((l) => l.includes("Qayyum")));

  // Check roots
  const roots = sub.nodes.filter((n) => n.type === "root");
  assert.ok(roots.length > 0, "Expected roots to be extracted");

  // Check similar verses
  const similar = sub.nodes.filter((n) => n.type === "similar_ayah");
  assert.ok(similar.length > 0, "Expected similar verses to be extracted");
});

test("extractAyahSubgraph: Surah Yusuf Episode (12:4)", () => {
  const sub = extractAyahSubgraph("12:4");
  assert.equal(sub.ref, "12:4");
  assert.ok(sub.storyContext !== null, "Expected storyContext for 12:4");
  assert.equal(sub.storyContext?.storyId, "story-yusuf");
  assert.equal(sub.storyContext?.activeEpisodes[0]?.title_en, "The Dream of Eleven Stars");

  // Check Prophets
  const prophets = sub.nodes.filter((n) => n.type === "person");
  assert.ok(prophets.some((p) => p.label.includes("Yusuf")));
  assert.ok(prophets.some((p) => p.label.includes("Yaqub")));

  // Check Story Node & Episode Node
  const storyNode = sub.nodes.find((n) => n.type === "story");
  const episodeNode = sub.nodes.find((n) => n.type === "episode");
  assert.ok(storyNode);
  assert.ok(episodeNode);
});

test("extractAyahSubgraph: Surah Al-Kahf Musa & Khidr (18:60)", () => {
  const sub = extractAyahSubgraph("18:60");
  assert.equal(sub.ref, "18:60");
  assert.ok(sub.storyContext !== null);
  assert.equal(sub.storyContext?.storyId, "story-musa");

  // Check Place (Junction of two seas)
  const places = sub.nodes.filter((n) => n.type === "place");
  assert.ok(places.length > 0);
});

test("extractEntitySubgraph: Prophet Yusuf", () => {
  const entSub = extractEntitySubgraph("person:yusuf");
  assert.ok(entSub !== null);
  assert.equal(entSub?.nodes[0]?.isCenter, true);
  assert.ok(entSub?.nodes[0]?.label.includes("Yusuf"));

  // Must connect to related verses
  const verses = entSub?.nodes.filter((n) => n.type === "ayah");
  assert.ok((verses?.length || 0) > 0);

  // Must connect to co-occurring entities
  const co = entSub?.edges.filter((e) => e.type === "co_occurs_with");
  assert.ok((co?.length || 0) > 0);
});

test("extractStorySubgraph: Story of Yusuf", () => {
  const storySub = extractStorySubgraph("story-yusuf");
  assert.ok(storySub !== null);
  assert.equal(storySub?.story.id, "story-yusuf");

  // Must have episodes linked chronologically
  const episodeNodes = storySub?.nodes.filter((n) => n.type === "episode");
  assert.equal(episodeNodes?.length, 6);

  const sequentialEdges = storySub?.edges.filter((e) => e.type === "leads_to");
  assert.equal(sequentialEdges?.length, 5); // 6 episodes connected linearly by 5 leads_to edges
});

test("getMacroGraph: Central Ontological Hubs", () => {
  const macro = getMacroGraph();
  assert.ok(macro.nodes.length >= 30, "Expected at least 30 central hubs");
  assert.ok(macro.edges.length >= 30, "Expected at least 30 semantic edges");

  const types = new Set(macro.nodes.map((n) => n.type));
  assert.ok(types.has("name_of_allah"));
  assert.ok(types.has("person"));
  assert.ok(types.has("place"));
  assert.ok(types.has("story"));
  assert.ok(types.has("theme"));
});

test("entityIdToSlug: formatting rules", () => {
  assert.equal(entityIdToSlug("person:adam"), "person-adam");
  assert.equal(entityIdToSlug("name_of_allah:al-hayy"), "name_of_allah-al-hayy");
  assert.equal(entityIdToSlug("place:tur-sina"), "place-tur-sina");
});
