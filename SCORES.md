# Scoring Systems in Critical Care Medicine — A Domain-Organized Reference

**Version:** 0.3.0 · **Updated:** 2026-06-02 · **Supersedes:** 0.2.0

## Changelog

### 0.3.0 — 2026-06-02

- Repo adopts a **single SemVer line** (reference + tooling + calculable platform share one version); this document no longer carries a version number separate from the repo. See [`TODO.md` §4](TODO.md).
- Added the calculable-score platform (JSON definitions, dual engine, web calculator). **No row, `Status`, or `Key ref` changes** in this revision — reference content is unchanged from 0.2.0.

### 0.2.0 — 2026-06-01

- Appended two columns to every table: `Status` (2026 currency) and `Key ref`.
- Every row defaults to `unverified` — a _citation-check-pending_ flag, **not** a claim of invalidity. The count of `unverified` rows is the project's verification debt (see [`TODO.md`](TODO.md)).
- Verified and annotated this revision: ARDS/Berlin (§5), sepsis SIRS/qSOFA/SOFA (§3), pediatric sepsis Phoenix (§3, §20), hepatic allocation MELD/PELD (§7), AKI RIFLE/AKIN/KDIGO (§8).
- v0.1.0 `Score` / `Full name` / `Purpose` cell text preserved **verbatim**; only columns appended and front-matter added.

### 0.1.0 — initial

- Domain-organized enumeration across 24 sections; no currency annotation.

## Status legend

| Token        | Meaning                                                                 |
| ------------ | ----------------------------------------------------------------------- |
| `current`    | Verified this revision as the operative/recommended instrument in 2026. |
| `superseded` | Verified replaced by a newer instrument (named in the row note / ref).  |
| `contested`  | Verified still in use but with documented validity dispute.             |
| `unverified` | Default. No citation check run this revision. NOT an invalidity claim.  |

> **Machine-readable contract (CI-enforced):**
>
> 1. A row may carry `current` / `superseded` / `contested` **only if** `Key ref` is non-empty.
> 2. An `unverified` row **must** have `Key ref` = `—`.
> 3. Every `Key ref` code (`R#`) must resolve to an entry in **References**, and every DOI there must return HTTP 200.
> 4. `Status` must be one of the four legend tokens.
> 5. The `unverified` count is a monotonic ratchet — a PR may only lower it. `1.0.0` requires `unverified == 0`.

---

> **Scope note.** "All scores" is an open set: the literature holds hundreds of validated, proposed, and locally-derived instruments, and ML-derived scores are added continuously. This document enumerates the clinically operative set an intensivist works with, plus the major disease-specific scores that intersect ICU practice. Treat it as comprehensive-by-domain, not exhaustive-by-count. Years and authorship are given where they aid identification; exact point cutoffs are deliberately omitted in favor of _what each instrument is for and what it consumes_, since cutoffs are where transcription errors hide — confirm those against the original publication or a calculator before bedside use.

---

## 1. General ICU severity-of-illness / mortality prediction

| Score             | Full name                                                                             | Purpose / inputs                                                                                                                                                      | Status     | Key ref |
| ----------------- | ------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------- | ------- |
| APACHE I–IV       | Acute Physiology and Chronic Health Evaluation                                        | ICU mortality prediction; worst physiology in first 24 h + age + chronic health. APACHE II (1985) remains the most cited; III/IV add diagnosis-specific coefficients. | contested  | R8, R9  |
| SAPS I–III        | Simplified Acute Physiology Score                                                     | Mortality prediction; SAPS II (1993) uses 17 variables; SAPS 3 (2005) uses admission data + global recalibration.                                                     | current    | R10, R9 |
| MPM0/II/III       | Mortality Probability Model                                                           | Logistic mortality probability at admission (MPM0), 24/48/72 h; fewer physiologic variables than APACHE.                                                              | current    | R11     |
| SOFA              | Sequential (originally Sepsis-related) Organ Failure Assessment                       | Organ-dysfunction severity across 6 systems (resp, coag, hepatic, CV, CNS, renal); trended daily; backbone of Sepsis-3.                                               | current    | R12     |
| LODS              | Logistic Organ Dysfunction System                                                     | Organ-dysfunction severity, logistic-derived weighting across 6 systems.                                                                                              | current    | R13     |
| MODS              | Multiple Organ Dysfunction Score                                                      | Organ dysfunction quantification (Marshall 1995); CV term uses pressure-adjusted heart rate.                                                                          | current    | R14     |
| ODIN              | Organ Dysfunctions and/or Infection                                                   | Early organ-dysfunction + infection descriptor.                                                                                                                       | unverified | —       |
| OASIS             | Oxford Acute Severity of Illness Score                                                | Parsimonious mortality model derived for EHR/automated extraction.                                                                                                    | current    | R15, R23|
| ICNARC model      | Intensive Care National Audit & Research Centre model                                 | UK risk-adjustment mortality model.                                                                                                                                   | current    | R16     |
| TISS-28 / TISS-76 | Therapeutic Intervention Scoring System                                               | Workload/resource intensity by counting interventions.                                                                                                                | superseded | R17     |
| NEMS              | Nine Equivalents of Nursing Manpower use Score                                        | Simplified workload measure derived from TISS.                                                                                                                        | current    | R18     |
| NAS               | Nursing Activities Score                                                              | Nursing workload, broader than NEMS.                                                                                                                                  | current    | R19     |
| POSSUM / P-POSSUM | Physiological and Operative Severity Score for enUmeration of Mortality and morbidity | Surgical risk-adjusted morbidity/mortality.                                                                                                                           | current    | R20     |
| SMR               | Standardized Mortality Ratio                                                          | Observed/expected deaths — a benchmarking output of the models above, not a bedside score.                                                                            | current    | R21     |

