// Loads the generated definition bundle (produced by scripts/sync-scores.mjs
// from the canonical scores/*.json before every dev/build/test).
import raw from "./generated/scores.json";
import type { ScoreDefinition } from "./engine/types";

export const SCORES = raw as unknown as ScoreDefinition[];

export function scoresBySection(): Map<number, ScoreDefinition[]> {
  const byId = new Map<number, ScoreDefinition[]>();
  for (const s of SCORES) {
    const list = byId.get(s.section) ?? [];
    list.push(s);
    byId.set(s.section, list);
  }
  return byId;
}

export function getScore(id: string): ScoreDefinition | undefined {
  return SCORES.find((s) => s.id === id);
}
