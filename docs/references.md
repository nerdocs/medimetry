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

### `ckd_epi_2009`

- Levey AS, et al. Ann Intern Med. 2009;150(9):604-612. doi:10.7326/0003-4819-150-9-200905050-00006 (**secondary**).
  The tests check the single formula against the sex- and creatinine-specific forms of Table 2 (144 / 141, 166 / 163
  for Black patients); the full text was not re-checked when this entry was written.

### `kfre_2_year`, `kfre_5_year`

- Tangri N, et al. JAMA. 2016;315(2):164-174. doi:10.1001/jama.2015.18202, eAppendix 2 (**secondary**). The
  supplement was not accessible. Coefficients, centering values and the non-North American baseline survival
  (0.9832 / 0.9365) were checked against the verbatim reproduction "as provided in the KFRE eAppendix 2" in the
  supplement of Ramspek CL, et al. J Am Soc Nephrol. 2021;32(5). doi:10.1681/ASN.2020071077, which also
  gives the units (ACR in mg/g); the North American baseline survival (0.9750 / 0.9240) against the formula text
  of the LOINC terms 85624-5 and 85625-2, which also states the natural logarithm and male = 1, female = 0.
- Development of the equation: Tangri N, et al. JAMA. 2011;305(15):1553-1559. doi:10.1001/jama.2011.451. The
  library implements the pooled, regionally calibrated equations of 2016, not the 2011 equations.
- Domain: adults with CKD stages 3-5; the functions raise for an eGFR of 60 mL/min/1.73m² or more and below 18
  years. There is no default region.
- LOINC 85624-5 / 85625-2 ("Kidney failure 2-year / 5-year risk [Likelihood] by KFRE", %): the formula text of
  the terms shows the North American baseline survival. The library gives the same codes for either region; a
  consumer has to store the region beside the value.
- Only the 4-variable equation is implemented. The 8-variable equation (albumin, phosphate, bicarbonate,
  calcium) is left out until its North American baseline survival is verified: secondary sources disagree.

## Laboratory (`laboratory.py`)

### `zlog`

- Hoffmann G, et al. LaboratoriumsMedizin. 2017;41(1):23-32. doi:10.1515/labmed-2016-0087 (**secondary**). The
  full text was not accessible; the formula was checked against the R package `zlog` (CRAN, `z()`/`zlog()`) and the
  KBV MIO *Laborbefund* page "zlog-Wert", and the results against Cadamuro J, et al. Crit Rev Clin Lab Sci. 2021,
  Figure 6, which plots zlog values for a blood count.
- One-sided intervals: no zlog. The R package's `set_missing_limits()` substitutes LL = 0.15 × UL after Haeckel
  2015; Hoffmann (KBV MIO comment, July 2022) calls zlog not computable without a real lower limit. The library
  follows Hoffmann and rejects a lower limit of 0.

## Cardiovascular (`cardiovasc.py`)

### `framingham_score`, `framingham_risk`, `framingham_category`

- Points (`framingham_score`) and 10-year risk (`framingham_risk`): D'Agostino RB Sr, et al. Circulation.
  2008;117(6):743-753. doi:10.1161/CIRCULATIONAHA.107.699579 (**secondary**). The full text was not accessible
  (403); every point band and both risk tables were checked against a verbatim reproduction citing Tables 5–8 of
  the paper: Novartis statistical analysis plan CABL001J12301, SAP Amendment 2, section 5.5.1, Tables 5-3 to 5-6
  (clinicaltrials.gov NCT04971226), which also gives a worked example (woman, 43 y, 7 points). Total and HDL
  cholesterol are taken in mmol/l and converted with 38.67 to the published mg/dl bands (total cholesterol
  160/200/240/280, HDL 35/45/50/60 mg/dl).
- Risk level (`framingham_category`): Anderson TJ, et al. Can J Cardiol. 2016;32(11):1263-1282.
  doi:10.1016/j.cjca.2016.07.510 (**primary**, guideline summary). Not part of D'Agostino 2008: low < 10 %,
  intermediate 10–19 %, high ≥ 20 %.

## Electrolytes (`lytes.py`)

### `calcium_correction`

- Payne RB, et al. Br Med J. 1973;4(5893):643-646. doi:10.1136/bmj.4.5893.643 (**primary**, abstract).
  "Adjusted calcium = calcium − albumin + 4.0" (mg/100 ml, g/100 ml). The common 0.8 × (4.0 − albumin) variant is
  not Payne's formula.

## Metabolic (`metabolic.py`)

### `child_pugh_score`, `child_pugh_category`

- Pugh RN, et al. Br J Surg. 1973;60(8):646-649. doi:10.1002/bjs.1800600817 (**secondary**). Pugh grades the
  prothrombin time prolongation in seconds (< 4, 4–6, > 6 s). Grades (`child_pugh_category`): A 5–6, B 7–9,
  C 10–15.
- INR bands < 1.7 / 1.7–2.3 / > 2.3 (**unverified**): widely used, but no primary source was found. Durand & Valla
  2005 (J Hepatol 42 Suppl 1:S100-107), often cited for them, lists the prothrombin time in seconds.

## Neurological (`neuro.py`)

### `gcs_score`, `gcs_from_scores`, `gcs_category`

- Teasdale G, Jennett B. Lancet. 1974;2(7872):81-84. doi:10.1016/s0140-6736(74)91639-0 (**secondary**).
  Component scores and sum (`gcs_score`, `gcs_from_scores`).
- Category (`gcs_category`): Rimel RW, et al. Neurosurgery. 1982;11(3):344-351.
  doi:10.1227/00006123-198209000-00002 (**primary**, abstract). Not part of Teasdale 1974: "severe, 3-8; moderate, 9-12; and minor, 13-15".

## Anthropometric (`anthropometric.py`)

### `bmi_category`

- WHO. Obesity: preventing and managing the global epidemic. WHO Technical Report Series 894. Geneva: WHO; 2000
  (**primary**, Table 2.1). Titles follow the table: "Normal range", "Preobese" (25.00–29.99, the code's
  `OVERWEIGHT`), "Obese class I–III".

## Other modules

The remaining formulas (Cockcroft-Gault, MDRD, CKD-EPI 2021, KDIGO staging, ACR, MAP, CHA₂DS₂-VASc, BSA formulas,
QTc, Simplified and Revised Geneva, PERC, LMS growth math) were checked against secondary sources in an audit in
October 2026 without findings. They have not been re-checked against the primary papers yet.
