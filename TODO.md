# TODO — Score Currency Verification (`SCORES.md`)

**Companion to:** `SCORES.md` v0.2.0 · **TODO version:** 0.1.0 · **Created:** 2026-06-01

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

## 2. CI enforcement (the mechanism)

`verify_scores.py` is the gate. Wire it so the build is red on any contract breach.

- [ ] Add to repo root with the reference file.
- [ ] Pin baseline ceiling to current count (**161**) and lower it with every merged batch.
- [ ] `.github/workflows/verify-scores.yml`:

```yaml
name: verify-scores
on: [pull_request, push]
jobs:
  contract:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - name: Enforce score-currency contract
        run: uv run verify_scores.py SCORES.md --max-unverified 161
      - name: Resolve all cited DOIs (nightly / pre-tag)
        if: github.event_name == 'push'
        run: uv run verify_scores.py SCORES.md --max-unverified 161 --check-dois
```

- [ ] Branch protection: require `verify-scores / contract` green before merge.
- [ ] On each domain batch merge: decrement `--max-unverified` in the workflow to the new actual count (the ratchet — it can only go down).
- [ ] Pre-`1.0.0` tag job runs with `--check-dois` and `--max-unverified 0`.

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

## 4. Milestones → SemVer mapping

| Milestone | Trigger                                     | Doc version      | Gate ceiling          |
| --------- | ------------------------------------------- | ---------------- | --------------------- |
| M0 (done) | v0.2.0 shipped; gate live                   | 0.2.0            | 161                   |
| M1        | each domain batch merged                    | 0.2.x patch each | lowered to new actual |
| M2        | all **P1** domains done                     | 0.3.0            | ~ verified count      |
| M3        | **P1 + P2** done                            | 0.4.0            | ~                     |
| M4        | **all** rows verified, `--check-dois` green | **1.0.0**        | **0**                 |

Rule: a doc version bump requires a green `verify-scores` run at the **new** ceiling. No bump without a lowered ratchet.

---

## 5. Progress ledger

| Date       | Batch                                                          | Rows verified | unverified after | Ceiling set | Doc ver |
| ---------- | -------------------------------------------------------------- | ------------- | ---------------- | ----------- | ------- |
| 2026-06-01 | Initial deltas (ARDS, sepsis, peds-sepsis, hepatic-alloc, AKI) | 11            | 161              | 161         | 0.2.0   |
|            |                                                                |               |                  |             |         |

---

## 5b. Calculable-scores track (web/mobile platform)

A parallel ratchet to the citation contract: the **calculation contract**
(`tools/verify_definitions.py`) requires each `scores/*.json` to pass schema +
reference resolution + golden vectors reproduced by **both** engines. A score is only
exposed in the calculator once it passes the citation contract **and** the calculation
contract. See [`docs/`](docs/) for the SDLC framing (12207 / IEC 62304 / ISO 14971).

| Milestone | Trigger | Doc version | Calculable scores |
| --------- | ------- | ----------- | ----------------- |
| C0 (done) | schema + dual engine + contract gate + SPA + CI/Pages | 0.3.0 | 4 (qSOFA, SIRS, P/F-ARDS, KDIGO AKI) |
| C1 | encode each verified score as it clears the citation gate | 0.3.x | grows with verified count |
| C2 | all P1 verified scores calculable | 0.4.0 | ~ |
| C3 | mobile (React Native) reusing TS engine + `scores/*.json` | — | next major track |

Rule: a new `scores/*.json` requires (a) the score is citation-verified in `SCORES.md`,
(b) ≥1 golden vector from the primary publication, (c) green `verify_definitions.py` +
green `pytest` (Python) + green `vitest` (TS). DoD per definition = all three.

Backlog (next definitions, pull from already-verified rows / add references first):
SOFA (needs ref), GCS (needs ref), NEWS2 (needs ref), MELD 3.0 (R5 — cross-check formula
vs OPTN worked example before trusting the golden vector), CURB-65 (needs ref).

---

## 6. Known re-verification triggers (watch list)

- [ ] **KDIGO 2026 AKI/AKD** final publication → re-verify §8 KDIGO row (currently `current` on the 2012 guideline; 2026 draft in review through 2026-05-11).
- [ ] **SSC** next adult guideline cycle → re-check §3 qSOFA `contested` status.
- [ ] **New Global Definition of ARDS** prospective validation studies → may move §5 Berlin note from "predecessor" to fully retired.
