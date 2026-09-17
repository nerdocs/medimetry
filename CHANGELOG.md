
# Changelog

uses semantic versioning


## [0.1.0] - 2026-09-17

* ACR: urine albumin/creatinine in mg/g (was a unitless ratio, 1000x off vs. KDIGO thresholds)
* ckd_stage: third element is now the KDIGO heat-map risk category (1-4); "checks per year" removed
* Framingham: fix HDL point bands (1.2-1.29 = 0, 0.9-1.19 = +1), men's 15-point risk 21.6 %, cite D'Agostino 2008
* Geneva: rewrite geneva_score as geneva_simplified_score (Klok 2008); fix revised score (Le Gal 2006) double item
* GCS: raise ValueError instead of summing a NOT_TESTABLE component
* PERC: drop recommendation text and __bool__; rename hormone_use to exogenous_estrogen
* dob2age_tuple: no negative days when the previous month is shorter than the day deficit
* Move calcium_correction to lytes.py; cockcroft_gault returns float; fix error messages and docstring units
* Enum values are plain identifiers; translated titles live in *_titles dicts
* Add DISCLAIMER.md, intended-use statement, literature references per function; classifier Alpha
* Remove labunits tests; labunits stays the single runtime dependency
* Add growth charts (growth.py): LMS z-score/percentile, CDC 2000 bundled, WHO 2006/2007 via download_who_tables
* download_who_tables raises WhoDownloadError listing every failed URL with HTTP status
* Remove bundled WHO tables from the package and from git history (WHO license is CC BY-NC-SA, not MIT-compatible)

## [0.0.1] - 2025-10-03

* First release
* basic implementation of some formulas as functions, index of planned functions