---

## 2. Early warning / track-and-trigger (deterioration on wards / pre-ICU)

| Score         | Full name                                 | Purpose / inputs                                                                                                                                | Status     | Key ref |
| ------------- | ----------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- | ---------- | ------- |
| NEWS / NEWS2  | National Early Warning Score              | Aggregate vitals (RR, SpO2, O2 use, temp, SBP, HR, consciousness); NEWS2 adds new-onset confusion and a second SpO2 scale for hypercapnic risk. | unverified | —       |
| MEWS          | Modified Early Warning Score              | Predecessor aggregate-vitals trigger.                                                                                                           | unverified | —       |
| ViEWS         | VitalPAC Early Warning Score              | Empirical antecedent to NEWS.                                                                                                                   | unverified | —       |
| Rothman Index | —                                         | Continuous EHR-derived acuity (vitals, labs, nursing assessments).                                                                              | unverified | —       |
| eCART         | electronic Cardiac Arrest Risk Triage     | ML deterioration/arrest risk from EHR.                                                                                                          | unverified | —       |
| TREWScore     | Targeted Real-time Early Warning Score    | EHR-based early sepsis prediction.                                                                                                              | unverified | —       |
| SWIFT         | Stability and Workload Index for Transfer | Predicts unplanned ICU readmission at discharge.                                                                                                | unverified | —       |

---

## 3. Sepsis-specific

| Score           | Full name                                              | Purpose / inputs                                                        | Status     | Key ref |
| --------------- | ------------------------------------------------------ | ----------------------------------------------------------------------- | ---------- | ------- |
| SIRS            | Systemic Inflammatory Response Syndrome criteria       | Temp, HR, RR/PaCO2, WBC — sensitive, nonspecific; pre-Sepsis-3.         | superseded | R3, R7  |
| qSOFA           | quick SOFA                                             | Bedside screen: RR ≥22, altered mentation, SBP ≤100 (Sepsis-3, 2016).   | contested  | R7      |
| SOFA (Sepsis-3) | —                                                      | Defines sepsis as infection + acute SOFA rise ≥2.                       | current    | R7      |
| MEDS            | Mortality in Emergency Department Sepsis               | ED sepsis mortality risk.                                               | unverified | —       |
| PIRO            | Predisposition, Infection, Response, Organ dysfunction | Staging framework for sepsis.                                           | unverified | —       |
| LRINEC          | Laboratory Risk Indicator for Necrotizing Fasciitis    | Discriminates nec-fasc from cellulitis (CRP, WBC, Hb, Na, Cr, glucose). | unverified | —       |
| Phoenix         | Phoenix Sepsis Score / Criteria                        | Pediatric sepsis definition (2024) — see §20.                           | current    | R3, R4  |

> §3 notes — _verified 2026-06-01:_ SIRS was **removed from the sepsis definition** by Sepsis-3 (2016) and is documented to have poor predictive properties (R3, R7); it survives as a descriptive concept, not a sepsis definition. qSOFA remains in use but is `contested` — low sensitivity, de-emphasized as a standalone screen in current Surviving Sepsis Campaign guidance (R7). Adult sepsis **definition** (SOFA/Sepsis-3) is unchanged since 2016; the **management** guideline is the newest SSC 2026 edition (R7).

---

## 4. Neurologic / neurocritical care

| Score                    | Full name                                         | Purpose / inputs                                                                      | Status     | Key ref |
| ------------------------ | ------------------------------------------------- | ------------------------------------------------------------------------------------- | ---------- | ------- |
| GCS / GCS-P              | Glasgow Coma Scale (± Pupil reactivity)           | Consciousness; GCS-P subtracts pupil reactivity score for prognostic granularity.     | unverified | —       |
| FOUR                     | Full Outline of UnResponsiveness                  | Coma scale usable in intubated patients (eye, motor, brainstem, respiration).         | unverified | —       |
| NIHSS                    | NIH Stroke Scale                                  | Ischemic stroke severity.                                                             | unverified | —       |
| ASPECTS                  | Alberta Stroke Program Early CT Score             | Early ischemic change on CT (MCA territory).                                          | unverified | —       |
| Hunt & Hess              | —                                                 | Clinical grade of aneurysmal SAH.                                                     | unverified | —       |
| WFNS                     | World Federation of Neurosurgical Societies grade | SAH grade (GCS + focal deficit).                                                      | unverified | —       |
| Fisher / modified Fisher | —                                                 | SAH blood burden on CT → vasospasm risk.                                              | unverified | —       |
| ICH Score                | —                                                 | 30-day mortality in intracerebral hemorrhage (GCS, volume, IVH, infratentorial, age). | unverified | —       |
| Marshall / Rotterdam     | CT classifications                                | TBI CT grading; Rotterdam is additive/prognostic.                                     | unverified | —       |
| IMPACT / CRASH           | prognostic models                                 | TBI outcome prediction.                                                               | unverified | —       |
| GOS / GOSE               | Glasgow Outcome Scale / Extended                  | Global functional outcome.                                                            | unverified | —       |
| mRS                      | modified Rankin Scale                             | Disability/dependence outcome (stroke especially).                                    | unverified | —       |
| CPC                      | Cerebral Performance Category                     | Neurologic outcome after cardiac arrest.                                              | unverified | —       |
| CAM-ICU                  | Confusion Assessment Method for the ICU           | Delirium screen for ventilated patients.                                              | unverified | —       |
| ICDSC                    | Intensive Care Delirium Screening Checklist       | Delirium screen, checklist-based.                                                     | unverified | —       |
| Spetzler-Martin          | —                                                 | AVM surgical risk grade.                                                              | unverified | —       |

