import type { APIRoute } from "astro";
import surahsData from "../lib/search/surahs.json" with { type: "json" };
import entitiesData from "../data/graph/entities.json" with { type: "json" };
import rootsData from "../data/graph/roots.json" with { type: "json" };
import storiesData from "../data/graph/stories.json" with { type: "json" };
import { entityIdToSlug } from "../lib/graph/subgraph.ts";

export const GET: APIRoute = async ({ site }) => {
  const baseUrl = site ? site.toString().replace(/\/$/, "") : "https://qurangraph.iliassami57.workers.dev";
  const now = new Date().toISOString().split("T")[0];

  interface SitemapUrl {
    loc: string;
    lastmod: string;
    changefreq: "always" | "hourly" | "daily" | "weekly" | "monthly" | "yearly" | "never";
    priority: string;
  }

  const urls: SitemapUrl[] = [
    { loc: `${baseUrl}`, lastmod: now, changefreq: "daily", priority: "1.0" },
    { loc: `${baseUrl}/search`, lastmod: now, changefreq: "weekly", priority: "0.95" },
    { loc: `${baseUrl}/surahs`, lastmod: now, changefreq: "weekly", priority: "0.9" },
    { loc: `${baseUrl}/graph`, lastmod: now, changefreq: "weekly", priority: "0.9" },
    { loc: `${baseUrl}/learn`, lastmod: now, changefreq: "weekly", priority: "0.9" },
    { loc: `${baseUrl}/numbers`, lastmod: now, changefreq: "monthly", priority: "0.8" },
    { loc: `${baseUrl}/sources`, lastmod: now, changefreq: "monthly", priority: "0.7" },
  ];

  // 114 Surahs
  for (const s of surahsData) {
    urls.push({
      loc: `${baseUrl}/surah/${s.id}`,
      lastmod: now,
      changefreq: "weekly",
      priority: "0.85",
    });

    // 6,236 Ayat
    for (let a = 1; a <= s.ayat; a++) {
      urls.push({
        loc: `${baseUrl}/ayah/${s.id}/${a}`,
        lastmod: now,
        changefreq: "monthly",
        priority: "0.75",
      });
    }
  }

  // 884 Entities
  for (const id of Object.keys(entitiesData)) {
    const slug = entityIdToSlug(id);
    urls.push({
      loc: `${baseUrl}/entity/${encodeURIComponent(slug)}`,
      lastmod: now,
      changefreq: "monthly",
      priority: "0.7",
    });
  }

  // 1,651 Roots
  for (const rootKey of Object.keys(rootsData)) {
    urls.push({
      loc: `${baseUrl}/root/${encodeURIComponent(rootKey)}`,
      lastmod: now,
      changefreq: "monthly",
      priority: "0.7",
    });
  }

  // Stories
  for (const story of storiesData as any[]) {
    const slug = story.id.replace("story-", "");
    urls.push({
      loc: `${baseUrl}/story/${encodeURIComponent(slug)}`,
      lastmod: now,
      changefreq: "monthly",
      priority: "0.8",
    });
  }

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls
  .map(
    (u) => `  <url>
    <loc>${u.loc}</loc>
    <lastmod>${u.lastmod}</lastmod>
    <changefreq>${u.changefreq}</changefreq>
    <priority>${u.priority}</priority>
  </url>`
  )
  .join("\n")}
</urlset>`;

  return new Response(xml, {
    headers: {
      "Content-Type": "application/xml; charset=utf-8",
      "Cache-Control": "public, max-age=86400, s-maxage=86400",
    },
  });
};
