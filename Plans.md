# critical-care-scores Plans.md

Created: 2026-06-02 · Synced with [`TODO.md`](TODO.md): 2026-06-02

> Execution tracker for the single repo SemVer line (see [`TODO.md` §4](TODO.md)).
> `TODO.md §3` (T1–T24) is the **atomic** verification backlog SSOT; each row below
> tracks one tier or milestone. Markers: `cc:TODO` · `cc:wip` · `cc:done` · `blocked`.

---

## Phase 0 — Release 0.3.0: Calculable platform (done)

| Task | Description | DoD | Depends | Status |
|------|-------------|-----|---------|--------|
| 0.1 | Score-definition JSON Schema (`schema/score.schema.json`) | Draft 2020-12 schema validates every `scores/*.json` | - | cc:done |
| 0.2 | Python reference engine (`engine/ccscores`) | `pytest engine/tests` green; safe formula AST, no `eval` | 0.1 | cc:done |
| 0.3 | TypeScript engine + React/Vite SPA (`web/`) | `vitest` reproduces same golden vectors; typecheck + build green | 0.1, 0.2 | cc:done |
| 0.4 | Calculation contract gate (`tools/verify_definitions.py`) | Exit 1 on schema/ref/vector breach; exit 0 on valid set | 0.1, 0.2 | cc:done |
| 0.5 | Pilot definitions (qSOFA, SIRS, P/F-ARDS, KDIGO AKI) | 4 scores pass citation + calculation contracts | 0.4 | cc:done |
| 0.6 | Web references display (DOI links + band source) | Selected score shows full citations w/ clickable DOI; band links to its ref | 0.3, 0.5 | cc:done |
| 0.7 | CI/CD pipeline + GitHub Pages deploy | `verify`+`deploy` green; site live at sha888.github.io/critical-care-scores | 0.4 | cc:done |
| 0.8 | Harden DOI check (DOI Handle System API) | `--check-dois` blocking + green via `responseCode` | 0.7 | cc:done |
| 0.9 | CI on Node-24 action majors | checkout@v6, setup-node@v6, setup-uv@v7, upload-pages-artifact@v5, deploy-pages@v5; no deprecation warnings | 0.7 | cc:done |
| 0.10 | Reconcile docs to single repo SemVer line (0.3.0) | No version collision across README/TODO/SCORES.md; contracts green | - | cc:done |

---

## Phase 1 — Release 0.3.x → 0.4.0: P1 verification + encode (TODO §3 P1, §5b)

DoD pattern per verify task: every row in the tier set to `current`/`superseded`/`contested`
with ≥1 `R#` resolving in References; `--max-unverified` lowered to the new actual; `verify-scores` green.

| Task | Description | DoD | Depends | Status |
|------|-------------|-----|---------|--------|
| 1.1 | Verify §1 General severity — TODO T1 (APACHE/SAPS/SOFA/MODS/…) | tier verified + ratchet lowered + gate green | - | cc:done |
| 1.2 | Verify §2 Early warning — T2 (NEWS2/MEWS/ViEWS/…) | tier verified + ratchet lowered + gate green | - | cc:TODO |
| 1.3 | Verify §5 Respiratory remaining — T3 (Murray/P-F/CURB-65/PSI/4C/…) | tier verified + ratchet lowered + gate green | - | cc:TODO |
| 1.4 | Verify §6 Cardiovascular/shock — T4 (GRACE/HEART/SCAI SHOCK/Wells/…) | tier verified + ratchet lowered + gate green | - | cc:TODO |
| 1.5 | Verify §20 Pediatric/neonatal remaining — T5 (PRISM/PIM/pSOFA/APGAR/…) | tier verified + ratchet lowered + gate green | - | cc:TODO |
| 1.6 | Verify §22 ECMO — T6 (RESP/SAVE/PRESERVE/PRESET) | tier verified + ratchet lowered + gate green | - | cc:TODO |
| 1.7 | Verify §8 Renal remaining — T7 (Cleveland Clinic score) | tier verified + ratchet lowered + gate green | - | cc:TODO |
| 1.8 | Encode cleared P1 scores as `scores/*.json` (SOFA, GCS, NEWS2, CURB-65, MELD 3.0) | each passes calc contract; golden vectors from primary source; both engines green `[tdd:required]` | 1.1, 1.2, 1.3, 1.4 | cc:TODO |
| 1.9 | Tag release 0.4.0 | P1 verified + P1 scores calculable; all gates green | 1.1, 1.7, 1.8 | cc:TODO |

---

## Phase 2 — Release 0.5.0: P2 verification (TODO §3 P2)

