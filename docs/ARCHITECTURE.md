# Architecture

*Reference framework: ISO/IEC/IEEE 12207 (life-cycle processes), IEC 62304
(medical-device software). Design intent: separate safety-critical clinical
**data** from **code**, and verify the data the same way the catalogue verifies
citations.*

## Components

```
SCORES.md ──R# citations──┐                 scores/<id>.json  (calculable definitions)
 (catalogue, contract)     │   each cutoff/band cites R#  │
                           ▼                              ▼
              tools/verify_scores.py          tools/verify_definitions.py
              (citation contract)             (schema + reference + golden-vector contract)
                                                          │
        ┌─────────────────────────────────────────────────┼───────────────────────────────┐
        ▼                                                  ▼                                ▼
 engine/ccscores  (Python, reference)        web/src/engine  (TypeScript)         scores[].tests (golden vectors)
        └──────────────────────── both reproduce every golden vector ───────────────────────┘
                                                          │
                                                          ▼
                                  web/  React + Vite SPA (form-from-definition)
                                                          │
                                              GitHub Pages (CI-deployed)
```

## Key decisions

1. **Definitions are the database.** One JSON file per score (`scores/<id>.json`),
   validated by `schema/score.schema.json` (JSON Schema Draft 2020-12). The file is
   the single source for both engines, the gate, and the UI.

2. **Two engines, one contract.** `engine/ccscores` (Python, stdlib-only) is the
   *reference* implementation; `web/src/engine` is a faithful TypeScript port. Every
   definition ships `tests[]` (golden vectors) that **both** must reproduce. Rounding
   is pinned to half-up (`floor(x+0.5)`) in both so results never diverge.

3. **Safe formula evaluation.** Formula scores use a constrained expression
   (`+ - * / % ^`, `ln exp log10 sqrt min max round floor ceil abs clamp`). Python
   walks an `ast` whitelist; TypeScript uses a hand-written recursive-descent parser.
   **No `eval` / no `Function`** in either engine.

4. **Two aggregate modes.** `sum` (per-input point mapping: numeric `bins` or enum
   `option→points` or boolean) covers additive scores; `formula` over raw values
   covers computed scores. Output `bands` map the total to an interpretation.

5. **Client-side only.** Computation runs in the browser; inputs never leave the
   device. The "live database" is the CI-published, versioned definition set —
   updates flow through git/CI exactly like the citation ratchet.

6. **Mobile-ready.** The TypeScript engine is framework-agnostic; a future React
   Native app reuses the identical `scores/*.json` + engine + golden vectors.

## Data flow (one calculation)

`UI form → values map → compute(definition, values) → {score, band, breakdown} → ResultCard`.
The same `compute()` signature exists in both engines.

## Build/codegen

`web/scripts/sync-scores.mjs` bundles `scores/*.json` into `web/src/generated/scores.json`
before every dev/build/test, so the UI, the build, and the TS tests all see exactly the
canonical definitions (no importing JSON from outside the web root).
