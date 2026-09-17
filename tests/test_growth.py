import io
import math
import urllib.error
import zipfile
from pathlib import Path

import pytest

from medimetry import Gender
from medimetry.growth import DAYS_PER_MONTH
from medimetry.growth import GrowthIndicator
from medimetry.growth import GrowthReference
from medimetry.growth import WhoDownloadError
from medimetry.growth import _read_xlsx
from medimetry.growth import download_who_tables
from medimetry.growth import growth_percentile
from medimetry.growth import growth_zscore
from medimetry.growth import write_canonical_table

FIXTURES = Path(__file__).parent / "fixtures" / "who"

# Literal rows from the CDC 2000 raw files (public domain): indicator, sex, raw key, L, M, S, P3, P97
CDC_ROWS = [
    (GrowthIndicator.WEIGHT_FOR_AGE, Gender.MALE, 24.5, -0.216501213, 12.74154396, 0.108166006, 10.4414422, 15.68840631),
    (GrowthIndicator.WEIGHT_FOR_AGE, Gender.FEMALE, 0.5, 1.357944315, 3.79752846, 0.138075916, 2.756916984, 4.743581789),
    (GrowthIndicator.LENGTH_HEIGHT_FOR_AGE, Gender.FEMALE, 120.5, 0.284748919, 138.2111552, 0.048704503, 125.9599043, 151.2919534),
    (GrowthIndicator.BMI_FOR_AGE, Gender.MALE, 180.5, -2.132344989, 19.85766121, 0.135110159, 16.20844134, 28.63575076),
    (GrowthIndicator.HEAD_CIRCUMFERENCE_FOR_AGE, Gender.MALE, 12.5, 0.171147024, 46.49853438, 0.027601686, 44.1359978, 48.96494367),
    (GrowthIndicator.WEIGHT_FOR_LENGTH, Gender.FEMALE, 80.5, -0.857844783, 10.6891553, 0.080099785, 9.277093118, 12.56034996),
    (GrowthIndicator.WEIGHT_FOR_HEIGHT, Gender.MALE, 77.5, -0.979897716, 10.38901871, 0.076995353, 9.073267731, 12.14509038),
]


def _key_kwargs(indicator, raw_key):
    if indicator in (GrowthIndicator.WEIGHT_FOR_LENGTH, GrowthIndicator.WEIGHT_FOR_HEIGHT):
        return {"length_cm": raw_key}
    return {"age_days": raw_key * DAYS_PER_MONTH}


@pytest.mark.parametrize(("indicator", "gender", "raw_key", "l", "m", "s", "p3", "p97"), CDC_ROWS)
def test_cdc_zscore_at_published_percentiles(indicator, gender, raw_key, l, m, s, p3, p97):  # noqa: E741
    """z at M is 0, at the published P3 / P97 values it is -1.881 / +1.881."""
    kwargs = _key_kwargs(indicator, raw_key)
    assert growth_zscore(indicator, gender, value=m, **kwargs) == pytest.approx(0, abs=0.01)
    assert growth_zscore(indicator, gender, value=p97, **kwargs) == pytest.approx(1.881, abs=0.01)
    assert growth_zscore(indicator, gender, value=p3, **kwargs) == pytest.approx(-1.881, abs=0.01)


@pytest.mark.parametrize(("indicator", "gender", "raw_key", "l", "m", "s", "p3", "p97"), CDC_ROWS)
def test_cdc_percentile_at_published_percentiles(indicator, gender, raw_key, l, m, s, p3, p97):  # noqa: E741
    kwargs = _key_kwargs(indicator, raw_key)
    assert growth_percentile(indicator, gender, value=m, **kwargs) == 50.0
    assert growth_percentile(indicator, gender, value=p97, **kwargs) == pytest.approx(97.0, abs=0.1)
    assert growth_percentile(indicator, gender, value=p3, **kwargs) == pytest.approx(3.0, abs=0.1)


def test_interpolation_between_rows():
    """Halfway between two rows the interpolated M gives z = 0 (CDC wfa boys, Agemos 24.5 and 25.5)."""
    m_mid = (12.74154396 + 12.88102276) / 2
    z = growth_zscore(GrowthIndicator.WEIGHT_FOR_AGE, Gender.MALE, value=m_mid, age_days=25.0 * DAYS_PER_MONTH)
    assert z == pytest.approx(0, abs=1e-9)


def test_zscore_is_not_rounded():
    z = growth_zscore(GrowthIndicator.WEIGHT_FOR_AGE, Gender.MALE, value=13.0, age_days=24.5 * DAYS_PER_MONTH)
    assert z != round(z, 2)


def test_key_outside_table_range():
    with pytest.raises(ValueError, match="outside reference table range"):
        growth_zscore(GrowthIndicator.WEIGHT_FOR_AGE, Gender.MALE, value=10, age_days=21 * 365.25)
    with pytest.raises(ValueError, match="outside reference table range"):
        growth_zscore(GrowthIndicator.WEIGHT_FOR_LENGTH, Gender.MALE, value=10, length_cm=44)


def test_invalid_value():
    with pytest.raises(ValueError, match="must be positive"):
        growth_zscore(GrowthIndicator.WEIGHT_FOR_AGE, Gender.MALE, value=0, age_days=100)