| Task | Description | DoD | Depends | Status |
|------|-------------|-----|---------|--------|
| 2.1 | Verify §3 Sepsis remaining — T8 (MEDS/PIRO/LRINEC) | tier verified + ratchet lowered + gate green | - | cc:TODO |
| 2.2 | Verify §4 Neurologic — T9 (GCS/FOUR/NIHSS/ICH/CAM-ICU/…) | tier verified + ratchet lowered + gate green | - | cc:TODO |
| 2.3 | Verify §7 Hepatic remaining — T10 (Child-Pugh/King's/CLIF-C/ALBI/…) | tier verified + ratchet lowered + gate green | - | cc:TODO |
| 2.4 | Verify §9 Coagulation — T11 (ISTH DIC/4Ts/HAS-BLED/Padua/PLASMIC/…) | tier verified + ratchet lowered + gate green | - | cc:TODO |
| 2.5 | Verify §17 GI — T12 (Ranson/BISAP/Blatchford/Rockall/AIMS65/…) | tier verified + ratchet lowered + gate green | - | cc:TODO |
| 2.6 | Verify §18 Obstetric — T13 (MEOWS/omSOFA/SOS/HELLP) | tier verified + ratchet lowered + gate green | - | cc:TODO |
| 2.7 | Verify §21 Cardiac arrest — T14 (CPC/OHCA/CAHP/rCAST) | tier verified + ratchet lowered + gate green | - | cc:TODO |
| 2.8 | Shareable result URLs (querystring state, no PHI server-side) | URL encodes inputs; DevTools confirms no network call carries inputs | Phase 1 | cc:TODO |
| 2.9 | Tag release 0.5.0 | P1+P2 verified; all gates green | 2.1, 2.7 | cc:TODO |

---

## Phase 3 — Release 1.0.0: P3 verification + final gate (TODO §3 P3, §4)

| Task | Description | DoD | Depends | Status |
|------|-------------|-----|---------|--------|
| 3.1 | Verify §10 Trauma — T15 (ISS/RTS/TRISS/Shock Index/…) | tier verified + ratchet lowered + gate green | - | cc:TODO |
| 3.2 | Verify §11 Burns — T16 (TBSA/Baux/ABSI/BOBI) | tier verified + ratchet lowered + gate green | - | cc:TODO |
| 3.3 | Verify §12 Sedation/pain/delirium — T17 (RASS/SAS/CPOT/BPS/…) | tier verified + ratchet lowered + gate green | - | cc:TODO |
| 3.4 | Verify §13 Withdrawal — T18 (CIWA-Ar/CINA/COWS/WAT-1) | tier verified + ratchet lowered + gate green | - | cc:TODO |
| 3.5 | Verify §14 Nutrition — T19 (NUTRIC/NRS-2002/SGA/MUST) | tier verified + ratchet lowered + gate green | - | cc:TODO |
| 3.6 | Verify §15 Frailty/function — T20 (CFS/FSS-ICU/MRC sum/Barthel/…) | tier verified + ratchet lowered + gate green | - | cc:TODO |
| 3.7 | Verify §16 Pressure injury — T21 (Braden/Norton/Waterlow) | tier verified + ratchet lowered + gate green | - | cc:TODO |
| 3.8 | Verify §19 Airway — T22 (Mallampati/Cormack-Lehane/LEMON/MACOCHA/…) | tier verified + ratchet lowered + gate green | - | cc:TODO |
| 3.9 | Verify §23 Toxicology — T23 (PSS/King's paracetamol/Rumack-Matthew) | tier verified + ratchet lowered + gate green | - | cc:TODO |
| 3.10 | Verify §24 Long-term/QoL — T24 (GOSE/mRS/CPC/EQ-5D/SF-36) | tier verified + ratchet lowered + gate green | - | cc:TODO |
| 3.11 | 1.0.0 release gate | `unverified == 0` AND `verify_scores.py SCORES.md --max-unverified 0 --check-dois` green; tag 1.0.0 | 3.1-3.10 | cc:TODO |

---

## Phase 4 — Post-1.0: Mobile

| Task | Description | DoD | Depends | Status |
|------|-------------|-----|---------|--------|
| 4.1 | Mobile app (React Native) reusing TS engine + `scores/*.json` | App computes via shared engine; golden vectors green on device | 3.11 | cc:TODO |

---

## Standing watch (TODO §6 re-verification triggers)

| Task | Description | DoD | Depends | Status |
|------|-------------|-----|---------|--------|
| W.1 | KDIGO 2026 AKI/AKD final → re-verify §8 KDIGO row + `kdigo-aki.json` | re-checked against published 2026 guideline; gate green | - | cc:TODO |
| W.2 | SSC next adult guideline cycle → re-check §3 qSOFA `contested` | status re-confirmed/updated w/ ref; gate green | - | cc:TODO |
| W.3 | New Global Definition of ARDS prospective validation → §5 Berlin note | note updated; `pf-ratio.json` re-checked | - | cc:TODO |
