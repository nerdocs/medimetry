# Medimetry

Reference implementations of published clinical formulas and scores, written in pure Python for software
developers and researchers.

## Intended use

medimetry reproduces formulas and scoring systems exactly as published in the cited literature (every function
lists its primary source). It returns the raw numeric result or the category defined by that publication and
nothing else: no interpretation, no recommendation, no clinical guidance.

**medimetry is not a medical device.** It is not intended for diagnosis, prevention, monitoring, prediction,
prognosis, treatment or alleviation of disease, and it must not be used as a basis for clinical decisions.
Anyone integrating it into a product with such a purpose is the manufacturer of that product and is solely
responsible for its qualification, validation and regulatory compliance (e.g. as software of unknown provenance
under IEC 62304). See [DISCLAIMER.md](DISCLAIMER.md).

The implementations are unit-tested against the published point tables and worked examples, but no clinical
validation has been performed and no warranty of correctness is given.

* Free software: MIT license

## Installation

```bash
pip install medimetry
```

You can also install the in-development version with::

    pip install https://github.com/nerdocs/medimetry/archive/refs/heads/main.zip


## Growth charts and WHO reference tables

`medimetry.growth` computes pediatric z-scores/percentiles from LMS tables. The CDC 2000 tables (public domain) are
bundled. The WHO Child Growth Standards / Growth Reference 2007 are licensed CC BY-NC-SA 3.0 IGO and cannot be
redistributed in an MIT package, so download them yourself once:

```python
from pathlib import Path
from medimetry.growth import download_who_tables
download_who_tables(Path("~/.cache/medimetry/who").expanduser())
```

Then pass `reference=GrowthReference.WHO, data_dir=...` to `growth_zscore` / `growth_percentile`.
See [docs/growth.md](docs/growth.md) for indicators, units and limitations.

## Development

See [Contributing](CONTRIBUTING.md).


## Medical Tests Reference Table

| Domain / System                                     |   | Test / Score / Calculator                     | Purpose / Use Case                             |
|-----------------------------------------------------|---|-----------------------------------------------|------------------------------------------------|
| Renal Function (**renal**)                          | ✅ | Creatinine Clearance (Cockcroft-Gault)        | Estimate renal function (CrCl)                 |
|                                                     | ✅ | CKD-EPI GFR Equations                         | Estimate GFR in CKD patients                   |
|                                                     | ✅ | MDRD GFR Equation                             | Estimate GFR in CKD patients                   |
|                                                     | ✅ | CKD Staging                                   | KDIGO GFR/albuminuria/risk categories          |
|                                                     |   | Fractional Excretion of Sodium (FENa)         | Differentiate renal failure type               |
| Electrolytes (**lytes**)                            |   | Sodium Correction for Hyperglycemia           | Correct Na in hyperglycemia                    |
|                                                     |   | Serum Osmolality/Osmolarity                   | Detect unmeasured serum compounds              |
|                                                     | ✅ | Calcium Correction for Hypo-/Hyperalbuminemia | Correct serum calcium                          |
|                                                     |   | Free Water Deficit in Hypernatremia           | Guide rehydration therapy                      |
| Cardiovascular Risk / Hemodynamics (**cardiovasc**) | ✅ | Mean Arterial Pressure (MAP)                  | Assess perfusion pressure                      |
|                                                     | ✅ | CHA₂DS₂-VASc Score                            | Stroke risk in atrial fibrillation             |
|                                                     |   | ASCVD 2013 Risk Calculator                    | 10-year risk of hard ASCVD                     |
|                                                     |   | ASCVD Risk Algorithm with Known ASCVD         | 10-year risk & statin guidance                 |
|                                                     | ✅ | Framingham General CVD Risk Score (2008)      | 10-year risk of cardiovascular disease         |
|                                                     |   | HEART Score                                   | 6-week risk of major cardiac events            |
|                                                     |   | GRACE ACS Risk and Mortality Calculator       | Mortality risk in ACS                          |
|                                                     |   | Revised Cardiac Risk Index (Pre-op)           | Cardiac risk after noncardiac surgery          |
|                                                     |   | ARISCAT Score                                 | Post-op pulmonary complications risk           |
|                                                     |   | Gupta MICA Score                              | Post-op MI/cardiac arrest risk                 |
| Liver / GI / Metabolic                              |   | Fibrosis-4 (FIB-4) Index                      | Noninvasive liver fibrosis assessment          |
|                                                     | ✅ | Child-Pugh Score                              | Cirrhosis severity & mortality                 |
|                                                     |   | MELD Na                                       | End-stage liver disease & transplant planning  |
|                                                     |   | HOMA-IR                                       | Insulin resistance estimate                    |
|                                                     |   | Serum Anion Gap                               | Metabolic acidosis evaluation                  |
| Pulmonary / Sleep                                   |   | Wells’ Criteria for PE                        | PE risk stratification                         |
|                                                     | ✅ | Revised / Simplified Geneva Score             | Clinical probability of PE                     |
|                                                     | ✅ | PERC Rule                                     | PE rule-out criteria count                     |
|                                                     |   | Wells’ Criteria for DVT                       | DVT risk assessment                            |
|                                                     |   | STOP-BANG Score                               | Obstructive sleep apnea screening              |
| Neurological / Stroke / Consciousness (**neuro**)   |   | NIH Stroke Scale (NIHSS)                      | Stroke severity & monitoring                   |
|                                                     | ✅ | Glasgow Coma Scale (GCS)                      | Coma severity assessment                       |
|                                                     |   | PECARN Pediatric Head Injury                  | Brain imaging need after pediatric head injury |
|                                                     |   | CURB-65 Score                                 | Pneumonia severity & mortality                 |
| Body Metrics                                        | ✅ | BMI and BSA                                   | Body mass and surface area                     |
|                                                     | ✅ | Growth charts (CDC 2000 / WHO 2006+2007)      | Pediatric z-scores and percentiles (LMS)       |
|                                                     |   | Ideal & Adjusted Body Weight                  | Weight assessment for dosing/therapy           |
|                                                     |   | Maintenance Fluids Calculations               | Calculate fluid needs                          |
| Cardiac / ECG  (**cardiac**)                        | ✅ | Corrected QT Interval (QTc)                   | Correct QT for heart rate extremes             |
| Psychiatric / Neuropsychiatric                      |   | PHQ-9                                         | Depression severity                            |
|                                                     |   | GAD-7                                         | Anxiety severity                               |
|                                                     |   | CIWA-Ar                                       | Alcohol withdrawal severity                    |
| Medication / Pharmacology                           |   | Steroid Conversion Calculator                 | Steroid dose equivalence                       |
|                                                     |   | Morphine Milligram Equivalents (MME)          | Opioid dose conversion                         |
| Risk Prediction / Surgery / ICU                     |   | SIRS, Sepsis, Septic Shock Criteria           | Sepsis severity assessment                     |
|                                                     |   | Sequential Organ Failure Assessment (SOFA)    | ICU mortality prediction                       |
|                                                     |   | Padua Prediction Score                        | VTE risk & anticoagulation need                |
|                                                     |   | ARISCAT Score                                 | Post-op pulmonary complications risk           |
| Infectious / Inflammatory                           |   | Centor Score (Strep Pharyngitis)              | Streptococcal pharyngitis probability          |
|                                                     |   | PSI/PORT Score (Pneumonia)                    | Pneumonia mortality risk                       |
