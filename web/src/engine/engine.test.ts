// Cross-implementation conformance: the TypeScript engine must reproduce every
// golden vector declared in the canonical definitions — the SAME vectors the
// Python reference engine is held to. If these diverge, the math has drifted.
import { describe, expect, it } from "vitest";
import { compute } from "./engine";
import { SCORES } from "../data";

describe("golden vectors", () => {
  it("loads at least one definition", () => {
    expect(SCORES.length).toBeGreaterThan(0);
  });

  for (const def of SCORES) {
    for (const [i, vector] of def.tests.entries()) {
      it(`${def.id} :: ${vector.name ?? `vector-${i}`}`, () => {
        const result = compute(def, vector.inputs);
        expect(result.score).toBe(vector.expected_score);
        if (vector.expected_band !== undefined) {
          expect(result.band).toBe(vector.expected_band);
        }
      });
    }
  }
});
