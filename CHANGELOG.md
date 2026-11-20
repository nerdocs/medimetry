
# Changelog

uses semantic versioning


## [Unreleased]

## [0.3.0] - 2026-11-20

* Add laboratory.zlog: zlog value of a result against a two-sided reference interval (Hoffmann 2017)
* Input checks raise ValueError/TypeError instead of assert (asserts vanished under python -O)
* Drop the unused labunits dependency; ship py.typed; run the docstring doctests in the test suite
* Remove the cookiecutter bootstrap (ci/bootstrap.py, tox env bootstrap, jinja2 dev dependency)
* All results unrounded; keyword-only `rounded=True` rounds half up to the formula's customary places
* Add formulas.FORMULAS / formula(id): FormulaInfo per formula (UCUM units, input LOINC, digits, citation)
* Formulas raise ValueError below their published minimum age (eGFR equations and Cockcroft-Gault: 18 years)
* ckd_epi -> ckd_epi_2021; ckd_epi stays as a wrapper for the newest CKD-EPI creatinine equation
* Cystatin C equations are functions of their own: ckd_epi_2021_cystatin, ekfc_cystatin (cystatin_c argument removed)
* Remove bmi_with_category(_cm) and the import-time gettext titles (gfr/bmi/gcs/geneva *_titles)
* GCS: `glasgow_coma_scale` -> `gcs_score` (int only); `gcs_from_scores` returns int; new `gcs_category(score)`
* Child-Pugh: `child_pugh_score` returns the score only; new `child_pugh_category(score)` (Pugh 1973)
* Geneva: score functions return int; new `geneva_simplified_category` / `geneva_revised_category`; `GenevaScore` gone
* Framingham: `framingham_risk_score` -> `framingham_score`, `framingham_risk(points, gender)`, `framingham_category`
* Tests: Framingham age/treated-SBP bands and risk tables, WHO download path, `_lms_rows`; CKD-EPI values documented
* Add ckd_epi_2009: CKD-EPI 2009 creatinine equation (Levey 2009)

## [0.2.2] - 2026-11-01

* CI publishes tagged releases to PyPI via trusted publishing

## [0.2.1] - 2026-10-30

* Fix CI check job: exclude CLAUDE.md and uv.lock from sdist, taplo-lint without schema catalog

## [0.2.0] - 2026-10-30

* Add growth_value_at_percentile, growth_curves (AgeUnit, presets CHART_FIRST_YEAR / CHART_0_18_YEARS)
* Add ekfc: EKFC eGFR (Pottel 2021), optionally averaged with EKFC cystatin C (Pottel 2023)
* calcium_correction: use Payne 1973 as published (Ca - albumin + 4.0), was 0.8 x (4.0 - albumin)
* mdrd, ckd_epi, ekfc: reject Gender.DIVERSE instead of computing it as male
* Framingham: total cholesterol and HDL bands converted exactly from the published mg/dl values; cite CCS 2016
* FraminghamRiskLevel values are lowercase identifiers; GCS cites Rimel 1982, Child-Pugh INR marked unverified
* Add docs/references.md: verification status of the cited sources
* MDR wording: drop purpose column from README, neutral docstrings, disclaimer covers category sources and titles
* BMI and GCS titles use the wording of WHO TRS 894 ("Normal range", "Preobese") and Rimel 1982 ("Minor")
* cockcroft_gault: weight above 300 kg raises ValueError like bmi; dob2age uses the local date

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
