"""
Pediatric growth charts: z-scores and percentiles from LMS reference tables.

Two reference datasets are supported behind one API:

* ``GrowthReference.CDC`` - CDC 2000 Growth Charts (US Government work, public domain), bundled with the package.
* ``GrowthReference.WHO`` - WHO Child Growth Standards 2006 (0-5 years) and WHO Growth Reference 2007
  (5-19 years). These are licensed CC BY-NC-SA / WHO terms of use and are therefore NOT bundled. Call
  ``download_who_tables(target_dir)`` once; it fetches the WHO workbooks and converts them into the same canonical
  CSV layout the CDC tables use.

Canonical table layout: one CSV per (reference, indicator, sex) named ``<indicator>_<m|f>.csv`` with the header
``key;L;M;S``. The key is age in days for age-based indicators (1 month = 30.4375 days) or length/height in cm.
"""

import csv
import math
import zipfile
from bisect import bisect_left
from collections.abc import Iterable
from enum import Enum
from functools import lru_cache
from importlib import resources
from io import BytesIO
from itertools import pairwise
from pathlib import Path
from urllib.error import HTTPError
from urllib.error import URLError
from urllib.request import Request
from urllib.request import urlopen
from xml.etree import ElementTree

from medimetry.constants import Gender

DAYS_PER_MONTH = 30.4375  # 365.25 / 12


class WhoDownloadError(Exception):
    """
    Raised by ``download_who_tables`` when one or more WHO workbooks could not be fetched.

    Attributes:
        failures (list[tuple[str, int | None, str]]): ``(url, http_status, reason)`` per failed download;
            ``http_status`` is None for network-level errors (DNS, timeout, connection refused).
    """

    def __init__(self, failures: list[tuple[str, int | None, str]]):
        self.failures = failures
        lines = [f"  {status if status is not None else '-'} {reason}: {url}" for url, status, reason in failures]
        super().__init__(f"{len(failures)} WHO download(s) failed (WHO may have moved or restricted the files):\n" + "\n".join(lines))


class GrowthReference(Enum):
    """Reference dataset used for growth chart computations."""

    CDC = "cdc"
    WHO = "who"


class GrowthIndicator(Enum):
    """Growth chart indicators. Weight-for-length (recumbent) and weight-for-height (standing) are separate tables."""

    WEIGHT_FOR_AGE = "wfa"
    LENGTH_HEIGHT_FOR_AGE = "lhfa"
    BMI_FOR_AGE = "bfa"
    HEAD_CIRCUMFERENCE_FOR_AGE = "hcfa"
    WEIGHT_FOR_LENGTH = "wfl"
    WEIGHT_FOR_HEIGHT = "wfh"


_LENGTH_KEYED = {GrowthIndicator.WEIGHT_FOR_LENGTH, GrowthIndicator.WEIGHT_FOR_HEIGHT}

_CANONICAL_HEADER = ["key", "L", "M", "S"]


def write_canonical_table(path: Path, rows: Iterable[tuple[float, float, float, float]]) -> None:
    """
    Write LMS rows as a canonical ``key;L;M;S`` CSV table, sorted by key.

    Args:
        path (Path): Target CSV file
        rows (Iterable[tuple]): ``(key, L, M, S)`` tuples; keys must be unique
    """
    sorted_rows = sorted(rows, key=lambda r: r[0])
    for previous, current in pairwise(sorted_rows):
        assert previous[0] < current[0], f"Duplicate key {current[0]} in {path}"
    with path.open("w", newline="") as f:
        writer = csv.writer(f, delimiter=";", lineterminator="\n")
        writer.writerow(_CANONICAL_HEADER)
        for row in sorted_rows:
            writer.writerow([str(float(v)) for v in row])


def _parse_table(text: str) -> tuple[list[float], list[tuple[float, float, float]]]:
    reader = csv.reader(text.splitlines(), delimiter=";")
    header = next(reader)
    assert header == _CANONICAL_HEADER, f"Unexpected header {header}"
    keys: list[float] = []
    lms: list[tuple[float, float, float]] = []
    for row in reader:
        keys.append(float(row[0]))
        lms.append((float(row[1]), float(row[2]), float(row[3])))
    return keys, lms


@lru_cache
def _load_table(
    reference: GrowthReference, indicator: GrowthIndicator, gender: Gender, data_dir: Path | None
) -> tuple[list[float], list[tuple[float, float, float]]]:
    filename = f"{indicator.value}_{gender.value}.csv"
    if reference == GrowthReference.CDC:
        text = (resources.files("medimetry") / "data" / "cdc" / filename).read_text()
    else:
        if data_dir is None:
            raise ValueError("data_dir is required for GrowthReference.WHO (see download_who_tables)")
        path = Path(data_dir) / filename
        if not path.is_file():
            raise FileNotFoundError(f"{path} not found - run medimetry.growth.download_who_tables(target_dir) first")
        text = path.read_text()
    return _parse_table(text)


