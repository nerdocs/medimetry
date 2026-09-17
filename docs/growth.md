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

## Percentile curves for plotting

`growth_value_at_percentile` inverts the LMS formula (value = M · (1 + L·S·z)^(1/L), or M · exp(S·z) if L = 0)
and returns the measurement on a given percentile at a given age or length. `growth_curves` samples that for a
set of percentiles and returns plain lists, ready to serialize as JSON for any charting library. The drawing
itself (axes, grid, labels) belongs to the application, not to medimetry.

```python
from medimetry.growth import AgeUnit, GrowthIndicator, growth_curves

curves = growth_curves(
    GrowthIndicator.WEIGHT_FOR_AGE, Gender.FEMALE,
    percentiles=(3, 10, 25, 50, 75, 90, 97),
    age_unit=AgeUnit.MONTHS, start=0, end=12, step=0.25,
)
curves.keys          # [0.0, 0.25, 0.5, ...] months
curves.curves[50.0]  # median weight in kg at each key
curves.age_unit      # AgeUnit.MONTHS (None for weight-for-length / -height, where keys are cm)
```

### Chart presets and percentile sets

Printed chart sheets follow a few conventions (WHO 2006/2007 sheets, CDC 2000 clinical charts, Kromeyer-Hauschild
sheets used in the German U-Heft; Austria uses the WHO curves below 5 years):

| Convention               | Sheets                           | Lines (P50 bold except CDC) | Constant                 |
|--------------------------|----------------------------------|-----------------------------|--------------------------|
| WHO                      | 0–6 mo (weeks), 0–2, 0–5, 5–19 y | 3, 15, 50, 85, 97           | `PERCENTILES_WHO`        |
| CDC birth–36 months      | one sheet, 3-month ticks         | 5, 10, 25, 50, 75, 90, 95   | `PERCENTILES_CDC_INFANT` |
| CDC 2–20 y, DACH (KH)    | one sheet, yearly ticks          | 3, 10, 25, 50, 75, 90, 97   | `DEFAULT_PERCENTILES`    |

Two sampling presets cover the layouts most applications need; unpack them into `growth_curves`:

```python
from medimetry.growth import CHART_0_18_YEARS, CHART_FIRST_YEAR, PERCENTILES_WHO

growth_curves(GrowthIndicator.WEIGHT_FOR_AGE, Gender.MALE, **CHART_FIRST_YEAR)   # weeks 0–52, weekly
growth_curves(GrowthIndicator.LENGTH_HEIGHT_FOR_AGE, Gender.MALE, percentiles=PERCENTILES_WHO, **CHART_0_18_YEARS)
```

`CHART_FIRST_YEAR` samples weeks 0–52 (53 points); `CHART_0_18_YEARS` samples years 0–18 monthly (217 points).
Drawing conventions worth copying in the application: emphasize the median line, label each line at its right end,
put a vertical marker at 2 years on length/height-for-age (recumbent length below, standing height above), and use
a fine minor grid (0.5 kg, 1 cm) under labeled major gridlines.

- `start`, `end` and `step` are in `age_unit` (`DAYS`, `WEEKS`, `MONTHS`, `YEARS`); for the length-keyed
  indicators they are in cm and `age_unit` is ignored.
- Without `step` the table rows are returned unchanged (CDC: half-monthly, WHO: daily below 5 years, monthly
  above). With `step` the curves are sampled uniformly using the same interpolation as `growth_zscore`, so the
  resolution is independent of the table.
- `start` / `end` are clamped to the table coverage. Asking WHO weight-for-age for 0–18 years returns 0–10 years;
  inspect `keys` when the range matters.
- The percentile at a given key is undefined if `1 + L·S·z <= 0` (only for extreme percentiles with strongly
  negative L); `growth_value_at_percentile` raises `ValueError` then.

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
