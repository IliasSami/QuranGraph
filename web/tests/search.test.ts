import { test } from "node:test";
import assert from "node:assert/strict";
import goldenData from "./golden.json" with { type: "json" };
import { search } from "../src/lib/search/engine.ts";

interface GoldenQuery {
  q: string;
  expect: string[];
  k: number;
  type: string;
}

const queries: GoldenQuery[] = goldenData.queries;

test("Search Golden Set Benchmark", async (t) => {
  let passed = 0;
  let failed = 0;
  const failures: { q: string; type: string; expect: string[]; got: string[]; k: number }[] = [];

  for (const item of queries) {
    await t.test(`Query [${item.type}]: "${item.q}"`, () => {
      const results = search(item.q, Math.max(item.k, 15));
      const topKRefs = results.slice(0, item.k).map((r) => r.ref);

      if (item.k === 0) {
        // No crash test
        assert.ok(Array.isArray(results));
        passed++;
        return;
      }

      const hasMatch = item.expect.some((expected) => topKRefs.includes(expected));
      if (!hasMatch) {
        failures.push({
          q: item.q,
          type: item.type,
          expect: item.expect,
          got: topKRefs,
          k: item.k
        });
        failed++;
      } else {
        passed++;
      }

      assert.ok(
        hasMatch,
        `Expected one of [${item.expect.join(", ")}] within top ${item.k}, but got [${topKRefs.join(", ")}]`
      );
    });
  }

  console.log(`\n--- Golden Search Benchmark Summary ---`);
  console.log(`Passed: ${passed}/${queries.length} (${Math.round((passed / queries.length) * 100)}%)`);
  if (failed > 0) {
    console.log(`Failed ${failed} queries.`);
  }
});
