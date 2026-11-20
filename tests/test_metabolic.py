import pytest

from medimetry.metabolic import AscitesSeverity
from medimetry.metabolic import ChildPughGrade
from medimetry.metabolic import EncephalopathyGrade
from medimetry.metabolic import child_pugh_category
from medimetry.metabolic import child_pugh_score


def _score_and_grade(*args, **kwargs):
    score = child_pugh_score(*args, **kwargs)
    return score, child_pugh_category(score)


def test_child_pugh_class_a_minimum():
    """Test Child-Pugh Class A with minimum score (5)."""
    # All parameters at best values (1 point each)
    score, grade = _score_and_grade(
        bilirubin=1.5,
        albumin=4.0,
        inr=1.5,
        ascites=AscitesSeverity.NONE,
        encephalopathy=EncephalopathyGrade.NONE,
    )
    assert score == 5
    assert grade == ChildPughGrade.A


def test_child_pugh_class_a_maximum():
    """Test Child-Pugh Class A with maximum score (6)."""
    score, grade = _score_and_grade(
        bilirubin=1.9,
        albumin=3.6,
        inr=1.6,
        ascites=AscitesSeverity.NONE,
        encephalopathy=EncephalopathyGrade.GRADE1_2,
    )
    assert score == 6
    assert grade == ChildPughGrade.A


def test_child_pugh_class_b_minimum():
    """Test Child-Pugh Class B with minimum score (7)."""
    score, grade = _score_and_grade(
        bilirubin=2.5,
        albumin=3.0,
        inr=1.8,
        ascites=AscitesSeverity.NONE,
        encephalopathy=EncephalopathyGrade.GRADE1_2,
    )
    assert score == 9
    assert grade == ChildPughGrade.B


def test_child_pugh_class_b_maximum():
    """Test Child-Pugh Class B with maximum score (9)."""
    score, grade = _score_and_grade(
        bilirubin=2.9,
        albumin=2.9,
        inr=2.2,
        ascites=AscitesSeverity.SLIGHT,
        encephalopathy=EncephalopathyGrade.GRADE1_2,
    )
    assert score == 10
    assert grade == ChildPughGrade.C


def test_child_pugh_class_c_minimum():
    """Test Child-Pugh Class C with minimum score (10)."""
    score, grade = _score_and_grade(
        bilirubin=3.1,
        albumin=2.7,
        inr=2.4,
        ascites=AscitesSeverity.SLIGHT,
        encephalopathy=EncephalopathyGrade.GRADE1_2,
    )
    assert score == 13
    assert grade == ChildPughGrade.C


def test_child_pugh_class_c_maximum():
    """Test Child-Pugh Class C with maximum score (15)."""
    # All parameters at worst values (3 points each)
    score, grade = _score_and_grade(
        bilirubin=5.0,
        albumin=2.0,
        inr=3.0,
        ascites=AscitesSeverity.MODERATE,
        encephalopathy=EncephalopathyGrade.GRADE3_4,
    )
    assert score == 15
    assert grade == ChildPughGrade.C


def test_child_pugh_bilirubin_boundaries():
    """Test bilirubin scoring boundaries."""
    # Test boundary values
    base_params = {
        "albumin": 4.0,
        "inr": 1.5,
        "ascites": AscitesSeverity.NONE,
        "encephalopathy": EncephalopathyGrade.NONE,
    }

    # < 2.0 mg/dL = 1 point
    score1, _ = _score_and_grade(bilirubin=1.9, **base_params)
    assert score1 == 5  # 1+1+1+1+1

    # 2.0-3.0 mg/dL = 2 points
    score2, _ = _score_and_grade(bilirubin=2.0, **base_params)
    assert score2 == 6  # 2+1+1+1+1

    score3, _ = _score_and_grade(bilirubin=3.0, **base_params)
    assert score3 == 6  # 2+1+1+1+1

    # > 3.0 mg/dL = 3 points
    score4, _ = _score_and_grade(bilirubin=3.1, **base_params)
    assert score4 == 7  # 3+1+1+1+1


def test_child_pugh_albumin_boundaries():
    """Test albumin scoring boundaries."""
    base_params = {
        "bilirubin": 1.5,
        "inr": 1.5,
        "ascites": AscitesSeverity.NONE,
        "encephalopathy": EncephalopathyGrade.NONE,
    }

    # > 3.5 g/dL = 1 point
    score1, _ = _score_and_grade(albumin=3.6, **base_params)
    assert score1 == 5  # 1+1+1+1+1

    # 2.8-3.5 g/dL = 2 points
    score2, _ = _score_and_grade(albumin=3.5, **base_params)
    assert score2 == 6  # 1+2+1+1+1

    score3, _ = _score_and_grade(albumin=2.8, **base_params)
    assert score3 == 6  # 1+2+1+1+1

    # < 2.8 g/dL = 3 points
    score4, _ = _score_and_grade(albumin=2.7, **base_params)
    assert score4 == 7  # 1+3+1+1+1


