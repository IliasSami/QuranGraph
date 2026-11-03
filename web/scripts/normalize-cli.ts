// Bridge for the Python pipeline: reads a JSON array of strings on stdin, writes a JSON array of token lists
// ([[term, surface, script, stop, skeleton], ...] per input) to stdout. Used by ingest/core/normalize.py so both sides
// analyse text with exactly the same code.
import { tokenize, arabicSkeleton } from "../src/lib/search/normalize.ts";

let input = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", (c) => (input += c));
process.stdin.on("end", () => {
  const texts: string[] = JSON.parse(input);
  const out = texts.map((t) => tokenize(t).map((k) => [k.term, k.surface, k.script, k.stop ? 1 : 0,
    k.script === "arabic" ? arabicSkeleton(k.term) : k.term]));
  process.stdout.write(JSON.stringify(out));
});
