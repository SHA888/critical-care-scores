# Critical Care Scores — Living Reference

A domain-organized reference of ICU scoring systems, paired with two small tools that keep it honest and current. The reference asserts nothing about a score's 2026 currency unless a citation backs it, and the backing is enforced by CI.

## The loop

```
tools/discover_scores.py  ──finds candidate DOIs──▶  human/triage  ──annotates──▶  SCORES.md
           ▲                                                                             │
           └──────────────── keywords auto-extracted from the doc ◀────────────────────┘
                                                                                        │
 tools/verify_scores.py  ──gates: every non-`unverified` row must cite a resolvable ref──▶ CI (red on breach)
```

**Discovery proposes, the gate disposes.** `discover` only _finds_ and triages candidates; it never sets a status. `verify` only _checks_ that claimed statuses are cited; it never fetches. The Markdown doc is the single source of truth.

## Calculator (web + future mobile)

On top of the catalogue sits a **calculation layer**: verified scores are encoded as
structured JSON definitions and computed in a browser-only SPA — no patient data leaves
the device. The platform follows an industry-standard SDLC framing (ISO/IEC/IEEE 12207,
IEC 62304 Class B, ISO 14971 risk management); see [`docs/`](docs/).

```
scores/<id>.json ──schema + R# refs + golden vectors──▶ verify_definitions.py (calc contract)
        │                                                          │
        ├─▶ engine/ccscores (Python reference) ─┐                  │
        └─▶ web/src/engine  (TypeScript)        ├─ both reproduce every golden vector
                                                ▼
                              web/  React + Vite SPA ─▶ GitHub Pages
```

**The calculator exposes only scores that pass _both_ contracts** — citation-verified
(`SCORES.md`) **and** formula-verified (golden vectors reproduced by two independent
engines). `unverified` rows stay reference-only. Run it:

```sh
# enforce the calculation contract (schema + references + golden vectors)
uv run --with jsonschema tools/verify_definitions.py
uv run --with pytest python -m pytest engine/tests -q       # Python reference engine

cd web && npm ci && npm test && npm run dev                 # TS engine tests + dev server
```

## Files

| File              | Role                                                                 | Version |
| ----------------- | -------------------------------------------------------------------- | ------- |
| `SCORES.md`       | The reference: 24 domains, ~172 rows, `Status` + `Key ref` per row   | 0.2.0   |
| `TODO.md`         | Atomic verification backlog, protocol, SemVer milestones             | 0.1.0   |
| `tools/`          | **Directory** containing discovery and verification tools            | —       |
| —                 | `discover_scores.py` — keyword→DOI harvester; feeds the verification queue | 0.1.0   |
| —                 | `verify_scores.py` — CI gate; enforces status/citation contract + ratchet   | —       |
| —                 | `verify_definitions.py` — CI gate; schema + R# refs + golden-vector contract | —       |
| `schema/`         | `score.schema.json` — JSON Schema for calculable definitions         | —       |
| `scores/`         | Structured, calculable score definitions (`<id>.json`)               | —       |
| `engine/`         | Python reference calculation engine (`ccscores`) + golden-vector tests | 0.1.0   |
| `web/`            | React + Vite SPA + TypeScript engine (client-side calculator)        | 0.3.0   |
| `docs/`           | SDLC artifacts: `REQUIREMENTS.md`, `ARCHITECTURE.md`, `RISK.md`      | —       |

Current state: **11 rows verified, 161 `unverified`** (a citation-check-pending flag, _not_ an invalidity claim). `1.0.0` of the reference = `unverified == 0` with all DOIs resolving.

## Quickstart

```sh
# see what we'd search for (no network)
uv run tools/discover_scores.py keywords

# harvest recent candidate DOIs into the living DB
uv run tools/discover_scores.py discover --since 2023 --sources crossref,pubmed --mailto you@example.org
uv run tools/discover_scores.py report --triage candidate

# enforce the contract (CI gate); lower the ceiling as rows get verified
uv run tools/verify_scores.py SCORES.md --max-unverified 161
uv run tools/verify_scores.py SCORES.md --max-unverified 0 --check-dois   # pre-1.0.0
```

Both scripts are stdlib-only (Python ≥3.11; PEP 723 headers, so `uv run` needs no setup). `discover` uses public Crossref + NCBI E-utilities; no API key required (`--ncbi-api-key` only raises rate limits).

## Status taxonomy

`current` · `superseded` · `contested` · `unverified` (default). A row may carry one of the first three **only if** `Key ref` is non-empty; `unverified` rows **must** be ref-empty. The gate is the mechanism that makes this true rather than aspirational.

See [`TODO.md`](TODO.md) for the verification protocol, Definition of Done per row, work breakdown by domain, and milestones.

## Verified deltas (2026-06-01)

ARDS Berlin → New Global Definition 2024 (`superseded`); pediatric sepsis → Phoenix 2024 (`current`); adult sepsis SIRS `superseded` / qSOFA `contested` / SOFA `current`; hepatic allocation → MELD 3.0 + PELD-Cr (`current`); AKI RIFLE/AKIN `superseded` → KDIGO `current` (watch: KDIGO 2026 final). Sources R1–R7 in the reference.

## See also

- **[`SCORES.md`](SCORES.md)** — The scoring systems reference itself (24 domains, ~172 scores).
- **[`TODO.md`](TODO.md)** — Verification protocol, work breakdown, and roadmap to 1.0.0.

## Known rough edges

- `discover` auto-queries are noisy for ~15 rows whose "Full name" is a component mnemonic (AIMS65, 4Ts, APGAR…). Fix: a small curated `OVERRIDES` map before the fallback.
- MCP sources (bioRxiv, Scite, Scholar Gateway, Clinical Trials) are a documented seam (`McpSourceAdapter`), not yet wired — Crossref + PubMed cover DOI discovery out of the box.
- Live HTTP adapters are unit-tested against fixtures, not yet against the real endpoints.

## Caveat

Not medical advice. The reference gives identity and intent of each instrument; exact cutoffs and bedside use must be confirmed against the primary source or a validated calculator.

## License

**Dual licensing**:

- **Code** (tools/*.py): [MIT License](LICENSE)
- **Documentation** (SCORES.md, TODO.md, etc.): [Creative Commons Attribution 4.0 International (CC BY 4.0)](LICENSE.docs)

See individual license files for details. External contributions welcome under these terms.