def _lms_at(keys: list[float], lms: list[tuple[float, float, float]], x: float) -> tuple[float, float, float]:
    """Linearly interpolate (L, M, S) at key x; raise ValueError outside the table range."""
    if x < keys[0] or x > keys[-1]:
        raise ValueError(f"Key {x} outside reference table range {keys[0]}-{keys[-1]}")
    i = bisect_left(keys, x)
    if keys[i] == x:
        return lms[i]
    x0, x1 = keys[i - 1], keys[i]
    t = (x - x0) / (x1 - x0)
    return tuple(a + t * (b - a) for a, b in zip(lms[i - 1], lms[i], strict=True))  # type: ignore[return-value]


def _lms_zscore(value: float, l: float, m: float, s: float) -> float:  # noqa: E741
    if l == 0:
        return math.log(value / m) / s
    return ((value / m) ** l - 1) / (l * s)


def _zscore(
    indicator: GrowthIndicator,
    gender: Gender,
    value: float,
    age_days: float | None,
    length_cm: float | None,
    reference: GrowthReference,
    data_dir: Path | None,
) -> float:
    assert isinstance(indicator, GrowthIndicator), "indicator must be a GrowthIndicator"
    assert isinstance(reference, GrowthReference), "reference must be a GrowthReference"
    assert gender in (Gender.MALE, Gender.FEMALE), "Gender must be Gender.MALE or Gender.FEMALE"
    if value <= 0:
        raise ValueError("Measured value must be positive")
    if (age_days is None) == (length_cm is None):
        raise ValueError("Exactly one of age_days or length_cm must be given")
    if indicator in _LENGTH_KEYED:
        if length_cm is None:
            raise ValueError(f"{indicator.name} is keyed by length_cm, not age_days")
        key = length_cm
    else:
        if age_days is None:
            raise ValueError(f"{indicator.name} is keyed by age_days, not length_cm")
        key = age_days

    keys, lms = _load_table(reference, indicator, gender, data_dir)
    return _lms_zscore(value, *_lms_at(keys, lms, key))


def growth_zscore(
    indicator: GrowthIndicator,
    gender: Gender,
    *,
    value: float,
    age_days: float | None = None,
    length_cm: float | None = None,
    reference: GrowthReference = GrowthReference.CDC,
    data_dir: Path | None = None,
) -> float:
    """
    Calculate the z-score of a measurement against a growth reference using the LMS method.

    z = ((value / M)^L - 1) / (L x S), or ln(value / M) / S if L = 0. L, M and S are linearly interpolated
    between the two adjacent table rows. Plain LMS only: no WHO adjusted z-scores (capping beyond +-3 SD) and no
    CDC extended BMI z-scores are applied. The result is returned unrounded.

    References:
        Cole TJ, Green PJ. Smoothing reference centile curves: the LMS method and penalized likelihood.
        Stat Med. 1992;11(10):1305-1319. doi:10.1002/sim.4780111005
        Kuczmarski RJ, et al. 2000 CDC Growth Charts for the United States: methods and development.
        Vital Health Stat 11. 2002;(246):1-190.
        WHO Multicentre Growth Reference Study Group. WHO Child Growth Standards: Length/height-for-age,
        weight-for-age, weight-for-length, weight-for-height and body mass index-for-age. Geneva: WHO; 2006.
        de Onis M, et al. Development of a WHO growth reference for school-aged children and adolescents.
        Bull World Health Organ. 2007;85(9):660-667. doi:10.2471/BLT.07.043497

    Args:
        indicator (GrowthIndicator): Which growth chart to use
        gender (Gender): Gender.MALE or Gender.FEMALE
        value (float): Measured value in the indicator's unit (kg, cm or kg/m²)
        age_days (float, optional): Age in days; required for age-based indicators. For ages given in months
            multiply by DAYS_PER_MONTH (30.4375).
        length_cm (float, optional): Recumbent length or standing height in cm; required for
            WEIGHT_FOR_LENGTH / WEIGHT_FOR_HEIGHT
        reference (GrowthReference): GrowthReference.CDC (bundled) or GrowthReference.WHO (user-downloaded)
        data_dir (Path, optional): Directory holding the WHO tables written by ``download_who_tables``

    Returns:
        float: z-score (standard deviation score), unrounded

    Raises:
        ValueError: If the value is not positive, the key argument is missing, mismatched or outside the table
        FileNotFoundError: If the WHO table has not been downloaded into ``data_dir``

    >>> round(growth_zscore(GrowthIndicator.WEIGHT_FOR_AGE, Gender.MALE, age_days=24.5 * DAYS_PER_MONTH, value=15.68840631), 2)
    1.88
    """
    return _zscore(indicator, gender, value, age_days, length_cm, reference, data_dir)


