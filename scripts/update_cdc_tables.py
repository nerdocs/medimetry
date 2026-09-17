#
# Downloads the CDC 2000 Growth Charts LMS data files (public domain, US Government work) and converts them into
# the canonical ``key;L;M;S`` tables under src/medimetry/data/cdc/.
#
# Run from the repository root: PYTHONPATH=src python scripts/update_cdc_tables.py
#
# Source: https://www.cdc.gov/growthcharts/cdc-data-files.htm
import csv
from pathlib import Path
from urllib.request import urlopen

from medimetry.constants import Gender
from medimetry.growth import DAYS_PER_MONTH
from medimetry.growth import GrowthIndicator
from medimetry.growth import write_canonical_table

BASE_URL = "https://www.cdc.gov/growthcharts/data/zscore"
TARGET_DIR = Path(__file__).parent.parent / "src" / "medimetry" / "data" / "cdc"

# (raw file name, indicator, key column, key factor, upper key limit (exclusive) or None)
SOURCES = [
    ("wtageinf", GrowthIndicator.WEIGHT_FOR_AGE, "Agemos", DAYS_PER_MONTH, 24),
    ("wtage", GrowthIndicator.WEIGHT_FOR_AGE, "Agemos", DAYS_PER_MONTH, None),
    ("lenageinf", GrowthIndicator.LENGTH_HEIGHT_FOR_AGE, "Agemos", DAYS_PER_MONTH, 24),
    ("statage", GrowthIndicator.LENGTH_HEIGHT_FOR_AGE, "Agemos", DAYS_PER_MONTH, None),
    ("bmiagerev", GrowthIndicator.BMI_FOR_AGE, "Agemos", DAYS_PER_MONTH, None),
    ("hcageinf", GrowthIndicator.HEAD_CIRCUMFERENCE_FOR_AGE, "Agemos", DAYS_PER_MONTH, None),
    ("wtleninf", GrowthIndicator.WEIGHT_FOR_LENGTH, "Length", 1.0, None),
    ("wtstat", GrowthIndicator.WEIGHT_FOR_HEIGHT, "Height", 1.0, None),
]

SEX = {"1": Gender.MALE, "2": Gender.FEMALE}


def main() -> None:
    collected: dict[tuple[GrowthIndicator, Gender], list[tuple[float, float, float, float]]] = {}
    for name, indicator, key_column, key_factor, limit in SOURCES:
        print(f"Downloading {name}.csv ...")
        with urlopen(f"{BASE_URL}/{name}.csv", timeout=60) as response:  # noqa: S310
            text = response.read().decode("utf-8-sig")
        for row in csv.DictReader(text.splitlines()):
            if row[key_column] == key_column:  # some files repeat the header row between the sexes
                continue
            key = float(row[key_column])
            if limit is not None and key >= limit:
                continue
            collected.setdefault((indicator, SEX[row["Sex"]]), []).append(
                (key * key_factor, float(row["L"]), float(row["M"]), float(row["S"]))
            )

    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    for (indicator, gender), rows in collected.items():
        path = TARGET_DIR / f"{indicator.value}_{gender.value}.csv"
        write_canonical_table(path, rows)
        print(f"✓ {path.name}: {len(rows)} rows")


if __name__ == "__main__":
    main()
