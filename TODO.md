# TODO — Score Currency Verification (`SCORES.md`)

**Companion to:** `SCORES.md` · **Repo release:** 0.3.0 (single SemVer line — see §4) · **Created:** 2026-06-01

Goal: drive the document's `unverified` count from **161 → 0**, with every non-`unverified` row backed by a resolvable citation, enforced by `verify_scores.py` in CI. Reaching zero unlocks the `1.0.0` tag of the reference.

---

## 0. Definition of Done (per row) — the atomic unit

A single table row is **Done** when all hold:

- [ ] Primary derivation source identified (DOI or PMID).
- [ ] 2026 currency determined against the relevant **governing body / current guideline** (not a secondary blog/calculator).
- [ ] `Status` set to one of `current` / `superseded` / `contested` (never left `unverified` once worked).
- [ ] `Key ref` populated with ≥1 `R#` code resolving to a **References** entry.
- [ ] If `superseded`/`contested`: the superseding instrument or the nature of the dispute named in the section note.
- [ ] Verification date appended to the section note.
- [ ] `verify_scores.py` passes with the new (lower) `--max-unverified` ceiling.

> Rows that bundle multiple instruments (e.g. `MELD / MELD-Na / MELD 3.0`) are one unit; split into separate rows only if their statuses diverge.

---

## 1. Verification protocol (the method)

**Source hierarchy** (stop at the highest tier that answers currency):

1. Governing body / allocation authority (OPTN, KDIGO, SCCM/ESICM, WHO, specialty college).
2. Current clinical practice guideline (GRADE-based, ≤5 yr old) citing the score.
3. Primary derivation + most recent external validation (PubMed).
4. Living systematic review / registry recalibration.

**Status decision rule:**

- `current` — named or assumed-standard in tier-1/2 source dated within the last guideline cycle.
- `superseded` — a tier-1/2 source designates a replacement; original retained only for legacy/prognostic use.
- `contested` — in use, but a tier-1/2/3 source documents a material validity problem (e.g. poor sensitivity, calibration failure) without a clean replacement.

**Tooling order (cheapest first):** PubMed MCP for primary refs/validation → web search of the governing body for adoption/currency → `--check-dois` before merge.

**Anti-patterns to refuse:** asserting `current` from training memory without a tier-1/2 hit; citing MDCalc/UpToDate as the _primary_ currency source; widening a quote instead of paraphrasing a guideline.

---

## 2. CI enforcement (the mechanism) — live

`.github/workflows/verify-scores.yml` is the gate and is the source of truth;
the snippet below is illustrative. Two jobs run on every PR/push:
`verify` (both contracts + dual-engine golden vectors + typecheck + build) and
`deploy` (publishes the SPA to GitHub Pages on push to `main`).

- [x] Workflow live; `verify` red on any contract breach.
- [x] Baseline ceiling pinned at **161**; lower it on each merged batch (the ratchet).
- [x] DOIs resolved via the **DOI Handle System API** (`--check-dois`, blocking on push) — see `tools/verify_scores.py:check_doi_resolves`.
- [x] Actions pinned to Node-24 majors (checkout@v6, setup-node@v6, setup-uv@v7, upload-pages-artifact@v5, deploy-pages@v5).
- [ ] Branch protection: require the **`verify`** job green before merge.
- [ ] On each domain batch merge: decrement `--max-unverified` to the new actual count (ratchet — only down).
- [ ] Pre-`1.0.0`: ratchet reaches `--max-unverified 0` with `--check-dois` green.

Run the same gates locally (stdlib-only; `--no-project` mirrors CI):

```sh
uv run --no-project python tools/verify_scores.py SCORES.md --max-unverified 161
uv run --no-project --with jsonschema python tools/verify_definitions.py
uv run --no-project --with pytest python -m pytest engine/tests -q
uv run --no-project python tools/verify_scores.py SCORES.md --max-unverified 161 --check-dois
```

---

## 3. Work breakdown by domain

Priority tiers reflect **probability of having moved since derivation × clinical stakes**, not alphabetical order. Verify P1 first.

### P1 — most likely to have shifted / highest stakes

