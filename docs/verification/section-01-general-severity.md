# §1 General ICU severity — Verification findings (Task 1.1)

**Status:** APPLIED — signed off 2026-06-14; dispositions written to `SCORES.md`, References R8–R23 added, CI ratchet lowered 161 → 148, both gates (incl. `--check-dois`) green.
**Date:** 2026-06-02 (proposal) · 2026-06-14 (applied) · **Tier:** P1 / T1 (`TODO.md §3`) · **Section:** SCORES.md §1 (14 rows)

> Working review artifact, now committed. Sign-off decisions: APACHE → `contested`,
> SAPS → `current`, ODIN → hold `unverified`; all other rows applied per the recommended
> dispositions below. 13 rows verified, ODIN held.

## Method

- Per the `TODO.md §1` protocol: source hierarchy (governing body → current guideline →
  primary derivation + recent external validation → living review), status decision rule,
  and the anti-pattern refusals (no "current from memory"; no MDCalc/UpToDate as primary).
- Sources retrieved via PubMed + web (3 parallel research passes). **Disposition (the status
  call) is mine**, to be ratified by you — "discovery fetches, verification disposes."
- **Every DOI below was confirmed to resolve** through the DOI Handle System API
  (`tools/verify_scores.py:check_doi_resolves`) — the same blocking check CI runs. 20/20 OK.

---

## Proposed statuses (your Decision column is blank)

| # | Row | Proposed status | Key ref | Confidence | Decision (you) |
|---|-----|-----------------|---------|------------|----------------|
| 1 | APACHE I–IV | `contested` ⚠️ | R8, R9 | high | |
| 2 | SAPS I–III | `current` ⚠️ | R10, R9 | high | |
| 3 | MPM0/II/III | `current` | R11 | medium | |
| 4 | SOFA | `current` | R12 | high | |
| 5 | LODS | `current` ⚠️ | R13 | medium | |
| 6 | MODS | `current` ⚠️ | R14 | medium | |
| 7 | ODIN | **hold `unverified`** ⚠️ | — (R22 if verified) | medium | |
| 8 | OASIS | `current` | R15, R23 | high | |
| 9 | ICNARC model | `current` | R16 | high | |
| 10 | TISS-28 / TISS-76 | `superseded` | R17 | high | |
| 11 | NEMS | `current` | R18 | medium | |
| 12 | NAS | `current` | R19 | high | |
| 13 | POSSUM / P-POSSUM | `current` | R20 | high | |
| 14 | SMR | `current` (annotate as output metric) ⚠️ | R21 | medium | |

⚠️ = judgment call I'd like you to rule on (see "Judgment calls" below).

**Ratchet:** approve leans as-is (13 verified, ODIN held) → ceiling **161 → 148**.
Also verify ODIN → **161 → 147**.

---

## Judgment calls (clinical — yours to decide)

- **APACHE → `contested` vs `current`.** Cox 2022 (R9) multicentre validation shows **preserved
  discrimination but poor calibration / mortality overestimation** in modern cohorts, with no
  governing-body replacement. The decision rule → `contested`. Defensible alternative: keep
  `current` (still the standard benchmark; drift handled by recalibration).
- **SAPS symmetry.** SAPS 3 sits on the *same* Cox 2022 drift finding but is proposed `current`
  because SAPS 3 ships built-in regional recalibration equations and some cohorts calibrate well
  (PeerJ 2021). If you rule APACHE `contested`, decide whether consistency makes SAPS `contested`
  too, or whether the built-in recalibration genuinely distinguishes them.
- **MPM** — `current` but **low confidence**: thin recent uptake, one Rwanda miscalibration;
  could be `contested`.
- **LODS / MODS** — validated, no replacement, but **largely research-use** now. `current` is
  defensible; alternative is to annotate "research-only" or hold.
- **ODIN** — single-centre 1993 model, **never externally validated, no authority named a
  successor**. `superseded` would overclaim (the rule needs a *designating* source). I recommend
  **leaving it `unverified`** this pass. Alternative: mark `superseded` (legacy).