---

## 5. Respiratory / ARDS / ventilation / weaning / pneumonia

| Score             | Full name                                                          | Purpose / inputs                                                              | Status     | Key ref |
| ----------------- | ------------------------------------------------------------------ | ----------------------------------------------------------------------------- | ---------- | ------- |
| Berlin definition | —                                                                  | ARDS classification (mild/mod/severe by P/F at PEEP ≥5).                      | superseded | R1, R2  |
| Murray LIS        | Lung Injury Score                                                  | ARDS severity (P/F, PEEP, compliance, CXR quadrants); used for ECMO referral. | unverified | —       |
| P/F ratio         | PaO2/FiO2                                                          | Oxygenation index of severity.                                                | unverified | —       |
| SF ratio          | SpO2/FiO2                                                          | Noninvasive surrogate for P/F.                                                | unverified | —       |
| OI / OSI          | Oxygenation Index / Oxygen Saturation Index                        | (MAP × FiO2)/PaO2 (or SpO2) — pediatric/severe hypoxemia.                     | unverified | —       |
| RSBI              | Rapid Shallow Breathing Index (Tobin)                              | RR/Vt — weaning readiness.                                                    | unverified | —       |
| ROX               | Respiratory rate–OXygenation index                                 | HFNC failure prediction ((SpO2/FiO2)/RR).                                     | unverified | —       |
| HACOR             | Heart rate, Acidosis, Consciousness, Oxygenation, Respiratory rate | NIV failure prediction.                                                       | unverified | —       |
| CPIS              | Clinical Pulmonary Infection Score                                 | VAP likelihood.                                                               | unverified | —       |
| CURB-65 / CRB-65  | Confusion, Urea, RR, BP, age ≥65                                   | CAP severity/disposition.                                                     | unverified | —       |
| PSI / PORT        | Pneumonia Severity Index                                           | CAP 30-day mortality risk stratification.                                     | unverified | —       |
| SMART-COP         | —                                                                  | Predicts need for intensive respiratory/vasopressor support in CAP.           | unverified | —       |
| 4C Mortality      | ISARIC Coronavirus Clinical Characterisation Consortium            | COVID-19 in-hospital mortality.                                               | unverified | —       |
| PESI / sPESI      | (simplified) Pulmonary Embolism Severity Index                     | PE 30-day mortality (also cardiovascular).                                    | unverified | —       |

> §5 note — _verified 2026-06-01:_ The **Berlin definition (2012) is superseded** by the New Global Definition of ARDS (2024), which adds HFNC ≥30 L/min, SpO2/FiO2 as a PaO2/FiO2 alternative, lung ultrasound, and PEEP-independent criteria for resource-limited settings (R1); ESICM 2023 guidelines accompany it (R2). Berlin remains valid as the predecessor framework and is still widely referenced in legacy trials.

---

## 6. Cardiovascular / cardiac / shock

| Score                   | Full name                                                                            | Purpose / inputs                              | Status     | Key ref |
| ----------------------- | ------------------------------------------------------------------------------------ | --------------------------------------------- | ---------- | ------- |
| Killip                  | —                                                                                    | Acute MI clinical heart-failure class.        | unverified | —       |
| Forrester               | —                                                                                    | Hemodynamic class (CI vs PCWP).               | unverified | —       |
| TIMI                    | Thrombolysis In Myocardial Infarction                                                | ACS risk.                                     | unverified | —       |
| GRACE                   | Global Registry of Acute Coronary Events                                             | ACS mortality.                                | unverified | —       |
| HEART                   | History, ECG, Age, Risk factors, Troponin                                            | ED chest-pain MACE risk.                      | unverified | —       |
| SCAI SHOCK              | Society for Cardiovascular Angiography and Interventions stages A–E                  | Cardiogenic shock severity staging.           | unverified | —       |
| VIS                     | Vasoactive-Inotropic Score                                                           | Cumulative vasoactive burden.                 | unverified | —       |
| CPO                     | Cardiac Power Output                                                                 | Pump performance in shock.                    | unverified | —       |
| CHA₂DS₂-VASc / HAS-BLED | —                                                                                    | AF stroke risk / bleeding risk (overlaps §9). | unverified | —       |
| Wells / Geneva          | —                                                                                    | PE/DVT pretest probability.                   | unverified | —       |
| EuroSCORE II / STS      | European System for Cardiac Operative Risk Evaluation / Society of Thoracic Surgeons | Cardiac surgery mortality.                    | unverified | —       |
| INTERMACS               | Interagency Registry for Mechanically Assisted Circulatory Support                   | MCS candidacy profile.                        | unverified | —       |
| Aldrete                 | —                                                                                    | Post-anesthesia recovery readiness.           | unverified | —       |

---

## 7. Hepatic / liver failure