def test_key_argument_validation():
    with pytest.raises(ValueError, match="Exactly one of"):
        growth_zscore(GrowthIndicator.WEIGHT_FOR_AGE, Gender.MALE, value=10)
    with pytest.raises(ValueError, match="Exactly one of"):
        growth_zscore(GrowthIndicator.WEIGHT_FOR_AGE, Gender.MALE, value=10, age_days=100, length_cm=50)
    with pytest.raises(ValueError, match="keyed by age_days"):
        growth_zscore(GrowthIndicator.WEIGHT_FOR_AGE, Gender.MALE, value=10, length_cm=50)
    with pytest.raises(ValueError, match="keyed by length_cm"):
        growth_zscore(GrowthIndicator.WEIGHT_FOR_LENGTH, Gender.MALE, value=10, age_days=100)


def test_type_validation():
    with pytest.raises(AssertionError, match="Gender"):
        growth_zscore(GrowthIndicator.WEIGHT_FOR_AGE, Gender.DIVERSE, value=10, age_days=100)
    with pytest.raises(AssertionError, match="GrowthIndicator"):
        growth_zscore("wfa", Gender.MALE, value=10, age_days=100)
    with pytest.raises(AssertionError, match="GrowthReference"):
        growth_zscore(GrowthIndicator.WEIGHT_FOR_AGE, Gender.MALE, value=10, age_days=100, reference="who")


def test_who_requires_data_dir(tmp_path):
    with pytest.raises(ValueError, match="data_dir is required"):
        growth_zscore(GrowthIndicator.WEIGHT_FOR_AGE, Gender.MALE, value=10, age_days=100, reference=GrowthReference.WHO)
    with pytest.raises(FileNotFoundError, match="download_who_tables"):
        growth_zscore(GrowthIndicator.WEIGHT_FOR_AGE, Gender.MALE, value=10, age_days=100, reference=GrowthReference.WHO, data_dir=tmp_path)


def test_who_fixture_l_zero_and_l_nonzero_branches():
    """Synthetic fixture table (not WHO data): exercises the loader path and the L = 0 branch."""
    kwargs = {"reference": GrowthReference.WHO, "data_dir": FIXTURES}
    z = growth_zscore(GrowthIndicator.WEIGHT_FOR_AGE, Gender.MALE, value=3.0 * math.exp(0.1), age_days=0, **kwargs)
    assert z == pytest.approx(1.0)
    z = growth_zscore(GrowthIndicator.WEIGHT_FOR_AGE, Gender.MALE, value=8.0 * 1.1, age_days=200, **kwargs)
    assert z == pytest.approx(1.0)


def _xlsx(shared_strings, rows):
    """Build a minimal XLSX (sharedStrings + sheet1) in memory."""
    ns = 'xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"'
    sst = f"<sst {ns}>" + "".join(f"<si><t>{s}</t></si>" for s in shared_strings) + "</sst>"
    sheet_rows = []
    for r, cells in enumerate(rows, start=1):
        xml_cells = []
        for c, (kind, value) in enumerate(cells):
            ref = f"{chr(ord('A') + c)}{r}"
            xml_cells.append(f'<c r="{ref}" t="s"><v>{value}</v></c>' if kind == "s" else f'<c r="{ref}"><v>{value}</v></c>')
        sheet_rows.append(f'<row r="{r}">' + "".join(xml_cells) + "</row>")
    sheet = f"<worksheet {ns}><sheetData>" + "".join(sheet_rows) + "</sheetData></worksheet>"
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("xl/sharedStrings.xml", sst)
        zf.writestr("xl/worksheets/sheet1.xml", sheet)
    return buf.getvalue()


def test_read_xlsx():
    data = _xlsx(["Day", "L", "M", "S"], [[("s", 0), ("s", 1), ("s", 2), ("s", 3)], [("n", 0), ("n", 1), ("n", 49.8842), ("n", 0.03795)]])
    assert _read_xlsx(data) == [["Day", "L", "M", "S"], ["0", "1", "49.8842", "0.03795"]]


def test_write_canonical_table(tmp_path):
    path = tmp_path / "t.csv"
    write_canonical_table(path, [(2.0, 1, 2, 3), (1.0, 4, 5, 6)])
    assert path.read_text().splitlines() == ["key;L;M;S", "1.0;4.0;5.0;6.0", "2.0;1.0;2.0;3.0"]
    with pytest.raises(AssertionError, match="Duplicate key"):
        write_canonical_table(path, [(1.0, 1, 2, 3), (1.0, 4, 5, 6)])


def test_download_who_tables_reports_all_failures(tmp_path, monkeypatch):
    """Every failed URL is collected with its HTTP status; nothing is written."""
    calls = []

    def fake_urlopen(request, timeout):
        calls.append(request.full_url)
        if len(calls) == 1:
            raise urllib.error.HTTPError(request.full_url, 403, "Forbidden", {}, None)
        if len(calls) == 2:
            raise urllib.error.URLError("timed out")
        raise urllib.error.HTTPError(request.full_url, 404, "Not Found", {}, None)

    monkeypatch.setattr("medimetry.growth.urlopen", fake_urlopen)
    with pytest.raises(WhoDownloadError) as excinfo:
        download_who_tables(tmp_path)

    failures = excinfo.value.failures
    assert len(failures) == len(calls) == 18
    assert failures[0][1:] == (403, "Forbidden")
    assert failures[1][1] is None
    assert "timed out" in failures[1][2]
    assert failures[2][1] == 404
    assert "18 WHO download(s) failed" in str(excinfo.value)
    assert "403 Forbidden" in str(excinfo.value)
    assert list(tmp_path.iterdir()) == []