- **SMR** — not a bedside score; a benchmarking *output* (O/E deaths) with documented case-mix /
  transfer bias. Mark `current` as a still-used metric (annotated), or treat as "not-a-score"?

---

## Proposed References (R8–R21) — all DOIs resolve ✓

- **R8** — Zimmerman JE, Kramer AA, McNair DS, Malila FM. *Acute Physiology and Chronic Health Evaluation (APACHE) IV: hospital mortality assessment for today's critically ill patients.* Crit Care Med. 2006. DOI: https://doi.org/10.1097/01.CCM.0000215112.84523.F0 (PMID 16540951)
- **R9** — Cox EGM, et al. *External validation of ICU mortality-prediction models (SICS-I + FINNAKI cohorts).* Crit Care Med. 2022. DOI: https://doi.org/10.1097/CCM.0000000000005712 (PMID 36378565) — _currency evidence for APACHE & SAPS: discrimination preserved, calibration poor pre-recalibration._
- **R10** — Moreno RP, Metnitz PGH, Almeida E, et al. *SAPS 3 — Part 2: development of a prognostic model for hospital mortality at ICU admission.* Intensive Care Med. 2005. DOI: https://doi.org/10.1007/s00134-005-2763-5 (PMID 16132892). _Predecessor SAPS II: Le Gall JR, Lemeshow S, Saulnier F. JAMA. 1993. DOI: https://doi.org/10.1001/jama.270.24.2957 (PMID 8254858)._
- **R11** — Higgins TL, Kramer AA, Nathanson BH, et al. *Prospective validation of the ICU admission Mortality Probability Model (MPM0-III).* Crit Care Med. 2009. DOI: https://doi.org/10.1097/CCM.0b013e31819ded31 (PMID 19325480)
- **R12** — Vincent JL, Moreno R, Takala J, et al. *The SOFA (Sepsis-related Organ Failure Assessment) score to describe organ dysfunction/failure.* Intensive Care Med. 1996. DOI: https://doi.org/10.1007/BF01709751 (PMID 8844239)
- **R13** — Le Gall JR, Klar J, Lemeshow S, et al. *The Logistic Organ Dysfunction system.* JAMA. 1996. DOI: https://doi.org/10.1001/jama.276.10.802 (PMID 8769590)
- **R14** — Marshall JC, Cook DJ, Christou NV, et al. *Multiple organ dysfunction score: a reliable descriptor of a complex clinical outcome.* Crit Care Med. 1995. DOI: https://doi.org/10.1097/00003246-199510000-00007 (PMID 7587228)
- **R15** — Johnson AEW, Kramer AA, Clifford GD. *A new severity of illness scale using a subset of Acute Physiology And Chronic Health Evaluation data elements shows comparable predictive accuracy.* Crit Care Med. 2013. DOI: https://doi.org/10.1097/CCM.0b013e31828a24fe (PMID 23660729) — _the Oxford Acute Severity of Illness Score (OASIS); title verbatim per PubMed._
- **R16** — Harrison DA, Parry GJ, Carpenter JR, Short A, Rowan K. *A new risk prediction model for critical care: the ICNARC model.* Crit Care Med. 2007. DOI: https://doi.org/10.1097/01.CCM.0000259468.24532.44 (PMID 17334248). _Currency: ICNARC maintains the live **ICNARCH-2023** model (Case Mix Programme, 2024)._
- **R17** — Miranda DR, de Rijk A, Schaufeli W. *Simplified Therapeutic Intervention Scoring System: the TISS-28 items.* Crit Care Med. 1996. DOI: https://doi.org/10.1097/00003246-199601000-00012. _Lineage: TISS-76 (obsolete) → TISS-28 → NEMS → NAS._
- **R18** — Reis Miranda D, Moreno R, Iapichino G. *Nine equivalents of nursing manpower use score (NEMS).* Intensive Care Med. 1997. DOI: https://doi.org/10.1007/s001340050406
- **R19** — Miranda DR, Nap R, de Rijk A, Schaufeli W, Iapichino G. *Nursing activities score.* Crit Care Med. 2003. DOI: https://doi.org/10.1097/01.CCM.0000045567.78801.CC. _Currency: Li L, Zou X, Chen H. Workload in ICU nurses: systematic review & meta-analysis of NAS. Intensive Crit Care Nurs. 2025;91:104086. DOI: https://doi.org/10.1016/j.iccn.2025.104086._
- **R20** — Copeland GP, Jones D, Walters M. *POSSUM: a scoring system for surgical audit.* Br J Surg. 1991. DOI: https://doi.org/10.1002/bjs.1800780327. _P-POSSUM: Prytherch DR, Whiteley MS, Higgins B, et al. Br J Surg. 1998. DOI: https://doi.org/10.1046/j.1365-2168.1998.00840.x. Currency: embedded in UK NELA (Year 9 report, RCoA 2024)._
- **R21** — Kahn JM, Kramer AA, Rubenfeld GD. *Transferring critically ill patients out of hospital improves the standardized mortality ratio: a simulation study.* Chest. 2007. DOI: https://doi.org/10.1378/chest.06-0741
- **(R22 — only if ODIN verified)** — Fagon JY, Chastre J, Novara A, Medioni P, Gibert C. *Characterization of ICU patients using a model based on organ dysfunctions and/or infection: the ODIN model.* Intensive Care Med. 1993. DOI: https://doi.org/10.1007/BF01720528 (PMID 8315120)
- **R23** — Zou J, Chen H, Liu C, et al. *Development and validation of a nomogram to predict the 30-day mortality risk of patients with intracerebral hemorrhage.* Front Neurosci. 2022;16:942100. DOI: https://doi.org/10.3389/fnins.2022.942100 (PMID 36033629) — _OASIS currency: applied as a comparator severity score on a contemporary MIMIC-III ICU cohort; validation-cohort OASIS AUC 0.728. Source: PubMed. DOI resolves ✓ (Handle System API)._