| Score                     | Full name                              | Purpose / inputs                                                                 | Status     | Key ref |
| ------------------------- | -------------------------------------- | -------------------------------------------------------------------------------- | ---------- | ------- |
| Child-Pugh                | Child-Turcotte-Pugh                    | Cirrhosis severity (bilirubin, albumin, INR, ascites, encephalopathy).           | unverified | —       |
| MELD / MELD-Na / MELD 3.0 | Model for End-stage Liver Disease      | Transplant allocation & mortality; 3.0 (2021) adds albumin & sex.                | current    | R5      |
| UKELD / PELD              | UK / Pediatric End-stage Liver Disease | Regional/pediatric variants.                                                     | current    | R5      |
| King's College Criteria   | —                                      | Transplant listing in acute liver failure (paracetamol vs non-paracetamol arms). | unverified | —       |
| CLIF-SOFA / CLIF-C ACLF   | Chronic Liver Failure consortium       | Acute-on-chronic liver failure grading/prognosis.                                | unverified | —       |
| Maddrey DF                | Maddrey Discriminant Function          | Severe alcoholic hepatitis, steroid decision.                                    | unverified | —       |
| Lille                     | —                                      | Day-7 steroid response in alcoholic hepatitis.                                   | unverified | —       |
| GAHS                      | Glasgow Alcoholic Hepatitis Score      | Alcoholic hepatitis prognosis.                                                   | unverified | —       |
| ALBI                      | Albumin-Bilirubin grade                | Liver function, objective alternative to Child-Pugh.                             | unverified | —       |

> §7 note — _verified 2026-06-01:_ For **US allocation**, MELD 3.0 (adds albumin + sex, creatinine capped at 3.0 mg/dL) and PELD-Cr (adds creatinine) became the operative scores at OPTN implementation in **July 2023** (R5). Plain MELD / MELD-Na / classic PELD remain valid as prognostic tools but are no longer the allocation instrument. Child-Pugh status (still-current prognostic use) not yet citation-checked → remains `unverified`.

---

## 8. Renal / acute kidney injury

| Score                  | Full name                                 | Purpose / inputs                                             | Status     | Key ref |
| ---------------------- | ----------------------------------------- | ------------------------------------------------------------ | ---------- | ------- |
| RIFLE                  | Risk, Injury, Failure, Loss, ESRD         | First consensus AKI staging (creatinine/GFR + urine output). | superseded | R6      |
| AKIN                   | Acute Kidney Injury Network               | Refined AKI staging within 48 h.                             | superseded | R6      |
| KDIGO                  | Kidney Disease: Improving Global Outcomes | Current harmonized AKI staging.                              | current    | R6      |
| Cleveland Clinic score | —                                         | Cardiac-surgery–associated AKI risk.                         | unverified | —       |

> §8 note — _verified 2026-06-01:_ KDIGO 2012 staging is the **operative AKI definition today**, having harmonized RIFLE and AKIN (now `superseded` predecessors). **Live transition:** the KDIGO 2026 AKI/AKD guideline draft is in public review (through 2026-05-11) — first major update since 2012, introducing an AKI/AKD continuum and structural biomarkers alongside creatinine/urine-output criteria (R6). Re-verify the KDIGO row when the final 2026 guideline publishes.

---

## 9. Coagulation / hematology

| Score                     | Full name                                           | Purpose / inputs                                                | Status     | Key ref |
| ------------------------- | --------------------------------------------------- | --------------------------------------------------------------- | ---------- | ------- |
| ISTH overt DIC            | International Society on Thrombosis and Haemostasis | DIC diagnosis (platelets, fibrin marker, PT, fibrinogen).       | unverified | —       |
| JAAM DIC                  | Japanese Association for Acute Medicine             | More sensitive DIC criteria.                                    | unverified | —       |
| 4Ts                       | Thrombocytopenia, Timing, Thrombosis, oTher         | HIT pretest probability.                                        | unverified | —       |
| HAS-BLED / ORBIT / ATRIA  | —                                                   | Anticoagulation bleeding risk.                                  | unverified | —       |
| Caprini / Padua / IMPROVE | —                                                   | VTE prophylaxis risk (surgical/medical); IMPROVE also bleeding. | unverified | —       |
| PLASMIC                   | —                                                   | TTP likelihood (ADAMTS13 deficiency).                           | unverified | —       |
| HScore                    | —                                                   | Hemophagocytic lymphohistiocytosis (HLH) probability.           | unverified | —       |

---

## 10. Trauma

| Score       | Full name                                                             | Purpose / inputs                                                               | Status     | Key ref |
| ----------- | --------------------------------------------------------------------- | ------------------------------------------------------------------------------ | ---------- | ------- |
| AIS         | Abbreviated Injury Scale                                              | Anatomic injury severity by body region — basis for ISS.                       | unverified | —       |
| ISS / NISS  | (New) Injury Severity Score                                           | Sum of squares of top AIS regions; NISS uses worst three regardless of region. | unverified | —       |
| RTS         | Revised Trauma Score                                                  | Physiologic (GCS, SBP, RR).                                                    | unverified | —       |
| TRISS       | Trauma and Injury Severity Score                                      | Survival probability combining ISS + RTS + age + mechanism.                    | unverified | —       |
| ASCOT       | A Severity Characterization Of Trauma                                 | Alternative to TRISS.                                                          | unverified | —       |
| Shock Index | HR/SBP                                                                | Occult hemorrhage marker.                                                      | unverified | —       |
| ABC / TASH  | Assessment of Blood Consumption / Trauma Associated Severe Hemorrhage | Massive transfusion prediction.                                                | unverified | —       |
| MGAP / GAP  | Mechanism, GCS, Age, Pressure                                         | Field/early mortality triage.                                                  | unverified | —       |
| MESS        | Mangled Extremity Severity Score                                      | Limb salvage vs amputation.                                                    | unverified | —       |
| AAST OIS    | American Association for the Surgery of Trauma Organ Injury Scale     | Grades solid-organ injury (spleen, liver, kidney, etc.).                       | unverified | —       |