- [ ] **T1 · §1 General severity** — APACHE I–IV; SAPS I–III; MPM0/II/III; SOFA; LODS; MODS; ODIN; OASIS; ICNARC; TISS-28/76; NEMS; NAS; POSSUM/P-POSSUM; SMR. _(Focus: era calibration, any post-2020 recalibration or successor model.)_
- [ ] **T2 · §2 Early warning** — NEWS/NEWS2; MEWS; ViEWS; Rothman; eCART; TREWScore; SWIFT. _(Focus: NEWS2 currency + RCT evidence on EHR EW tools.)_
- [ ] **T3 · §5 Respiratory (remaining)** — Murray LIS; P/F; SF; OI/OSI; RSBI; ROX; HACOR; CPIS; CURB-65/CRB-65; PSI/PORT; SMART-COP; 4C; PESI/sPESI. _(Berlin row already `superseded` — done.)_
- [ ] **T4 · §6 Cardiovascular/shock** — Killip; Forrester; TIMI; GRACE; HEART; SCAI SHOCK; VIS; CPO; CHA₂DS₂-VASc/HAS-BLED; Wells/Geneva; EuroSCORE II/STS; INTERMACS; Aldrete. _(Focus: SCAI SHOCK 2022 update; GRACE/HEART guideline status.)_
- [ ] **T5 · §20 Pediatric/neonatal (remaining)** — PRISM III/IV; PIM2/PIM3; PELOD-2; pSOFA; APGAR; SNAP/SNAPPE-II; CRIB/CRIB-II; Westley; COMFORT-B. _(Phoenix row done; check pSOFA standing post-Phoenix.)_
- [ ] **T6 · §22 ECMO** — RESP; SAVE; PRESERVE; PRESET/ECMOnet. _(Focus: post-2020 recalibration, ELSO positioning.)_
- [ ] **T7 · §8 Renal (remaining)** — Cleveland Clinic score. _(RIFLE/AKIN/KDIGO done; re-verify KDIGO when 2026 final publishes.)_

### P2 — moderate change probability

- [ ] **T8 · §3 Sepsis (remaining)** — MEDS; PIRO; LRINEC. _(SIRS/qSOFA/SOFA/Phoenix done.)_
- [ ] **T9 · §4 Neurologic** — GCS/GCS-P; FOUR; NIHSS; ASPECTS; Hunt & Hess; WFNS; Fisher/mod-Fisher; ICH; Marshall/Rotterdam; IMPACT/CRASH; GOS/GOSE; mRS; CPC; CAM-ICU; ICDSC; Spetzler-Martin.
- [ ] **T10 · §7 Hepatic (remaining)** — Child-Pugh; King's College; CLIF-SOFA/CLIF-C ACLF; Maddrey DF; Lille; GAHS; ALBI. _(MELD/PELD done.)_
- [ ] **T11 · §9 Coagulation** — ISTH overt DIC; JAAM DIC; 4Ts; HAS-BLED/ORBIT/ATRIA; Caprini/Padua/IMPROVE; PLASMIC; HScore.
- [ ] **T12 · §17 GI** — Ranson; Glasgow-Imrie; BISAP; CTSI/Balthazar; Marshall (mod.); Glasgow-Blatchford; Rockall; AIMS65; Forrest.
- [ ] **T13 · §18 Obstetric** — MEOWS; omSOFA/omqSOFA; SOS; HELLP.
- [ ] **T14 · §21 Cardiac arrest** — CPC; OHCA; CAHP; rCAST.

### P3 — stable anatomic/clinical scales, low change probability (verify last)

