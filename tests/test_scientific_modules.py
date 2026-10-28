import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from nfi_v4.qc import bootstrap_mean_ci, flag_aberrant_hd
from nfi_v4.sensitivity import one_at_a_time_sensitivity
import pandas as pd


def test_aberrant_hd_flags():
    df = pd.DataFrame({"dbh": [10.0, 10.0, 10.0], "ht": [3.0, 0.1, 40.0]})
    out = flag_aberrant_hd(df, "dbh", "ht")
    assert bool(out.loc[0, "flag_aberrant_hd"]) is False or out.loc[0, "hd_ratio"] > 0
    assert bool(out.loc[2, "flag_aberrant_hd"]) is True


def test_bootstrap_ci_contains_mean():
    x = np.random.default_rng(0).normal(5, 1, 200)
    r = bootstrap_mean_ci(x, n_boot=200, random_state=0)
    assert r["ci_low"] <= r["mean"] <= r["ci_high"]


def test_sensitivity_changes_with_wood_density():
    dbh = np.array([8.0, 12.0, 15.0])
    ht = np.array([3.0, 4.0, 5.0])
    sens = one_at_a_time_sensitivity(dbh, ht)
    assert "wood_density" in set(sens["parameter"])
    assert sens["pct_change"].abs().max() > 0