---

## 11. Burns

| Score               | Full name                       | Purpose / inputs                                          | Status     | Key ref |
| ------------------- | ------------------------------- | --------------------------------------------------------- | ---------- | ------- |
| TBSA                | Total Body Surface Area         | Burn extent (Rule of Nines, Lund-Browder chart).          | unverified | —       |
| Baux / revised Baux | —                               | Mortality = age + %TBSA (revised adds inhalation injury). | unverified | —       |
| ABSI                | Abbreviated Burn Severity Index | Mortality (age, sex, TBSA, inhalation, full-thickness).   | unverified | —       |
| BOBI                | Belgian Outcome in Burn Injury  | Mortality (age, TBSA, inhalation).                        | unverified | —       |

---

## 12. Sedation / pain / agitation / delirium (analgosedation bundle)

| Score           | Full name                            | Purpose / inputs                                  | Status     | Key ref |
| --------------- | ------------------------------------ | ------------------------------------------------- | ---------- | ------- |
| RASS            | Richmond Agitation-Sedation Scale    | Sedation–agitation target (+4 to −5).             | unverified | —       |
| SAS             | Riker Sedation-Agitation Scale       | Sedation depth (1–7).                             | unverified | —       |
| Ramsay          | —                                    | Older sedation scale.                             | unverified | —       |
| MAAS            | Motor Activity Assessment Scale      | Sedation via motor response.                      | unverified | —       |
| BIS             | Bispectral Index                     | Processed-EEG depth (esp. NMB/burst suppression). | unverified | —       |
| CPOT            | Critical-Care Pain Observation Tool  | Behavioral pain in non-communicative patients.    | unverified | —       |
| BPS             | Behavioral Pain Scale                | Behavioral pain (ventilated).                     | unverified | —       |
| NRS / VAS       | Numeric Rating / Visual Analog Scale | Self-reported pain.                               | unverified | —       |
| CAM-ICU / ICDSC | (see §4)                             | Delirium screening.                               | unverified | —       |

---

## 13. Withdrawal syndromes

| Score       | Full name                                                     | Purpose / inputs                                        | Status     | Key ref |
| ----------- | ------------------------------------------------------------- | ------------------------------------------------------- | ---------- | ------- |
| CIWA-Ar     | Clinical Institute Withdrawal Assessment for Alcohol, revised | Alcohol withdrawal severity / symptom-triggered dosing. | unverified | —       |
| CINA        | Clinical Institute Narcotic Assessment                        | Opioid withdrawal.                                      | unverified | —       |
| COWS / SOWS | Clinical / Subjective Opiate Withdrawal Scale                 | Opioid withdrawal.                                      | unverified | —       |
| WAT-1       | Withdrawal Assessment Tool-1                                  | Pediatric iatrogenic withdrawal.                        | unverified | —       |

---

## 14. Nutrition

| Score            | Full name                                                  | Purpose / inputs                                        | Status     | Key ref |
| ---------------- | ---------------------------------------------------------- | ------------------------------------------------------- | ---------- | ------- |
| NUTRIC / mNUTRIC | Nutrition Risk in the Critically Ill (modified omits IL-6) | Identifies who benefits most from aggressive nutrition. | unverified | —       |
| NRS-2002         | Nutritional Risk Screening 2002                            | General hospital nutrition risk.                        | unverified | —       |
| SGA              | Subjective Global Assessment                               | Clinical nutritional status.                            | unverified | —       |
| MUST             | Malnutrition Universal Screening Tool                      | Screening.                                              | unverified | —       |

---

## 15. Frailty / functional status / ICU-acquired weakness

| Score          | Full name                                      | Purpose / inputs                                           | Status     | Key ref |
| -------------- | ---------------------------------------------- | ---------------------------------------------------------- | ---------- | ------- |
| CFS            | Clinical Frailty Scale (Rockwood)              | Pre-admission frailty (1–9).                               | unverified | —       |
| IMS            | ICU Mobility Scale                             | Highest mobility level achieved.                           | unverified | —       |
| FSS-ICU        | Functional Status Score for the ICU            | Physical function in ICU.                                  | unverified | —       |
| CPAx           | Chelsea Critical Care Physical Assessment tool | Physical morbidity.                                        | unverified | —       |
| MRC sum score  | Medical Research Council sum score             | ICU-acquired weakness (manual strength, 12 muscle groups). | unverified | —       |
| Barthel / Katz | —                                              | Baseline ADL function.                                     | unverified | —       |

---

## 16. Pressure injury risk

| Score    | Full name                                      | Status     | Key ref |
| -------- | ---------------------------------------------- | ---------- | ------- |
| Braden   | Braden Scale for Predicting Pressure Sore Risk | unverified | —       |
| Norton   | Norton Scale                                   | unverified | —       |
| Waterlow | Waterlow Score                                 | unverified | —       |

---

## 17. GI: pancreatitis & GI bleeding

