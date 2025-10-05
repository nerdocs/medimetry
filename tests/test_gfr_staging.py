import pytest

from medimetry.renal import ckd_stage


def test_ckd_stage_g1_a1():
    """Test CKD staging with G1 stage and A1 category."""
    # GFR 95 (≥90) = G1, ACR 25 (<30) = A1
    gfr_category, alb_category, risk = ckd_stage(95, 25)
    assert gfr_category == "G1"
    assert alb_category == "A1"
    assert risk == 1


def test_ckd_stage_g2_a2():
    """Test CKD staging with G2 stage and A2 category."""
    # GFR 75 (60-89) = G2, ACR 150 (30-300) = A2
    gfr_category, alb_category, risk = ckd_stage(75, 150)
    assert gfr_category == "G2"
    assert alb_category == "A2"
    assert risk == 1


def test_ckd_stage_g3a_a3():
    """Test CKD staging with G3a stage and A3 category."""
    # GFR 50 (45-60) = G3a, ACR 400 (>300) = A3
    gfr_category, alb_category, risk = ckd_stage(50, 400)
    assert gfr_category == "G3a"
    assert alb_category == "A3"
    assert risk == 3


def test_ckd_stage_g3b_boundary():
    """Test CKD staging with G3b stage when GFR is exactly 30."""
    # GFR 30 (=30) = G3b, ACR 25 (<30) = A1
    gfr_category, alb_category, risk = ckd_stage(30, 25)
    assert gfr_category == "G3b"
    assert alb_category == "A1"
    assert risk == 2


def test_ckd_stage_g4_boundary():
    """Test CKD staging with G4 stage when GFR is exactly 15."""
    # GFR 15 (=15) = G4, ACR 25 (<30) = A1
    gfr_category, alb_category, risk = ckd_stage(15, 25)
    assert gfr_category == "G4"
    assert alb_category == "A1"
    assert risk == 3


def test_ckd_stage_g5():
    """Test CKD staging with G5 stage when GFR is below 15."""
    # GFR 10 (<15) = G5, ACR 25 (<30) = A1
    gfr_category, alb_category, risk = ckd_stage(10, 25)
    assert gfr_category == "G5"
    assert alb_category == "A1"
    assert risk == 4


def test_ckd_stage_acr_boundary_30():
    """Test CKD staging with ACR boundary value of exactly 30."""
    # GFR 75 (60-89) = G2, ACR 30 (=30) = A2
    gfr_category, alb_category, risk = ckd_stage(75, 30)
    assert gfr_category == "G2"
    assert alb_category == "A2"
    assert risk == 1


def test_ckd_stage_acr_boundary_300():
    """Test CKD staging with ACR boundary value of exactly 300."""
    # GFR 75 (60-89) = G2, ACR 300 (=300) = A2
    gfr_category, alb_category, risk = ckd_stage(75, 300)
    assert gfr_category == "G2"
    assert alb_category == "A2"
    assert risk == 1


def test_ckd_stage_gfr_boundary_90():
    """Test CKD staging with GFR boundary value of exactly 90."""
    # GFR 90 (=90) = G1, ACR 25 (<30) = A1
    gfr_category, alb_category, risk = ckd_stage(90, 25)
    assert gfr_category == "G1"
    assert alb_category == "A1"
    assert risk == 1


def test_ckd_stage_negative_gfr():
    """Test that ValueError is raised for negative GFR values."""
    with pytest.raises(ValueError, match="Invalid GFR value: -10"):
        ckd_stage(-10, 25)