- [ ] **T15 · §10 Trauma** — AIS; ISS/NISS; RTS; TRISS; ASCOT; Shock Index; ABC/TASH; MGAP/GAP; MESS; AAST OIS.
- [ ] **T16 · §11 Burns** — TBSA; Baux/revised Baux; ABSI; BOBI.
- [ ] **T17 · §12 Sedation/pain/delirium** — RASS; SAS; Ramsay; MAAS; BIS; CPOT; BPS; NRS/VAS; CAM-ICU/ICDSC.
- [ ] **T18 · §13 Withdrawal** — CIWA-Ar; CINA; COWS/SOWS; WAT-1.
- [ ] **T19 · §14 Nutrition** — NUTRIC/mNUTRIC; NRS-2002; SGA; MUST.
- [ ] **T20 · §15 Frailty/function** — CFS; IMS; FSS-ICU; CPAx; MRC sum; Barthel/Katz.
- [ ] **T21 · §16 Pressure injury** — Braden; Norton; Waterlow.
- [ ] **T22 · §19 Airway** — Mallampati; Cormack-Lehane; LEMON; MACOCHA; Wilson/El-Ganzouri.
- [ ] **T23 · §23 Toxicology** — PSS; King's College (paracetamol); Rumack-Matthew.
- [ ] **T24 · §24 Long-term/QoL** — GOSE/mRS/CPC; EQ-5D, SF-36.

---

## 4. Milestones → SemVer (single repo version line)

One version line for the whole repo (reference + tooling + calculable platform).
Two tracks advance **within** it: the **verification ratchet** (lower `unverified`)
and **calculable coverage** (encode verified scores). The calculable-track DoD and
backlog are in §5b.

| Release | Trigger | Verification (ceiling) | Calculable scores |
| ------- | ------- | ---------------------- | ----------------- |
| 0.2.0 (done) | Reference + citation gate live | 161 (11 verified) | — |
| **0.3.0 (done)** | Calculable platform: schema, dual engine, contract gate, SPA, CI/Pages | 161 (held) | 4 (qSOFA, SIRS, P/F-ARDS, KDIGO AKI) |
| 0.3.x | each verified batch merged; encode cleared scores | lowered per batch | grows with verified count |
| 0.4.0 | all **P1** domains verified (+ P1 scores calculable) | ~ P1 verified | P1 |
| 0.5.0 | **P1 + P2** verified | ~ | P2; shareable URLs (no PHI server-side) |
| 1.0.0 | **all** rows verified, `--check-dois` green | **0** | all currently-verifiable |
| post-1.0 | mobile (React Native) reusing TS engine + `scores/*.json` | — | next major track |

Rule: the ratchet may only go **down**; a release bump requires a green
`verify-scores` run. The 0.3.0 platform release **held** the ceiling at 161
(no rows verified in it) — ratchet lowering resumes at 0.3.x.

---

## 5. Progress ledger

| Date       | Batch                                                          | Rows verified | unverified after | Ceiling set | Doc ver |
| ---------- | -------------------------------------------------------------- | ------------- | ---------------- | ----------- | ------- |
| 2026-06-01 | Initial deltas (ARDS, sepsis, peds-sepsis, hepatic-alloc, AKI) | 11            | 161              | 161         | 0.2.0   |
|            |                                                                |               |                  |             |         |

---

## 5b. Calculable-scores track (web/mobile) — DoD & backlog

The **calculation contract** (`tools/verify_definitions.py`) requires each
`scores/*.json` to pass schema + reference resolution + golden vectors reproduced
by **both** engines. A score is exposed in the calculator only after it passes the
citation contract **and** the calculation contract. Release versions for this track
live in the unified table in §4. SDLC framing: see [`docs/`](docs/)
(12207 / IEC 62304 / ISO 14971).

**DoD per definition:** (a) score is citation-verified in `SCORES.md`; (b) ≥1 golden
vector from the primary publication; (c) green `verify_definitions.py` + `pytest`
(Python) + `vitest` (TS).

**Backlog** (next definitions — add/verify the citation first): SOFA, GCS, NEWS2,
MELD 3.0 (R5 — cross-check the formula vs the OPTN worked example before trusting
the golden vector), CURB-65.

---

## 6. Known re-verification triggers (watch list)

- [ ] **KDIGO 2026 AKI/AKD** final publication → re-verify §8 KDIGO row (currently `current` on the 2012 guideline; 2026 draft in review through 2026-05-11).
- [ ] **SSC** next adult guideline cycle → re-check §3 qSOFA `contested` status.
- [ ] **New Global Definition of ARDS** prospective validation studies → may move §5 Berlin note from "predecessor" to fully retired.
