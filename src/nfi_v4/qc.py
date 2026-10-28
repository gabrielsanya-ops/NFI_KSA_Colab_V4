"""Field QA/QC helpers aligned with common NFI practice (range and cross-field checks)."""

from __future__ import annotations

import numpy as np
import pandas as pd


def dbh_height_ratio(dbh_cm, height_m):
    """Height (m) per DBH (cm). Very small or large ratios are aberrant."""
    dbh = np.asarray(dbh_cm, dtype=float)
    ht = np.asarray(height_m, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        return ht / dbh


def flag_aberrant_hd(
    df: pd.DataFrame,
    dbh_col: str,
    height_col: str,
    min_ratio: float = 0.05,
    max_ratio: float = 2.5,
    min_dbh: float = 0.1,
    max_dbh: float = 200.0,
    min_height: float = 0.1,
    max_height: float = 60.0,
) -> pd.DataFrame:
    """Flag range and cross-field inconsistencies. Does not delete rows."""
    out = df.copy()
    dbh = pd.to_numeric(out[dbh_col], errors="coerce")
    ht = pd.to_numeric(out[height_col], errors="coerce")
    ratio = dbh_height_ratio(dbh, ht)
    out["hd_ratio"] = ratio
    out["flag_range_dbh"] = (dbh < min_dbh) | (dbh > max_dbh)
    out["flag_range_height"] = (ht < min_height) | (ht > max_height)
    out["flag_aberrant_hd"] = (ratio < min_ratio) | (ratio > max_ratio)
    out["flag_qc_any"] = out["flag_range_dbh"] | out["flag_range_height"] | out["flag_aberrant_hd"]
    return out


def bootstrap_mean_ci(x, n_boot: int = 1000, alpha: float = 0.05, random_state: int = 42):
    """Percentile bootstrap CI for the mean (sample inference, not design-based)."""
    rng = np.random.default_rng(random_state)
    x = np.asarray(pd.Series(x).dropna(), dtype=float)
    if len(x) == 0:
        return {"n": 0, "mean": np.nan, "ci_low": np.nan, "ci_high": np.nan}
    means = []
    for _ in range(n_boot):
        sample = rng.choice(x, size=len(x), replace=True)
        means.append(sample.mean())
    lo, hi = np.quantile(means, [alpha / 2, 1 - alpha / 2])
    return {
        "n": int(len(x)),
        "mean": float(x.mean()),
        "ci_low": float(lo),
        "ci_high": float(hi),
        "note": "BOOTSTRAP_SAMPLE_CI_NOT_DESIGN_BASED",
    }
