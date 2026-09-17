import pytest

from medimetry.pulmonary import GenevaRiskLevel
from medimetry.pulmonary import geneva_revised_score
from medimetry.pulmonary import geneva_simplified_score

ALL_ITEMS = {
    "previous_pe_dvt": True,
    "recent_surgery_or_fracture": True,
    "hemoptysis": True,
    "active_cancer": True,
    "unilateral_leg_pain": True,
    "leg_pain_on_palpation_and_edema": True,
}


def test_simplified_minimal_case():
    result = geneva_simplified_score(age=30, heart_rate=60)
    assert result.score == 0
    assert result.risk_level == GenevaRiskLevel.LOW


@pytest.mark.parametrize(("age", "expected"), [(65, 0), (66, 1)])
def test_simplified_age_threshold_is_over_65(age, expected):
    assert geneva_simplified_score(age=age, heart_rate=60).score == expected


@pytest.mark.parametrize(("hr", "expected"), [(74, 0), (75, 1), (94, 1), (95, 2), (140, 2)])
def test_simplified_heart_rate_points(hr, expected):
    assert geneva_simplified_score(age=30, heart_rate=hr).score == expected


def test_simplified_all_items_max_9():
    result = geneva_simplified_score(age=80, heart_rate=110, **ALL_ITEMS)
    assert result.score == 9
    assert result.risk_level == GenevaRiskLevel.HIGH


@pytest.mark.parametrize(
    ("kwargs", "score", "level"),
    [
        ({"previous_pe_dvt": True}, 1, GenevaRiskLevel.LOW),
        ({"previous_pe_dvt": True, "hemoptysis": True}, 2, GenevaRiskLevel.INTERMEDIATE),
        (
            {"previous_pe_dvt": True, "hemoptysis": True, "active_cancer": True, "unilateral_leg_pain": True},
            4,
            GenevaRiskLevel.INTERMEDIATE,
        ),
        (
            {
                "previous_pe_dvt": True,
                "hemoptysis": True,
                "active_cancer": True,
                "unilateral_leg_pain": True,
                "recent_surgery_or_fracture": True,
            },
            5,
            GenevaRiskLevel.HIGH,
        ),
    ],
)
def test_simplified_risk_levels(kwargs, score, level):
    result = geneva_simplified_score(age=30, heart_rate=60, **kwargs)
    assert result.score == score
    assert result.risk_level == level


def test_revised_minimal_case():
    result = geneva_revised_score(age=30, heart_rate=60)
    assert result.score == 0
    assert result.risk_level == GenevaRiskLevel.LOW


@pytest.mark.parametrize(("age", "expected"), [(65, 0), (66, 1)])
def test_revised_age_threshold_is_over_65(age, expected):
    assert geneva_revised_score(age=age, heart_rate=60).score == expected


@pytest.mark.parametrize(("hr", "expected"), [(74, 0), (75, 3), (94, 3), (95, 5)])
def test_revised_heart_rate_points(hr, expected):
    assert geneva_revised_score(age=30, heart_rate=hr).score == expected


@pytest.mark.parametrize(
    ("item", "points"),
    [
        ("previous_pe_dvt", 3),
        ("recent_surgery_or_fracture", 2),
        ("hemoptysis", 2),
        ("active_cancer", 2),
        ("unilateral_leg_pain", 3),
        ("leg_pain_on_palpation_and_edema", 4),
    ],
)
def test_revised_item_points(item, points):
    assert geneva_revised_score(age=30, heart_rate=60, **{item: True}).score == points


def test_revised_all_items_max_22():
    result = geneva_revised_score(age=80, heart_rate=110, **ALL_ITEMS)
    assert result.score == 22
    assert result.risk_level == GenevaRiskLevel.HIGH


@pytest.mark.parametrize(
    ("kwargs", "score", "level"),
    [
        ({"previous_pe_dvt": True}, 3, GenevaRiskLevel.LOW),
        ({"leg_pain_on_palpation_and_edema": True}, 4, GenevaRiskLevel.INTERMEDIATE),
        ({"leg_pain_on_palpation_and_edema": True, "previous_pe_dvt": True, "unilateral_leg_pain": True}, 10, GenevaRiskLevel.INTERMEDIATE),
        (
            {"leg_pain_on_palpation_and_edema": True, "previous_pe_dvt": True, "unilateral_leg_pain": True, "age": 70},
            11,
            GenevaRiskLevel.HIGH,
        ),
    ],
)
def test_revised_risk_levels(kwargs, score, level):
    kwargs = {"age": 30, "heart_rate": 60, **kwargs}
    result = geneva_revised_score(**kwargs)
    assert result.score == score
    assert result.risk_level == level


@pytest.mark.parametrize("func", [geneva_simplified_score, geneva_revised_score])
def test_invalid_inputs(func):
    with pytest.raises(ValueError, match="Age must be positive"):
        func(age=0, heart_rate=60)
    with pytest.raises(ValueError, match="Heart rate must be between 1 and 300"):
        func(age=30, heart_rate=0)
    with pytest.raises(ValueError, match="Heart rate must be between 1 and 300"):
        func(age=30, heart_rate=301)