def growth_percentile(
    indicator: GrowthIndicator,
    gender: Gender,
    *,
    value: float,
    age_days: float | None = None,
    length_cm: float | None = None,
    reference: GrowthReference = GrowthReference.CDC,
    data_dir: Path | None = None,
) -> float:
    """
    Calculate the percentile of a measurement against a growth reference.

    The percentile is the standard normal cumulative distribution of the LMS z-score (see ``growth_zscore`` for
    arguments, references and limitations).

    Returns:
        float: Percentile in the range 0-100, rounded to 1 decimal place

    >>> growth_percentile(GrowthIndicator.WEIGHT_FOR_AGE, Gender.MALE, age_days=24.5 * DAYS_PER_MONTH, value=12.74154396)
    50.0
    """
    z = _zscore(indicator, gender, value, age_days, length_cm, reference, data_dir)
    return round(50 * (1 + math.erf(z / math.sqrt(2))), 1)


# --- WHO download -------------------------------------------------------------------------------------------------

_WHO_0_5 = "https://cdn.who.int/media/docs/default-source/child-growth/child-growth-standards/indicators"
_WHO_5_19 = "https://cdn.who.int/media/docs/default-source/child-growth/growth-reference-5-19-years"

# (indicator, gender, url, key column name, key factor to days/cm)
_WHO_SOURCES: list[tuple[GrowthIndicator, Gender, str, str, float]] = []
for _sex, _gender in (("boys", Gender.MALE), ("girls", Gender.FEMALE)):
    _WHO_SOURCES += [
        (
            GrowthIndicator.WEIGHT_FOR_AGE,
            _gender,
            f"{_WHO_0_5}/weight-for-age/expanded-tables/wfa-{_sex}-zscore-expanded-tables.xlsx",
            "Day",
            1.0,
        ),
        (
            GrowthIndicator.LENGTH_HEIGHT_FOR_AGE,
            _gender,
            f"{_WHO_0_5}/length-height-for-age/expandable-tables/lhfa-{_sex}-zscore-expanded-tables.xlsx",
            "Day",
            1.0,
        ),
        (
            GrowthIndicator.BMI_FOR_AGE,
            _gender,
            f"{_WHO_0_5}/body-mass-index-for-age/expanded-tables/bfa-{_sex}-zscore-expanded-tables.xlsx",
            "Day",
            1.0,
        ),
        (
            GrowthIndicator.HEAD_CIRCUMFERENCE_FOR_AGE,
            _gender,
            f"{_WHO_0_5}/head-circumference-for-age/expanded-tables/hcfa-{_sex}-zscore-expanded-tables.xlsx",
            "Day",
            1.0,
        ),
        (
            GrowthIndicator.WEIGHT_FOR_LENGTH,
            _gender,
            f"{_WHO_0_5}/weight-for-length-height/expanded-tables/wfl-{_sex}-zscore-expanded-table.xlsx",
            "Length",
            1.0,
        ),
        (
            GrowthIndicator.WEIGHT_FOR_HEIGHT,
            _gender,
            f"{_WHO_0_5}/weight-for-length-height/expanded-tables/wfh-{_sex}-zscore-expanded-tables.xlsx",
            "Height",
            1.0,
        ),
        (
            GrowthIndicator.LENGTH_HEIGHT_FOR_AGE,
            _gender,
            f"{_WHO_5_19}/height-for-age-(5-19-years)/hfa-{_sex}-z-who-2007-exp.xlsx",
            "Month",
            DAYS_PER_MONTH,
        ),
        (
            GrowthIndicator.BMI_FOR_AGE,
            _gender,
            f"{_WHO_5_19}/bmi-for-age-(5-19-years)/bmi-{_sex}-z-who-2007-exp.xlsx",
            "Month",
            DAYS_PER_MONTH,
        ),
    ]
# The 5-10 y weight-for-age workbooks are misnamed "hfa-*" on WHO's server; their content is weight-for-age.
_WHO_SOURCES += [
    (
        GrowthIndicator.WEIGHT_FOR_AGE,
        Gender.MALE,
        f"{_WHO_5_19}/weight-for-age-(5-10-years)/hfa-boys-z-who-2007-exp_0ff9c43c-8cc0-4c23-9fc6-81290675e08b.xlsx",
        "Month",
        DAYS_PER_MONTH,
    ),
    (
        GrowthIndicator.WEIGHT_FOR_AGE,
        Gender.FEMALE,
        f"{_WHO_5_19}/weight-for-age-(5-10-years)/hfa-girls-z-who-2007-exp_7ea58763-36a2-436d-bef0-7fcfbadd2820.xlsx",
        "Month",
        DAYS_PER_MONTH,
    ),
]