---

## Per-row evidence (audit trail)

### 1. APACHE I–IV → `contested`
- Primary: Zimmerman 2006 (R8). APACHE IV is the current operative model; APACHE II (1985) most-cited legacy.
- Currency: Cox 2022 (R9) — among 43 models APACHE IV had top-tier discrimination (scaled Brier 0.10) but **poor calibration before recalibration**; derivation paper itself notes APACHE overestimates as model ages.
- Rationale: tier-3 — active use + documented calibration failure, no governing-body replacement → `contested`.

### 2. SAPS I–III → `current`
- Primary: Moreno 2005, SAPS 3 (R10); predecessor SAPS II 1993.
- Currency: still actively validated/benchmarked (PeerJ 2021 AUC 0.89, good calibration); Cox 2022 (R9) drift handled via built-in customized equations; no "SAPS 4".
- Rationale: tier-3 — operative SAPS instrument, recalibration built in, no dominant validity failure → `current`. (See SAPS-symmetry judgment call.)

### 3. MPM0/II/III → `current` (low conf)
- Primary: Higgins 2009, MPM0-III (R11).
- Currency: mixed — Tanzania PeerJ 2021 good (AUC 0.90); Rwanda PLoS One 2016 poor calibration (HL p=0.024). No successor, no replacement.
- Rationale: tier-3 — operative with no published successor; mixed evidence rather than dominant failure → `current`, but a `contested` case exists.

### 4. SOFA → `current`
- Primary: Vincent 1996 (R12). Currency: Sepsis-3 (Singer 2016) embeds SOFA; criticisms are population-specific (e.g., COVID-19) and drive refinement, not replacement.
- Rationale: tier-1/2 consensus body uses it as the operative organ-dysfunction score → `current`. (Consistent with §3 SOFA = current/R7.)

### 5. LODS → `current` (borderline)
- Primary: Le Gall 1996 (R13); derivation on 13,152 admissions, AUC ~0.85.
- Rationale: tier-3 — validated, no replacement, **largely research-use**; operative within that scope → `current` (borderline).

### 6. MODS → `current` (borderline)
- Primary: Marshall 1995 (R14); AUC ~0.93 derivation/validation.
- Rationale: tier-3 — validated organ-dysfunction descriptor, mostly research use, not superseded → `current` (borderline).