| Score              | Full name                                       | Purpose / inputs                                             | Status     | Key ref |
| ------------------ | ----------------------------------------------- | ------------------------------------------------------------ | ---------- | ------- |
| Ranson             | —                                               | Acute pancreatitis severity (admission + 48 h).              | unverified | —       |
| Glasgow-Imrie      | —                                               | Pancreatitis severity.                                       | unverified | —       |
| BISAP              | Bedside Index of Severity in Acute Pancreatitis | Early mortality risk.                                        | unverified | —       |
| CTSI / Balthazar   | CT Severity Index                               | Radiologic pancreatitis severity.                            | unverified | —       |
| Marshall (mod.)    | —                                               | Organ dysfunction in revised Atlanta classification.         | unverified | —       |
| Glasgow-Blatchford | —                                               | Upper GI bleed — need for intervention (pre-endoscopy).      | unverified | —       |
| Rockall            | —                                               | Upper GI bleed rebleeding/mortality (full = post-endoscopy). | unverified | —       |
| AIMS65             | Albumin, INR, Mental status, SBP, age 65        | UGIB mortality.                                              | unverified | —       |
| Forrest            | —                                               | Endoscopic peptic-ulcer rebleeding stigmata.                 | unverified | —       |

---

## 18. Obstetric critical care

| Score                         | Full name                                        | Purpose / inputs                              | Status     | Key ref |
| ----------------------------- | ------------------------------------------------ | --------------------------------------------- | ---------- | ------- |
| MEOWS                         | Modified Early Obstetric Warning Score           | Maternal deterioration trigger.               | unverified | —       |
| omSOFA / omqSOFA              | obstetrically modified (q)SOFA                   | Pregnancy-adjusted sepsis screen.             | unverified | —       |
| SOS                           | Sepsis in Obstetrics Score                       | ICU admission prediction in obstetric sepsis. | unverified | —       |
| HELLP (Mississippi/Tennessee) | Hemolysis, Elevated Liver enzymes, Low Platelets | Severity classification.                      | unverified | —       |

---

## 19. Airway / difficult intubation

| Score                | Full name                                                    | Purpose / inputs                              | Status     | Key ref |
| -------------------- | ------------------------------------------------------------ | --------------------------------------------- | ---------- | ------- |
| Mallampati           | (modified)                                                   | Oropharyngeal view → difficult laryngoscopy.  | unverified | —       |
| Cormack-Lehane       | —                                                            | Laryngoscopic view grade.                     | unverified | —       |
| LEMON                | Look, Evaluate 3-3-2, Mallampati, Obstruction, Neck mobility | Difficult-airway bundle.                      | unverified | —       |
| MACOCHA              | —                                                            | Difficult intubation specifically in the ICU. | unverified | —       |
| Wilson / El-Ganzouri | —                                                            | Composite difficult-intubation risk.          | unverified | —       |

---

## 20. Pediatric & neonatal

| Score            | Full name                                                 | Purpose / inputs                                                | Status     | Key ref |
| ---------------- | --------------------------------------------------------- | --------------------------------------------------------------- | ---------- | ------- |
| PRISM III/IV     | Pediatric Risk of Mortality                               | PICU mortality.                                                 | unverified | —       |
| PIM2 / PIM3      | Pediatric Index of Mortality                              | Admission-based PICU mortality.                                 | unverified | —       |
| PELOD-2          | Pediatric Logistic Organ Dysfunction                      | Organ dysfunction.                                              | unverified | —       |
| pSOFA            | pediatric SOFA                                            | Age-adjusted SOFA.                                              | unverified | —       |
| Phoenix          | Phoenix Sepsis Score / Criteria                           | New pediatric sepsis definition (2024) — resp, CV, coag, neuro. | current    | R3, R4  |
| APGAR            | Appearance, Pulse, Grimace, Activity, Respiration         | Newborn condition at 1/5 min.                                   | unverified | —       |
| SNAP / SNAPPE-II | Score for Neonatal Acute Physiology (Perinatal Extension) | NICU mortality.                                                 | unverified | —       |
| CRIB / CRIB-II   | Clinical Risk Index for Babies                            | VLBW neonatal mortality.                                        | unverified | —       |
| Westley          | Westley Croup Score                                       | Croup severity.                                                 | unverified | —       |
| COMFORT-B        | —                                                         | Pediatric sedation/distress.                                    | unverified | —       |

> §20 note — _verified 2026-06-01:_ The Phoenix criteria (2024) **replaced the 2005 IPSCC / SIRS-based pediatric sepsis definitions** as the data-driven international standard (R3, R4). The legacy IPSCC pathway is not a row here; treat any pediatric SIRS-based sepsis criteria encountered elsewhere as superseded.

---

## 21. Cardiac arrest & post-arrest

| Score | Full name                                                | Purpose / inputs               | Status     | Key ref |
| ----- | -------------------------------------------------------- | ------------------------------ | ---------- | ------- |
| CPC   | Cerebral Performance Category                            | Neurologic outcome (1–5).      | unverified | —       |
| OHCA  | Out-of-Hospital Cardiac Arrest score                     | Outcome prediction.            | unverified | —       |
| CAHP  | Cardiac Arrest Hospital Prognosis                        | Poor neuro outcome prediction. | unverified | —       |
| rCAST | post-Cardiac Arrest Syndrome for Therapeutic hypothermia | Severity stratification.       | unverified | —       |

---

## 22. ECMO / mechanical support survival prediction