_XLSX_NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
# cdn.who.int answers 403 to the default urllib user agent
_USER_AGENT = "medimetry (+https://github.com/nerdocs/medimetry)"


def _column_index(cell_ref: str) -> int:
    """Convert an A1-style cell reference to a 0-based column index."""
    index = 0
    for char in cell_ref:
        if not char.isalpha():
            break
        index = index * 26 + ord(char.upper()) - ord("A") + 1
    return index - 1


def _read_xlsx(data: bytes) -> list[list[str]]:
    """Read the first worksheet of a simple XLSX workbook (numbers and shared strings only) as a matrix of strings."""
    with zipfile.ZipFile(BytesIO(data)) as zf:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in zf.namelist():
            root = ElementTree.fromstring(zf.read("xl/sharedStrings.xml"))  # noqa: S314 - trusted who.int source
            shared = ["".join(t.text or "" for t in si.iter(f"{_XLSX_NS}t")) for si in root.iter(f"{_XLSX_NS}si")]
        sheet = ElementTree.fromstring(zf.read("xl/worksheets/sheet1.xml"))  # noqa: S314

    rows: list[list[str]] = []
    for row in sheet.iter(f"{_XLSX_NS}row"):
        values: list[str] = []
        for cell in row.iter(f"{_XLSX_NS}c"):
            col = _column_index(cell.get("r", ""))
            v = cell.find(f"{_XLSX_NS}v")
            text = v.text if v is not None and v.text is not None else ""
            if cell.get("t") == "s" and text:
                text = shared[int(text)]
            while len(values) <= col:
                values.append("")
            values[col] = text
        rows.append(values)
    return rows


def _lms_rows(matrix: list[list[str]], key_column: str, key_factor: float) -> list[tuple[float, float, float, float]]:
    header = [h.strip() for h in matrix[0]]
    idx = [header.index(name) for name in (key_column, "L", "M", "S")]
    rows = []
    for line in matrix[1:]:
        cells = [line[i] if i < len(line) else "" for i in idx]
        if any(c == "" for c in cells):
            continue
        key, l, m, s = (float(c) for c in cells)  # noqa: E741
        rows.append((key * key_factor, l, m, s))
    return rows


def download_who_tables(target_dir: Path) -> list[Path]:
    """
    Download the WHO growth standard/reference tables and convert them into canonical CSV tables.

    Fetches the 18 z-score workbooks (WHO Child Growth Standards 2006 for 0-5 years, WHO Growth Reference 2007
    for 5-19 years) from who.int and writes one ``<indicator>_<m|f>.csv`` per indicator and sex into
    ``target_dir``. The 0-5 and 5-19 tables of the same indicator are merged into one file. Pass ``target_dir``
    as ``data_dir`` to ``growth_zscore`` / ``growth_percentile`` with ``reference=GrowthReference.WHO``.

    The WHO tables are subject to WHO's terms of use (CC BY-NC-SA 3.0 IGO); they are not distributed with this
    package. By downloading them you accept those terms.

    Args:
        target_dir (Path): Directory to write the CSV tables into (created if missing)

    Returns:
        list[Path]: The written CSV files (12)

    Raises:
        WhoDownloadError: If any workbook could not be fetched (HTTP error such as 403/404, or a network error).
            All URLs are attempted first so the error lists every failure; nothing is written in that case.
    """
    target_dir = Path(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    collected: dict[tuple[GrowthIndicator, Gender], list[tuple[float, float, float, float]]] = {}
    failures: list[tuple[str, int | None, str]] = []
    for indicator, gender, url, key_column, key_factor in _WHO_SOURCES:
        try:
            with urlopen(Request(url, headers={"User-Agent": _USER_AGENT}), timeout=60) as response:  # noqa: S310
                data = response.read()
        except HTTPError as e:
            failures.append((url, e.code, e.reason))
            e.close()
            continue
        except URLError as e:
            failures.append((url, None, str(e.reason)))
            continue
        collected.setdefault((indicator, gender), []).extend(_lms_rows(_read_xlsx(data), key_column, key_factor))
    if failures:
        raise WhoDownloadError(failures)

    written = []
    for (indicator, gender), rows in collected.items():
        path = target_dir / f"{indicator.value}_{gender.value}.csv"
        write_canonical_table(path, rows)
        written.append(path)
    _load_table.cache_clear()
    return written