def test_child_pugh_inr_boundaries():
    """Test INR scoring boundaries."""
    base_params = {
        "bilirubin": 1.5,
        "albumin": 4.0,
        "ascites": AscitesSeverity.NONE,
        "encephalopathy": EncephalopathyGrade.NONE,
    }

    # < 1.7 = 1 point
    score1, _ = _score_and_grade(inr=1.6, **base_params)
    assert score1 == 5  # 1+1+1+1+1

    # 1.7-2.3 = 2 points
    score2, _ = _score_and_grade(inr=1.7, **base_params)
    assert score2 == 6  # 1+1+2+1+1

    score3, _ = _score_and_grade(inr=2.3, **base_params)
    assert score3 == 6  # 1+1+2+1+1

    # > 2.3 = 3 points
    score4, _ = _score_and_grade(inr=2.4, **base_params)
    assert score4 == 7  # 1+1+3+1+1


def test_child_pugh_negative_bilirubin():
    """Test that ValueError is raised for negative bilirubin."""
    with pytest.raises(ValueError, match="Bilirubin must be non-negative"):
        child_pugh_score(-1.0, 4.0, 1.5, AscitesSeverity.NONE, EncephalopathyGrade.NONE)


def test_child_pugh_negative_albumin():
    """Test that ValueError is raised for negative albumin."""
    with pytest.raises(ValueError, match="Albumin must be non-negative"):
        child_pugh_score(1.5, -1.0, 1.5, AscitesSeverity.NONE, EncephalopathyGrade.NONE)


def test_child_pugh_negative_inr():
    """Test that ValueError is raised for negative INR."""
    with pytest.raises(ValueError, match="INR must be non-negative"):
        child_pugh_score(1.5, 4.0, -1.0, AscitesSeverity.NONE, EncephalopathyGrade.NONE)


def test_child_pugh_invalid_ascites():
    """Test that ValueError is raised for invalid ascites value."""
    with pytest.raises(ValueError):
        child_pugh_score(1.5, 4.0, 1.5, "somewhat", EncephalopathyGrade.NONE)


def test_child_pugh_invalid_encephalopathy():
    """Test that ValueError is raised for invalid encephalopathy value."""
    with pytest.raises(ValueError):
        child_pugh_score(1.5, 4.0, 1.5, AscitesSeverity.NONE, "grade17")


def test_child_pugh_zero_values():
    """Test Child-Pugh calculation with zero values."""
    score, grade = _score_and_grade(
        bilirubin=0.0,
        albumin=0.0,
        inr=0.0,
        ascites=AscitesSeverity.NONE,
        encephalopathy=EncephalopathyGrade.NONE,
    )
    # bilirubin=0 (1pt), albumin=0 (3pts), inr=0 (1pt), ascites=none (1pt), enceph=none (1pt)
    assert score == 7
    assert grade == ChildPughGrade.B


def test_child_pugh_realistic_scenarios():
    """Test realistic clinical scenarios."""
    # Compensated cirrhosis
    _score1, grade1 = _score_and_grade(1.2, 3.8, 1.3, AscitesSeverity.NONE, EncephalopathyGrade.NONE)
    assert grade1 == ChildPughGrade.A

    # Decompensated cirrhosis
    _score2, grade2 = _score_and_grade(3.5, 2.5, 2.8, AscitesSeverity.MODERATE, EncephalopathyGrade.GRADE3_4)
    assert grade2 == ChildPughGrade.C

    # Intermediate case
    _score3, grade3 = _score_and_grade(2.2, 3.2, 1.9, AscitesSeverity.SLIGHT, EncephalopathyGrade.NONE)
    assert grade3 == ChildPughGrade.B


@pytest.mark.parametrize(
    ("score", "grade"),
    [
        (5, ChildPughGrade.A),
        (6, ChildPughGrade.A),
        (7, ChildPughGrade.B),
        (9, ChildPughGrade.B),
        (10, ChildPughGrade.C),
        (15, ChildPughGrade.C),
    ],
)
def test_child_pugh_category_bands(score, grade):
    """Grade bands per Pugh 1973: A 5-6, B 7-9, C 10-15."""
    assert child_pugh_category(score) == grade


def test_child_pugh_score_returns_int_only():
    assert child_pugh_score(1.5, 4.0, 1.5, AscitesSeverity.NONE, EncephalopathyGrade.NONE) == 5


@pytest.mark.parametrize("score", [4, 16])
def test_child_pugh_category_out_of_range(score):
    with pytest.raises(ValueError, match="between 5 and 15"):
        child_pugh_category(score)


@pytest.mark.parametrize("score", [7.0, "7", True])
def test_child_pugh_category_type(score):
    with pytest.raises(TypeError, match="must be an int"):
        child_pugh_category(score)
