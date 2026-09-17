# Growth charts (`medimetry.growth`)

z-scores and percentiles for pediatric growth indicators, computed with the LMS method (Cole & Green 1992) from
reference tables. Two references share one API and one table format, selectable with `GrowthReference`.

## References

| `GrowthReference` | Source                                                  | Age range | Shipped?                  |
|-------------------|---------------------------------------------------------|-----------|---------------------------|
| `CDC`             | CDC 2000 Growth Charts (Kuczmarski 2002), public domain | 0–20 y    | yes, `data/cdc/`          |
| `WHO`             | WHO Child Growth Standards 2006 + Growth Reference 2007 | 0–19 y    | no, user downloads        |

WHO tables are published under CC BY-NC-SA 3.0 IGO / WHO terms of use, which exclude commercial use without
permission. They cannot be redistributed in this MIT-licensed package. `download_who_tables(target_dir)` fetches
the 18 z-score workbooks from who.int and converts them into the canonical layout; by running it you accept WHO's
terms yourself.

## Indicators

| `GrowthIndicator`            | Unit of `value` | Key          | CDC coverage       | WHO coverage      |
|------------------------------|-----------------|--------------|--------------------|-------------------|
| `WEIGHT_FOR_AGE`             | kg              | `age_days`   | 0–20 y             | 0–10 y            |
| `LENGTH_HEIGHT_FOR_AGE`      | cm              | `age_days`   | 0–20 y             | 0–19 y            |
| `BMI_FOR_AGE`                | kg/m²           | `age_days`   | 2–20 y             | 0–19 y            |
| `HEAD_CIRCUMFERENCE_FOR_AGE` | cm              | `age_days`   | 0–36 months        | 0–5 y             |
| `WEIGHT_FOR_LENGTH`          | kg              | `length_cm`  | 45–103.5 cm        | 45–110 cm         |
| `WEIGHT_FOR_HEIGHT`          | kg              | `length_cm`  | 77–121.5 cm        | 65–120 cm         |

Weight-for-length (recumbent, infants) and weight-for-height (standing) are distinct tables in both sources and
overlap in their key ranges, hence two indicators.

## Usage

```python
from pathlib import Path

from medimetry import Gender
from medimetry.growth import DAYS_PER_MONTH, GrowthIndicator, GrowthReference, download_who_tables
from medimetry.growth import growth_percentile, growth_zscore

# CDC (bundled)
z = growth_zscore(GrowthIndicator.WEIGHT_FOR_AGE, Gender.MALE, value=12.7, age_days=24.5 * DAYS_PER_MONTH)
p = growth_percentile(GrowthIndicator.WEIGHT_FOR_AGE, Gender.MALE, value=12.7, age_days=24.5 * DAYS_PER_MONTH)

# WHO (download once, then pass the directory)
who_dir = Path("~/.cache/medimetry/who").expanduser()
download_who_tables(who_dir)
z = growth_zscore(
    GrowthIndicator.LENGTH_HEIGHT_FOR_AGE, Gender.FEMALE, value=110.0, age_days=5 * 365.25,
    reference=GrowthReference.WHO, data_dir=who_dir,
)
```

Exactly one of `age_days` / `length_cm` must be given, and it must match the indicator.

`download_who_tables` tries all 18 WHO URLs and then raises a single `WhoDownloadError` if any failed. Its
`failures` attribute lists `(url, http_status, reason)` per failed download (`http_status` is `None` for network
errors), so a changed or restricted WHO download location shows up as one structured error, e.g. `403 Forbidden`.
Nothing is written in that case.

## Conventions and limitations

- **Age unit is days.** Table keys given in months by CDC and WHO are converted with 1 month = 30.4375 days
  (365.25 / 12). Pass `months * DAYS_PER_MONTH` for ages in months.
- **Linear interpolation** of L, M and S between the two adjacent table rows. Keys outside the table range raise
  `ValueError`; there is no extrapolation.
- **`growth_zscore` returns the raw, unrounded float.** Unlike the other modules (which round their results), the
  z-score is meant for further computation and plotting, so rounding is left to the caller. `growth_percentile`
  is rounded to one decimal place.
- **Plain LMS only.** WHO's adjusted z-scores for weight-based indicators (values beyond ±3 SD are recomputed
  relative to the SD2/SD3 distance) and CDC's 2022 extended BMI z-scores above the 95th percentile are *not*
  applied. Results beyond ±3 SD therefore differ from WHO Anthro / CDC tools in those regions.
- No categories or interpretation (stunting, wasting, obesity classes) are returned; see `DISCLAIMER.md`.

## Table format

One CSV per reference, indicator and sex: `<indicator>_<m|f>.csv`, header `key;L;M;S`, semicolon-separated,
keys strictly increasing. CDC tables are regenerated with `PYTHONPATH=src python scripts/update_cdc_tables.py`;
WHO tables are written by `download_who_tables`. Both go through `write_canonical_table`, so the layouts are
identical by construction.
