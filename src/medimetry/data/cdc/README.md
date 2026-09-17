# CDC 2000 Growth Charts — LMS reference tables

Source: https://www.cdc.gov/growthcharts/cdc-data-files.htm (raw files under
`https://www.cdc.gov/growthcharts/data/zscore/<name>.csv`), downloaded 2026-09-17.

Citation: Kuczmarski RJ, Ogden CL, Guo SS, et al. 2000 CDC Growth Charts for the United States: methods and
development. Vital Health Stat 11. 2002;(246):1-190.

License: work of the United States Government (National Center for Health Statistics, CDC), public domain.
"All material appearing in this report is in the public domain and may be reproduced or copied without permission;
citation as to source, however, is appreciated."

## Layout

One file per indicator and sex, `<indicator>_<m|f>.csv`, header `key;L;M;S`, semicolon-separated:

| file     | indicator                  | key                                    | raw CDC files                     |
|----------|----------------------------|----------------------------------------|-----------------------------------|
| `wfa_*`  | weight-for-age             | age in days (Agemos × 30.4375), 0–20 y | `wtageinf` (< 24 mo) + `wtage`    |
| `lhfa_*` | length/height-for-age      | age in days, 0–20 y                    | `lenageinf` (< 24 mo) + `statage` |
| `bfa_*`  | BMI-for-age                | age in days, 2–20 y                    | `bmiagerev`                       |
| `hcfa_*` | head circumference-for-age | age in days, 0–36 mo                   | `hcageinf`                        |
| `wfl_*`  | weight-for-length          | recumbent length in cm, 45–103.5       | `wtleninf`                        |
| `wfh_*`  | weight-for-height          | standing height in cm, 77–121.5        | `wtstat`                          |

Only the L, M, S columns are kept; the CDC percentile columns are derived values and are not carried over.

Regenerate with `PYTHONPATH=src python scripts/update_cdc_tables.py` from the repository root.
