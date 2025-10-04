# Medimetry

Medical calculation library for clinical formulas and scores

This library provides formulas for estimatng or calculating risks with the help of medically relevant and
often used algorithms.

They are tested intensively, but we can give no warranty that the results are correct. Especially, results must not
be taken for granted as basis for clinical decision-making.

* Free software: MIT license

## Installation

```bash
pip install medimetry
```

You can also install the in-development version with::

    pip install https://github.com/nerdocs/medimetry/-/archive/main/medimetry-main.zip


## Development

To install the git pre-commit hooks run:
```bash
pre-commit install --install-hooks
# To update the versions:
pre-commit autoupdate
```

To run all the tests run::

```bash
tox
```

Note, to combine the coverage data from all the tox environments run:

```bash
PYTEST_ADDOPTS=--cov-append tox
```

## Medical Tests Reference Table

| Domain / System                                     |   | Test / Score / Calculator                         | Purpose / Use Case                             |
|-----------------------------------------------------|---|---------------------------------------------------|------------------------------------------------|
| Renal Function (**renal**)                          | ✅ | Creatinine Clearance (Cockcroft-Gault)            | Estimate renal function (CrCl)                 |
|                                                     | ✅ | CKD-EPI GFR Equations                             | Estimate GFR in CKD patients                   |
|                                                     | ✅ | MDRD GFR Equation                                 | Estimate GFR in CKD patients                   |
|                                                     |   | Fractional Excretion of Sodium (FENa)             | Differentiate renal failure type               |
| Electrolytes (**lytes**)                            |   | Sodium Correction for Hyperglycemia               | Correct Na in hyperglycemia                    |
|                                                     |   | Serum Osmolality/Osmolarity                       | Detect unmeasured serum compounds              |
|                                                     | ✅ | Calcium Correction for Hypo-/Hyperalbuminemia     | Correct serum calcium                          |
|                                                     |   | Free Water Deficit in Hypernatremia               | Guide rehydration therapy                      |
| Cardiovascular Risk / Hemodynamics (**cardiovasc**) | ✅ | Mean Arterial Pressure (MAP)                      | Assess perfusion pressure                      |
|                                                     | ✅ | CHA₂DS₂-VASc Score                                | Stroke risk in atrial fibrillation             |
|                                                     |   | ASCVD 2013 Risk Calculator                        | 10-year risk of hard ASCVD                     |
|                                                     |   | ASCVD Risk Algorithm with Known ASCVD             | 10-year risk & statin guidance                 |
|                                                     |   | Framingham Risk Score for CHD                     | 10-year risk of heart attack                   |
|                                                     |   | HEART Score                                       | 6-week risk of major cardiac events            |
|                                                     |   | GRACE ACS Risk and Mortality Calculator           | Mortality risk in ACS                          |
|                                                     |   | Revised Cardiac Risk Index (Pre-op)               | Cardiac risk after noncardiac surgery          |
|                                                     |   | ARISCAT Score                                     | Post-op pulmonary complications risk           |
|                                                     |   | Gupta MICA Score                                  | Post-op MI/cardiac arrest risk                 |
| Liver / GI / Metabolic                              |   | Fibrosis-4 (FIB-4) Index                          | Noninvasive liver fibrosis assessment          |
|                                                     | ✅ | Child-Pugh Score                                  | Cirrhosis severity & mortality                 |
|                                                     |   | MELD Na                                           | End-stage liver disease & transplant planning  |
|                                                     |   | HOMA-IR                                           | Insulin resistance estimate                    |
|                                                     |   | Serum Anion Gap                                   | Metabolic acidosis evaluation                  |
| Pulmonary / Sleep                                   |   | Wells’ Criteria for PE                            | PE risk stratification                         |
|                                                     |   | PERC Rule                                         | Rule out PE                                    |
|                                                     |   | Wells’ Criteria for DVT                           | DVT risk assessment                            |
|                                                     |   | STOP-BANG Score                                   | Obstructive sleep apnea screening              |
| Neurological / Stroke / Consciousness (**neuro**)   |   | NIH Stroke Scale (NIHSS)                          | Stroke severity & monitoring                   |
|                                                     | ✅ | Glasgow Coma Scale (GCS)                          | Coma severity assessment                       |
|                                                     |   | PECARN Pediatric Head Injury                      | Brain imaging need after pediatric head injury |
|                                                     |   | CURB-65 Score                                     | Pneumonia severity & mortality                 |
| Endocrine / Body Metrics                            |   | BMI and BSA                                       | Body mass and surface area                     |
|                                                     |   | Ideal & Adjusted Body Weight                      | Weight assessment for dosing/therapy           |
|                                                     |   | Maintenance Fluids Calculations                   | Calculate fluid needs                          |
| Cardiac / ECG  (**cardiac**)                        | ✅ | Corrected QT Interval (QTc)                       | Correct QT for heart rate extremes             |
| Psychiatric / Neuropsychiatric                      |   | PHQ-9                                             | Depression severity                            |
|                                                     |   | GAD-7                                             | Anxiety severity                               |
|                                                     |   | CIWA-Ar                                           | Alcohol withdrawal severity                    |
| Medication / Pharmacology                           |   | Steroid Conversion Calculator                     | Steroid dose equivalence                       |
|                                                     |   | Morphine Milligram Equivalents (MME)              | Opioid dose conversion                         |
| Risk Prediction / Surgery / ICU                     |   | SIRS, Sepsis, Septic Shock Criteria               | Sepsis severity assessment                     |
|                                                     |   | Sequential Organ Failure Assessment (SOFA)        | ICU mortality prediction                       |
|                                                     |   | Padua Prediction Score                            | VTE risk & anticoagulation need                |
|                                                     |   | ARISCAT Score                                     | Post-op pulmonary complications risk           |
| Infectious / Inflammatory                           |   | Centor Score (Strep Pharyngitis)                  | Streptococcal pharyngitis probability          |
|                                                     |   | PSI/PORT Score (Pneumonia)                        | Pneumonia mortality risk                       |
