# Medimetry

Reference implementations of published clinical formulas and scores, written in pure Python for software
developers and researchers.

## Intended use

medimetry reproduces formulas and scoring systems exactly as published in the cited literature (every function
lists its primary source). It returns the raw numeric result or a category defined by that publication and
nothing else: no interpretation, no recommendation, no clinical guidance. Where a category comes from a different
publication than the formula (e.g. a guideline's risk bands), that publication is cited separately and marked as such.

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

See [docs/references.md](docs/references.md) for how the cited sources were verified.

## Development

See [Contributing](CONTRIBUTING.md).


## Medical Tests Reference Table

| Domain / System                                     |   | Test / Score / Calculator                     |
|-----------------------------------------------------|---|-----------------------------------------------|
| Renal Function (**renal**)                          | ✅ | Creatinine Clearance (Cockcroft-Gault)        |
|                                                     | ✅ | CKD-EPI GFR Equations                         |
|                                                     | ✅ | EKFC GFR Equation                             |
|                                                     | ✅ | MDRD GFR Equation                             |
|                                                     | ✅ | CKD Staging                                   |
|                                                     |   | Fractional Excretion of Sodium (FENa)         |
| Electrolytes (**lytes**)                            |   | Sodium Correction for Hyperglycemia           |
|                                                     |   | Serum Osmolality/Osmolarity                   |
|                                                     | ✅ | Calcium Correction for Hypo-/Hyperalbuminemia |
|                                                     |   | Free Water Deficit in Hypernatremia           |
| Cardiovascular Risk / Hemodynamics (**cardiovasc**) | ✅ | Mean Arterial Pressure (MAP)                  |
|                                                     | ✅ | CHA₂DS₂-VASc Score                            |
|                                                     |   | ASCVD 2013 Risk Calculator                    |
|                                                     |   | ASCVD Risk Algorithm with Known ASCVD         |
|                                                     | ✅ | Framingham General CVD Risk Score (2008)      |
|                                                     |   | HEART Score                                   |
|                                                     |   | GRACE ACS Risk and Mortality Calculator       |
|                                                     |   | Revised Cardiac Risk Index (Pre-op)           |
|                                                     |   | ARISCAT Score                                 |
|                                                     |   | Gupta MICA Score                              |
| Liver / GI / Metabolic                              |   | Fibrosis-4 (FIB-4) Index                      |
|                                                     | ✅ | Child-Pugh Score                              |
|                                                     |   | MELD Na                                       |
|                                                     |   | HOMA-IR                                       |
|                                                     |   | Serum Anion Gap                               |
| Pulmonary / Sleep                                   |   | Wells’ Criteria for PE                        |
|                                                     | ✅ | Revised / Simplified Geneva Score             |
|                                                     | ✅ | PERC Rule                                     |
|                                                     |   | Wells’ Criteria for DVT                       |
|                                                     |   | STOP-BANG Score                               |
| Neurological / Stroke / Consciousness (**neuro**)   |   | NIH Stroke Scale (NIHSS)                      |
|                                                     | ✅ | Glasgow Coma Scale (GCS)                      |
|                                                     |   | PECARN Pediatric Head Injury                  |
|                                                     |   | CURB-65 Score                                 |
| Body Metrics                                        | ✅ | BMI and BSA                                   |
|                                                     | ✅ | Growth charts (CDC 2000 / WHO 2006+2007)      |
|                                                     |   | Ideal & Adjusted Body Weight                  |
|                                                     |   | Maintenance Fluids Calculations               |
| Cardiac / ECG  (**cardiac**)                        | ✅ | Corrected QT Interval (QTc)                   |
| Psychiatric / Neuropsychiatric                      |   | PHQ-9                                         |
|                                                     |   | GAD-7                                         |
|                                                     |   | CIWA-Ar                                       |
| Medication / Pharmacology                           |   | Steroid Conversion Calculator                 |
|                                                     |   | Morphine Milligram Equivalents (MME)          |
| Risk Prediction / Surgery / ICU                     |   | SIRS, Sepsis, Septic Shock Criteria           |
|                                                     |   | Sequential Organ Failure Assessment (SOFA)    |
|                                                     |   | Padua Prediction Score                        |
|                                                     |   | ARISCAT Score                                 |
| Infectious / Inflammatory                           |   | Centor Score (Strep Pharyngitis)              |
|                                                     |   | PSI/PORT Score (Pneumonia)                    |
