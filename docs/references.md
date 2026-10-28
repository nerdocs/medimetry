# References and source verification

Every public function cites its primary publication in the `References:` block of its docstring. This page records
how those sources were checked, and where an implementation deliberately deviates from or adds to the primary
publication.

Verification levels:

- **primary**: checked against the original paper (full text or abstract)
- **secondary**: checked against an independent implementation or a secondary publication quoting the original
- **unverified**: no primary source found

## Renal (`renal.py`)

### `ekfc`

- Creatinine: Pottel H, et al. Ann Intern Med. 2021;174(2):183-191. doi:10.7326/M20-4366 (**primary**).
  107.3, exponents −0.322 / −1.132, 0.990^(age − 40) above 40 years, ln(Q) polynomials for 2–25 years,
  Q = 80 / 62 µmol/l above 25 years (Figure 1).
- Cystatin C: Pottel H, et al. N Engl J Med. 2023;388(4):333-343. doi:10.1056/NEJMoa2203769 (**secondary**).
  Q = 0.83 mg/l below 50 years, 0.83 + 0.005 × (age − 50) above; same exponents as creatinine. Checked against
  Table 1 of PMC10345172 and the R package `nephro` (`EKFC_SF.cys`).
- Cystatin C in children: Pottel H, et al. Pediatr Nephrol. 2024;39(4):1177-1183. doi:10.1007/s00467-023-06192-6
  (**primary**, abstract). The adult Q of 0.83 mg/l applies to children as well; a 4th-degree age polynomial (used
  by `nephro`) performed equally. The library uses 0.83 mg/l.
- Combined: arithmetic mean of the creatinine and the cystatin C equation (Pottel 2023, Pottel 2024).
- Creatinine is converted to µmol/l (× 88.4) because Q is published in µmol/l. Calculators using the rounded mg/dl
  values (0.90 / 0.70) differ by about 0.5 %.

## Cardiovascular (`cardiovasc.py`)

### `framingham_risk_score`

- Points and risk: D'Agostino RB Sr, et al. Circulation. 2008;117(6):743-753.
  doi:10.1161/CIRCULATIONAHA.107.699579 (**secondary**). Total and HDL cholesterol are taken in mmol/l and
  converted with 38.67 to the published mg/dl bands (total cholesterol 160/200/240/280, HDL 35/45/50/60 mg/dl).
- Risk level: Anderson TJ, et al. Can J Cardiol. 2016;32(11):1263-1282. doi:10.1016/j.cjca.2016.07.510
  (**primary**, guideline summary). Not part of D'Agostino 2008: low < 10 %, intermediate 10–19 %, high ≥ 20 %.

## Electrolytes (`lytes.py`)

### `calcium_correction`

- Payne RB, et al. Br Med J. 1973;4(5893):643-646. doi:10.1136/bmj.4.5893.643 (**primary**, abstract).
  "Adjusted calcium = calcium − albumin + 4.0" (mg/100 ml, g/100 ml). The common 0.8 × (4.0 − albumin) variant is
  not Payne's formula.

## Metabolic (`metabolic.py`)

### `child_pugh_score`

- Pugh RN, et al. Br J Surg. 1973;60(8):646-649. doi:10.1002/bjs.1800600817 (**secondary**). Pugh grades the
  prothrombin time prolongation in seconds (< 4, 4–6, > 6 s).
- INR bands < 1.7 / 1.7–2.3 / > 2.3 (**unverified**): widely used, but no primary source was found. Durand & Valla
  2005 (J Hepatol 42 Suppl 1:S100-107), often cited for them, lists the prothrombin time in seconds.

## Neurological (`neuro.py`)

### `glasgow_coma_scale`

- Teasdale G, Jennett B. Lancet. 1974;2(7872):81-84. doi:10.1016/s0140-6736(74)91639-0 (**secondary**).
  Component scores and sum.
- Category: Rimel RW, et al. Neurosurgery. 1982;11(3):344-351. doi:10.1227/00006123-198209000-00002 (**primary**,
  abstract). Not part of Teasdale 1974: "severe, 3-8; moderate, 9-12; and minor, 13-15".

## Other modules

The remaining formulas (Cockcroft-Gault, MDRD, CKD-EPI 2021, KDIGO staging, ACR, MAP, CHA₂DS₂-VASc, BMI and WHO
classes, BSA formulas, QTc, Simplified and Revised Geneva, PERC, LMS growth math) were checked against secondary
sources in an audit in October 2026 without findings. They have not been re-checked against the primary papers yet.