### 7. ODIN → recommend `unverified` (hold)
- Primary: Fagon 1993 (R22 if used). Single-centre (n=1070); authors say it "requires to be validated in other institutions." No external validation / guideline / authority found.
- Rationale: no authoritative currency source; `superseded` overclaims (no designating authority). **Hold `unverified`** is the honest default; alternative `superseded` (legacy).

### 8. OASIS → `current`
- Primary: Johnson 2013 (R15); internal validation set 2010–2011, AUROC 0.88.
- Currency: OASIS remains the de-facto standard ICU severity-score *benchmark* in contemporary database research (MIMIC-IV / eICU / MIMIC-III). Documented currency ref **R23** (Zou 2022) reports OASIS validation-cohort AUC 0.728 on a 2022 MIMIC-III cohort. Note: recent literature uses OASIS predominantly as a comparator baseline rather than as a dedicated external-validation target — continued-use evidence, not a fresh standalone revalidation.
- Rationale: tier-3/4 — operative parsimonious EHR severity score, no successor → `current`.

### 9. ICNARC model → `current`
- Primary: Harrison 2007 (R16). Currency: ICNARC (UK audit authority) maintains the live **ICNARCH-2023** model via serial recalibration (2014→2015→2018→2023).
- Rationale: tier-1 — authority designates the operative model → `current`.

### 10. TISS-28 / TISS-76 → `superseded`
- Primary: Miranda 1996, TISS-28 (R17). Lineage: Cullen 1974 → TISS-76 (obsolete) → TISS-28 → NEMS (1997) → NAS (2003). NAS explains 81% of nursing time vs TISS-28's 43%.
- Rationale: tier-3 — successor (NAS) named by the same authors; TISS-76 obsolete, TISS-28 legacy/cost use → `superseded`.

### 11. NEMS → `current` (medium)
- Primary: Reis Miranda 1997 (R18). Currency: used at ICU/unit level (EURICUS); reviews still list it alongside NAS.
- Rationale: tier-3 — validated macro/unit-level workload tool, distinct niche from patient-level NAS, no replacement → `current`.

### 12. NAS → `current`
- Primary: Miranda 2003 (R19). Currency: 2025 systematic review/meta-analysis (70 studies, 56,042 patients) — the predominant patient-level nursing-workload instrument.
- Rationale: tier-4 living review + tier-3 derivation → `current` (de facto standard).

### 13. POSSUM / P-POSSUM → `current`
- Primary: Copeland 1991 (R20); P-POSSUM Prytherch 1998. Currency: embedded risk-adjustment in UK NELA (Year 9 report, RCoA Oct 2024); 2023 comparative validations treat P-POSSUM as benchmark.
- Rationale: tier-2 audit authority + tier-3 validation → `current` (NELA-specific model coexists, doesn't retire it).

### 14. SMR → `current` (annotate as output metric)
- Primary/method: Kahn 2007 (R21). SMR = O/E deaths from a calibrated severity model; methodologically fragile (transfer/case-mix bias can shift SMR >0.1).
- Rationale: not a bedside instrument; still-used, definitionally stable benchmarking output. Mark `current` + annotate as "output metric, not a score," noting bias caveats. (Or treat as not-a-score — your call.)

---

## Sign-off

- [x] Approve all 6 high-confidence rows (SOFA, OASIS, ICNARC, NAS, POSSUM, TISS).
- [x] APACHE: **`contested`** ✅
- [x] SAPS: **`current`** ✅
- [x] MPM: **`current`** ✅
- [x] LODS / MODS: **`current`** ✅
- [x] ODIN: **hold `unverified`** ✅
- [x] SMR: **`current`** + annotate as output metric ✅
- [x] NEMS: **`current`** ✅
- [x] OASIS currency strengthened with R23 (Zou 2022, MIMIC-III validation AUC 0.728).

**Decided by:** Kresna Sucandra  **Date:** 2026-06-14

Applied: 13 §1 rows verified (ODIN held `unverified`), References R8–R23 added to `SCORES.md`,
CI ceiling lowered 161 → 148, contract + `--check-dois` gates green. Plans 1.1 → done.