| Score            | Full name                                   | Purpose / inputs            | Status     | Key ref |
| ---------------- | ------------------------------------------- | --------------------------- | ---------- | ------- |
| RESP             | Respiratory ECMO Survival Prediction        | VV-ECMO survival.           | unverified | —       |
| SAVE             | Survival After Veno-arterial ECMO           | VA-ECMO survival.           | unverified | —       |
| PRESERVE         | PRedicting dEath for SEvere ARDS on VV-ECMO | VV-ECMO mortality.          | unverified | —       |
| PRESET / ECMOnet | —                                           | VV-ECMO mortality variants. | unverified | —       |

---

## 23. Toxicology

| Score                            | Full name                | Purpose / inputs                                                     | Status     | Key ref |
| -------------------------------- | ------------------------ | -------------------------------------------------------------------- | ---------- | ------- |
| PSS                              | Poisoning Severity Score | Standardized poisoning severity grading.                             | unverified | —       |
| King's College (paracetamol arm) | —                        | Acetaminophen-induced ALF transplant criteria.                       | unverified | —       |
| Rumack-Matthew                   | —                        | Acetaminophen nomogram (treatment threshold; nomogram, not a score). | unverified | —       |

---

## 24. Long-term / quality-of-life outcomes (relevant to PICS follow-up)

| Instrument       | Note                                                               | Status     | Key ref |
| ---------------- | ------------------------------------------------------------------ | ---------- | ------- |
| GOSE / mRS / CPC | Functional/neurologic outcome (see prior sections).                | unverified | —       |
| EQ-5D, SF-36     | Generic HRQoL — used in ICU outcome research, not a bedside score. | unverified | —       |

---

### Practical caveats for use

- **Calibration drift.** APACHE/SAPS/MPM were derived on older cohorts; observed-to-expected ratios drift with case-mix and era. Local recalibration matters before using any of these for benchmarking.
- **Discrimination vs. calibration.** A score can rank patients well (good AUROC) yet predict absolute risk poorly. For individual decisions, calibration is the property that bites.
- **Screening vs. diagnosis vs. prognosis.** qSOFA screens, SOFA stages, APACHE prognosticates — conflating these is a common reasoning error.
- **Composite "definitions" vs. "scores."** Berlin (ARDS), Sepsis-3, KDIGO, and revised Atlanta are _classification frameworks_ that embed scores rather than being scores themselves; included here because they function as scoring instruments at the bedside.
- **Always verify thresholds at point of care.** This document gives identity and intent; exact cutoffs/weights should come from the primary source or a validated calculator.

---

## References

Verified entries cite these. PubMed-sourced items are attributed to PubMed with resolvable DOIs per source terms.

