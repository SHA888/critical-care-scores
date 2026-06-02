// Structured citations parsed from SCORES.md References (by scripts/sync-scores.mjs).
import raw from "./generated/references.json";

export interface Reference {
  code: string;
  text: string;
  url: string | null;
}

const ALL = raw as Reference[];
const BY_CODE = new Map(ALL.map((r) => [r.code, r]));

export function getReference(code: string): Reference | undefined {
  return BY_CODE.get(code);
}

/** Union of a score's top-level references and any band-level refs, sorted. */
export function citedCodes(references: string[], bandRefs: (string | undefined)[]): string[] {
  const set = new Set(references);
  for (const r of bandRefs) if (r) set.add(r);
  return [...set].sort((a, b) => Number(a.slice(1)) - Number(b.slice(1)));
}
