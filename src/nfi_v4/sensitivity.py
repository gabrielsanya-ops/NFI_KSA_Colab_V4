"""Allometric / IPCC-factor sensitivity for provisional biomass."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .biomass import (
    BEF,
    CARBON_FRACTION,
    FORM_FACTOR,
    ROOT_SHOOT,
    WOOD_DENSITY,
    basal_area_m2,
)


def tree_carbon_with_factors(dbh_cm, height_m, form_factor, wood_density, bef, root_shoot, carbon_fraction):
    ba = basal_area_m2(dbh_cm)
    vol = ba * np.asarray(height_m, dtype=float) * form_factor
    agb = vol * wood_density * bef
    bgb = agb * root_shoot
    return (agb + bgb) * carbon_fraction


def one_at_a_time_sensitivity(
    dbh_cm,
    height_m,
    deltas=None,
):
    """Perturb each constant by relative deltas and report mean carbon change (%)."""
    if deltas is None:
        deltas = {"form_factor": 0.10, "wood_density": 0.10, "bef": 0.10, "carbon_fraction": 0.05}
    base = tree_carbon_with_factors(
        dbh_cm, height_m, FORM_FACTOR, WOOD_DENSITY, BEF, ROOT_SHOOT, CARBON_FRACTION
    )
    base_mean = float(np.nanmean(base))
    rows = []
    specs = {
        "form_factor": FORM_FACTOR,
        "wood_density": WOOD_DENSITY,
        "bef": BEF,
        "carbon_fraction": CARBON_FRACTION,
    }
    for name, base_val in specs.items():
        d = deltas[name]
        for sign, label in [(1, "plus"), (-1, "minus")]:
            kwargs = {
                "form_factor": FORM_FACTOR,
                "wood_density": WOOD_DENSITY,
                "bef": BEF,
                "root_shoot": ROOT_SHOOT,
                "carbon_fraction": CARBON_FRACTION,
            }
            kwargs[name] = base_val * (1 + sign * d)
            alt = tree_carbon_with_factors(dbh_cm, height_m, **kwargs)
            alt_mean = float(np.nanmean(alt))
            rows.append(
                {
                    "parameter": name,
                    "perturbation": f"{label}_{int(100*d)}pct",
                    "base_mean_carbon": base_mean,
                    "alt_mean_carbon": alt_mean,
                    "pct_change": 100.0 * (alt_mean - base_mean) / base_mean if base_mean else np.nan,
                }
            )
    return pd.DataFrame(rows)