- **R1** — Matthay MA, et al. _A New Global Definition of Acute Respiratory Distress Syndrome._ Am J Respir Crit Care Med. 2024;209(1):37–47. Source: PubMed. DOI: https://doi.org/10.1164/rccm.202303-0558WS
- **R2** — Grasselli G, et al. _ESICM guidelines on acute respiratory distress syndrome: definition, phenotyping and respiratory support strategies._ Intensive Care Med. 2023;49(7):727–759. Source: PubMed. DOI: https://doi.org/10.1007/s00134-023-07050-7
- **R3** — Schlapbach LJ, et al. _International Consensus Criteria for Pediatric Sepsis and Septic Shock._ JAMA. 2024;331(8):665–674. Source: PubMed. DOI: https://doi.org/10.1001/jama.2024.0179
- **R4** — Sanchez-Pinto LN, et al. _Development and Validation of the Phoenix Criteria for Pediatric Sepsis and Septic Shock._ JAMA. 2024;331(8):675–686. Source: PubMed. DOI: https://doi.org/10.1001/jama.2024.0196
- **R5** — OPTN / UNOS. _Improving Liver Allocation: MELD 3.0 & PELD-Cr_ (implemented July 2023). https://optn.transplant.hrsa.gov/media/fyxhlkp5/improving-liver-allocation-meld-30-faq.pdf
- **R6** — KDIGO. _Acute Kidney Injury (AKI) and Acute Kidney Disease (AKD)_ — 2012 guideline operative; 2026 draft in public review through 2026-05-11. https://kdigo.org/guidelines/acute-kidney-injury/
- **R7** — Surviving Sepsis Campaign / SCCM / ESICM. _Adult sepsis definitions last revised 2016 (Sepsis-3); SSC 2026 management guidelines._ https://www.sccm.org/survivingsepsiscampaign/guidelines-and-resources/surviving-sepsis-campaign-adult-guidelines
- **R8** — Zimmerman JE, Kramer AA, McNair DS, Malila FM. _Acute Physiology and Chronic Health Evaluation (APACHE) IV: hospital mortality assessment for today's critically ill patients._ Crit Care Med. 2006;34(5):1297–1310. Source: PubMed (PMID 16540951). DOI: https://doi.org/10.1097/01.CCM.0000215112.84523.F0
- **R9** — Cox EGM, Wiersema R, Eck RJ, et al. _External validation of mortality prediction models for critical illness reveals preserved discrimination but poor calibration._ Crit Care Med. 2022;51(1):80–90. Source: PubMed (PMID 36378565). DOI: https://doi.org/10.1097/CCM.0000000000005712 — currency evidence for APACHE (`contested`) and SAPS: discrimination preserved, calibration poor before recalibration.
- **R10** — Moreno RP, Metnitz PGH, Almeida E, et al. _SAPS 3—From evaluation of the patient to evaluation of the intensive care unit. Part 2: development of a prognostic model for hospital mortality at ICU admission._ Intensive Care Med. 2005;31(10):1345–1355. Source: PubMed (PMID 16132892). DOI: https://doi.org/10.1007/s00134-005-2763-5. Predecessor SAPS II (Le Gall JR, Lemeshow S, Saulnier F. JAMA. 1993;270(24):2957–2963): https://doi.org/10.1001/jama.270.24.2957
- **R11** — Higgins TL, Kramer AA, Nathanson BH, et al. _Prospective validation of the intensive care unit admission Mortality Probability Model (MPM0-III)._ Crit Care Med. 2009;37(5):1619–1623. Source: PubMed (PMID 19325480). DOI: https://doi.org/10.1097/CCM.0b013e31819ded31
- **R12** — Vincent JL, Moreno R, Takala J, et al. _The SOFA (Sepsis-related Organ Failure Assessment) score to describe organ dysfunction/failure._ Intensive Care Med. 1996;22(7):707–710. Source: PubMed (PMID 8844239). DOI: https://doi.org/10.1007/BF01709751
- **R13** — Le Gall JR, Klar J, Lemeshow S, et al. _The Logistic Organ Dysfunction system: a new way to assess organ dysfunction in the intensive care unit._ JAMA. 1996;276(10):802–810. Source: PubMed (PMID 8769590). DOI: https://doi.org/10.1001/jama.276.10.802
- **R14** — Marshall JC, Cook DJ, Christou NV, et al. _Multiple organ dysfunction score: a reliable descriptor of a complex clinical outcome._ Crit Care Med. 1995;23(10):1638–1652. Source: PubMed (PMID 7587228). DOI: https://doi.org/10.1097/00003246-199510000-00007
- **R15** — Johnson AEW, Kramer AA, Clifford GD. _A new severity of illness scale using a subset of Acute Physiology And Chronic Health Evaluation data elements shows comparable predictive accuracy._ Crit Care Med. 2013;41(7):1711–1718. Source: PubMed (PMID 23660729). DOI: https://doi.org/10.1097/CCM.0b013e31828a24fe — the Oxford Acute Severity of Illness Score (OASIS).
- **R16** — Harrison DA, Parry GJ, Carpenter JR, Short A, Rowan K. _A new risk prediction model for critical care: the Intensive Care National Audit & Research Centre (ICNARC) model._ Crit Care Med. 2007;35(4):1091–1098. Source: PubMed (PMID 17334248). DOI: https://doi.org/10.1097/01.CCM.0000259468.24532.44 — currency: ICNARC maintains the live ICNARCH-2023 model (Case Mix Programme).
- **R17** — Miranda DR, de Rijk A, Schaufeli W. _Simplified Therapeutic Intervention Scoring System: the TISS-28 items._ Crit Care Med. 1996. Source: PubMed. DOI: https://doi.org/10.1097/00003246-199601000-00012 — lineage: TISS-76 (obsolete) → TISS-28 → NEMS → NAS.
- **R18** — Reis Miranda D, Moreno R, Iapichino G. _Nine equivalents of nursing manpower use score (NEMS)._ Intensive Care Med. 1997. Source: PubMed. DOI: https://doi.org/10.1007/s001340050406
- **R19** — Miranda DR, Nap R, de Rijk A, Schaufeli W, Iapichino G. _Nursing Activities Score._ Crit Care Med. 2003. Source: PubMed. DOI: https://doi.org/10.1097/01.CCM.0000045567.78801.CC. Currency — 2025 systematic review/meta-analysis of NAS (Li L, Zou X, Chen H, et al. Intensive Crit Care Nurs. 2025;91:104086): https://doi.org/10.1016/j.iccn.2025.104086
- **R20** — Copeland GP, Jones D, Walters M. _POSSUM: a scoring system for surgical audit._ Br J Surg. 1991. Source: PubMed. DOI: https://doi.org/10.1002/bjs.1800780327. P-POSSUM (Prytherch DR, Whiteley MS, Higgins B, et al. Br J Surg. 1998): https://doi.org/10.1046/j.1365-2168.1998.00840.x — currency: embedded in UK NELA (Year 9 report, RCoA 2024).
- **R21** — Kahn JM, Kramer AA, Rubenfeld GD. _Transferring critically ill patients out of hospital improves the standardized mortality ratio: a simulation study._ Chest. 2007. Source: PubMed. DOI: https://doi.org/10.1378/chest.06-0741 — SMR is a benchmarking output (observed/expected deaths), not a bedside score; subject to case-mix and transfer bias.
- **R23** — Zou J, Chen H, Liu C, et al. _Development and validation of a nomogram to predict the 30-day mortality risk of patients with intracerebral hemorrhage._ Front Neurosci. 2022;16:942100. Source: PubMed (PMID 36033629). DOI: https://doi.org/10.3389/fnins.2022.942100 — OASIS currency: comparator severity score on a contemporary MIMIC-III ICU cohort; validation-cohort OASIS AUC 0.728.

> **Verification provenance:** R1–R4 retrieved via PubMed (2026-06-01). R5–R7 retrieved via web search of primary governing-body sources (2026-06-01). R8–R23 added for §1 General severity verification (Task 1.1, 2026-06-14), retrieved via PubMed with citation metadata cross-checked; every DOI confirmed resolving via the DOI Handle System API. ODIN held `unverified` (single-centre 1993 model, no external validation or designating authority). R22 reserved for ODIN pending such a source. See [`TODO.md`](TODO.md) for the protocol and work breakdown to drive `unverified → 0`.
