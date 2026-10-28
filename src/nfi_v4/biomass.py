"""Tree and shrub biomass formulas from the KSA NFI calculation document.

Source: NFI_ KSA Calculation_Trees&shrubs.docx (extracted in docs/_calc_doc_extract.md).
All constants must match config.yaml / that document. No invented coefficients.
"""

from __future__ import annotations

import math
from typing import Iterable

import numpy as np
import pandas as pd

# Document defaults (also in config.yaml)
FORM_FACTOR = 0.65
WOOD_DENSITY = 0.6
BEF = 2.0
ROOT_SHOOT = 0.28
CARBON_FRACTION = 0.47
CO2EQ_FACTOR = 3.67
CONVERSION_FACTOR_HA = 10  # 1000 m2 plot = 0.1 ha


def basal_area_m2(dbh_cm: float | np.ndarray) -> float | np.ndarray:
    """Basal Area (m2) = (pi * DBH_cm^2) / 40000."""
    return (math.pi * np.asarray(dbh_cm, dtype=float) ** 2) / 40000.0


def tree_volume_m3(dbh_cm, height_m, form_factor: float = FORM_FACTOR):
    """Tree volume (m3) = BA * height_m * form_factor."""
    return basal_area_m2(dbh_cm) * np.asarray(height_m, dtype=float) * form_factor


def tree_agb_mg(volume_m3, wood_density: float = WOOD_DENSITY, bef: float = BEF):
    """AGB (Mg) = volume * wood_density * BEF."""
    return np.asarray(volume_m3, dtype=float) * wood_density * bef


def tree_bgb_mg(agb_mg, root_shoot: float = ROOT_SHOOT):
    """BGB (Mg) = AGB * root:shoot."""
    return np.asarray(agb_mg, dtype=float) * root_shoot


def total_biomass_mg(agb_mg, bgb_mg):
    """Total biomass = AGB + BGB (implied in calculation chain)."""
    return np.asarray(agb_mg, dtype=float) + np.asarray(bgb_mg, dtype=float)


def carbon_mg(total_biomass, carbon_fraction: float = CARBON_FRACTION):
    """Carbon (Mg) = total biomass * 0.47."""
    return np.asarray(total_biomass, dtype=float) * carbon_fraction


def co2eq_mg(carbon, factor: float = CO2EQ_FACTOR):
    """CO2 equivalent (Mg) = Carbon * 3.67."""
    return np.asarray(carbon, dtype=float) * factor


def tree_metrics_from_dbh_height(
    dbh_cm,
    height_m,
    form_factor: float = FORM_FACTOR,
    wood_density: float = WOOD_DENSITY,
    bef: float = BEF,
    root_shoot: float = ROOT_SHOOT,
    carbon_fraction: float = CARBON_FRACTION,
    co2eq_factor: float = CO2EQ_FACTOR,
) -> dict:
    ba = basal_area_m2(dbh_cm)
    vol = ba * np.asarray(height_m, dtype=float) * form_factor
    agb = tree_agb_mg(vol, wood_density, bef)
    bgb = tree_bgb_mg(agb, root_shoot)
    tot = total_biomass_mg(agb, bgb)
    carb = carbon_mg(tot, carbon_fraction)
    co2 = co2eq_mg(carb, co2eq_factor)
    return {
        "basal_area_m2": ba,
        "volume_m3": vol,
        "agb_mg": agb,
        "bgb_mg": bgb,
        "total_biomass_mg": tot,
        "carbon_mg_provisional": carb,
        "co2eq_mg_provisional": co2,
    }


def shrub_agb_mg(
    crown_diameter_m,
    height_cm,
    a: float = -0.37,
    b_cd: float = 1.903,
    b_h: float = 0.652,
    intercept_add: float = 1.403,
    scale: float = 1000.0,
    log_base: str = "natural",
):
    """Shrub AGB equation from calculation document.

    AGB = (exp(a + b_cd*log(CD) + b_h*log(H)) + intercept_add) / scale
    CD in m, H in cm. Document does not state log base; default natural log.
    """
    cd = np.asarray(crown_diameter_m, dtype=float)
    h = np.asarray(height_cm, dtype=float)
    if log_base == "natural":
        log = np.log
    elif log_base == "10":
        log = np.log10
    else:
        raise ValueError(f"Unsupported log_base: {log_base}")
    with np.errstate(divide="ignore", invalid="ignore"):
        inner = a + b_cd * log(cd) + b_h * log(h)
        agb = (np.exp(inner) + intercept_add) / scale
    return agb


def per_ha_from_plot_average(plot_average, conversion_factor: float = CONVERSION_FACTOR_HA):
    """Value per hectare = average of 5 plots * conversion factor (CF=10)."""
    return np.asarray(plot_average, dtype=float) * conversion_factor


def land_use_proportion(n_plots_in_class: int, plots_per_su: int = 5) -> float:
    return float(n_plots_in_class) / float(plots_per_su)


def apply_tree_metrics(df: pd.DataFrame, dbh_col: str, height_col: str, **kwargs) -> pd.DataFrame:
    out = df.copy()
    m = tree_metrics_from_dbh_height(out[dbh_col].to_numpy(), out[height_col].to_numpy(), **kwargs)
    for k, v in m.items():
        out[k] = v
    return out


def exclude_by_substrings(series: pd.Series, substrings: Iterable[str]) -> pd.Series:
    s = series.astype(str).str.lower().fillna("")
    mask = pd.Series(False, index=series.index)
    for sub in substrings:
        mask |= s.str.contains(str(sub).lower(), na=False)
    return ~mask
