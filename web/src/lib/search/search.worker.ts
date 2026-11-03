import { search } from "./engine.ts";

self.onmessage = (e: MessageEvent<{ query: string; limit?: number }>) => {
  const { query, limit = 10 } = e.data;
  const t0 = performance.now();
  const results = search(query, limit);
  const t1 = performance.now();
  self.postMessage({
    results,
    durationMs: t1 - t0
  });
};
