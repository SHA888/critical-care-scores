// Generates web/src/generated/scores.json from the canonical scores/*.json.
// Run automatically before dev/build/test (npm pre* hooks). Keeping the data in
// one generated bundle avoids importing JSON from outside the web root and makes
// dev, build, and test see exactly the same definitions.
import { readdirSync, readFileSync, mkdirSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(here, "..", "..");
const scoresDir = resolve(repoRoot, "scores");
const scoresMd = resolve(repoRoot, "SCORES.md");
const outDir = resolve(here, "..", "src", "generated");

const files = readdirSync(scoresDir).filter((f) => f.endsWith(".json"));
const defs = files
  .map((f) => JSON.parse(readFileSync(join(scoresDir, f), "utf-8")))
  .sort((a, b) => a.section - b.section || a.name.localeCompare(b.name));

// Parse the SCORES.md References section into structured citations so the web UI
// can show full references (and DOI links) for a calculated score. Mirrors the
// reference grammar that tools/verify_scores.py validates against.
function mdToText(s) {
  return s.replace(/\*\*(.+?)\*\*/g, "$1").replace(/_(.+?)_/g, "$1").replace(/\s+/g, " ").trim();
}
function parseReferences(md) {
  const lines = md.split(/\r?\n/);
  let inRefs = false;
  const refs = [];
  for (const line of lines) {
    if (/^#+\s+References/.test(line)) { inRefs = true; continue; }
    if (inRefs && /^#+\s/.test(line)) break; // next section ends References
    const m = inRefs && line.match(/^\s*[-*]\s*\*\*(R\d+)\*\*\s*[—–-]?\s*(.*)$/);
    if (m) {
      const url = (m[2].match(/https?:\/\/\S+/) || [null])[0];
      refs.push({ code: m[1], text: mdToText(m[2]), url });
    }
  }
  return refs.sort((a, b) => Number(a.code.slice(1)) - Number(b.code.slice(1)));
}
const references = parseReferences(readFileSync(scoresMd, "utf-8"));

mkdirSync(outDir, { recursive: true });
writeFileSync(join(outDir, "scores.json"), JSON.stringify(defs, null, 2) + "\n");
writeFileSync(join(outDir, "references.json"), JSON.stringify(references, null, 2) + "\n");
console.log(
  `sync-scores: wrote ${defs.length} definition(s) and ${references.length} reference(s) to src/generated/`,
);
