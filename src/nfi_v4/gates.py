"""Anti-clip Gate 1 / Gate 2 helpers for Asir NFI."""

from __future__ import annotations

import pandas as pd


def anti_clip_su_tree_counts(su_ids, trees: pd.DataFrame, su_col: str) -> pd.DataFrame:
    """LEFT join tree counts onto full SU universe (zeros retained)."""
    frame = pd.DataFrame({su_col: [str(x).strip() for x in su_ids]}).drop_duplicates()
    t = trees.copy()
    t[su_col] = t[su_col].astype(str).str.strip()
    counts = (
        t.groupby(su_col, dropna=False)
        .size()
        .rename("n_tree_records")
        .reset_index()
    )
    counts[su_col] = counts[su_col].astype(str).str.strip()
    out = frame.merge(counts, on=su_col, how="left")
    out["n_tree_records"] = out["n_tree_records"].fillna(0).astype(int)
    out["has_trees"] = out["n_tree_records"] > 0
    return out


def gate1_summary(su_tree: pd.DataFrame, expected: dict) -> dict:
    total = int(len(su_tree))
    with_trees = int(su_tree["has_trees"].sum())
    no_trees = total - with_trees
    return {
        "observed_total_sus": total,
        "observed_sus_with_trees": with_trees,
        "observed_sus_no_trees": no_trees,
        "expected_total_sus": expected.get("total_sus"),
        "expected_sus_with_trees": expected.get("sus_with_trees"),
        "expected_sus_no_trees": expected.get("sus_no_trees"),
        "match_total": total == expected.get("total_sus"),
        "match_with_trees": with_trees == expected.get("sus_with_trees"),
        "match_no_trees": no_trees == expected.get("sus_no_trees"),
    }


def build_su_plot_lattice(su_ids, plots_per_su: int = 5, su_col: str = "su_no") -> pd.DataFrame:
    rows = []
    for su in su_ids:
        su_s = str(su).strip()
        for p in range(1, plots_per_su + 1):
            rows.append({su_col: su_s, "plot_no": p, "plot_uid": f"{su_s}-{p}"})
    return pd.DataFrame(rows)


def gate2_summary(
    lattice: pd.DataFrame,
    trees: pd.DataFrame,
    su_col: str,
    plot_uid_col: str = "plot_uid",
    expected: dict | None = None,
) -> dict:
    expected = expected or {}
    t = trees.copy()
    t[plot_uid_col] = t[plot_uid_col].astype(str).str.strip()
    lat = lattice.copy()
    lat[plot_uid_col] = lat[plot_uid_col].astype(str).str.strip()
    lat[su_col] = lat[su_col].astype(str).str.strip()
    tree_plots = (
        t.assign(_one=1)
        .groupby(plot_uid_col, dropna=False)["_one"]
        .sum()
        .rename("n_trees")
        .reset_index()
    )
    tree_plots[plot_uid_col] = tree_plots[plot_uid_col].astype(str).str.strip()
    lat = lat.merge(tree_plots, on=plot_uid_col, how="left")
    lat["n_trees"] = lat["n_trees"].fillna(0).astype(int)
    lat["has_trees"] = lat["n_trees"] > 0

    su_has = lat.groupby(su_col)["has_trees"].any()
    zero_tree_sus = set(su_has[~su_has].index)
    lat["in_zero_tree_su"] = lat[su_col].isin(zero_tree_sus)
    # Gate 2 candidates: plots without trees that are NOT inside Gate-1 zero-tree SUs
    lat["gate2_candidate"] = (~lat["has_trees"]) & (~lat["in_zero_tree_su"])

    obs = {
        "observed_lattice_rows": int(len(lat)),
        "observed_plots_with_trees": int(lat["has_trees"].sum()),
        "observed_plots_in_zero_tree_sus": int(lat["in_zero_tree_su"].sum()),
        "observed_gate2_plots": int(lat["gate2_candidate"].sum()),
        "expected_plots": expected.get("expected_plots"),
        "expected_plots_with_trees": expected.get("plots_with_trees"),
        "expected_gate2_plots": expected.get("gate2_plots"),
    }
    return {"summary": obs, "lattice": lat}
