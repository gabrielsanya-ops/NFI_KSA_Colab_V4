"""Unit tests verifying formulas against the calculation document constants."""

import math
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from nfi_v4.biomass import (
    BEF,
    CARBON_FRACTION,
    CO2EQ_FACTOR,
    FORM_FACTOR,
    ROOT_SHOOT,
    WOOD_DENSITY,
    basal_area_m2,
    carbon_mg,
    co2eq_mg,
    shrub_agb_mg,
    total_biomass_mg,
    tree_agb_mg,
    tree_bgb_mg,
    tree_metrics_from_dbh_height,
    tree_volume_m3,
)


def test_basal_area_known_value():
    # DBH 20 cm: BA = pi*400/40000 = pi/100
    ba = basal_area_m2(20.0)
    assert abs(ba - (math.pi * 400.0 / 40000.0)) < 1e-12


def test_volume_uses_form_factor_065():
    vol = tree_volume_m3(20.0, 10.0)
    expected = basal_area_m2(20.0) * 10.0 * FORM_FACTOR
    assert abs(vol - expected) < 1e-12
    assert FORM_FACTOR == 0.65


def test_agb_wood_density_and_bef():
    vol = 1.0
    agb = tree_agb_mg(vol)
    assert abs(agb - (1.0 * WOOD_DENSITY * BEF)) < 1e-12
    assert WOOD_DENSITY == 0.6
    assert BEF == 2.0


def test_bgb_root_shoot():
    assert abs(tree_bgb_mg(10.0) - 10.0 * ROOT_SHOOT) < 1e-12
    assert ROOT_SHOOT == 0.28


def test_carbon_and_co2eq_chain():
    agb = 10.0
    bgb = tree_bgb_mg(agb)
    tot = total_biomass_mg(agb, bgb)
    carb = carbon_mg(tot)
    co2 = co2eq_mg(carb)
    assert abs(carb - tot * CARBON_FRACTION) < 1e-12
    assert abs(co2 - carb * CO2EQ_FACTOR) < 1e-12
    assert CARBON_FRACTION == 0.47
    assert CO2EQ_FACTOR == 3.67


def test_full_tree_metrics_monotonic_in_dbh():
    m_small = tree_metrics_from_dbh_height(5.0, 3.0)
    m_large = tree_metrics_from_dbh_height(25.0, 3.0)
    assert m_large["carbon_mg_provisional"] > m_small["carbon_mg_provisional"]


def test_shrub_equation_positive():
    # CD=1 m, H=100 cm
    agb = shrub_agb_mg(1.0, 100.0)
    assert np.isfinite(agb)
    assert agb > 0
