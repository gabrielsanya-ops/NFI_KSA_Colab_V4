"""Spatial / grouped CV utilities and optimism-gap reporting."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupKFold, KFold


def regression_scores(y_true, y_pred):
    return {
        "r2": float(r2_score(y_true, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "bias": float(np.mean(np.asarray(y_pred) - np.asarray(y_true))),
    }


def compare_random_vs_group_cv(estimator, X, y, groups, n_splits: int = 5, random_state: int = 42):
    """Fit the same estimator under random KFold vs GroupKFold(groups).

    A large RMSE gap (random much better) indicates spatial/group leakage optimism.
    """
    rows = []
    # Random CV
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    for fold, (tr, te) in enumerate(kf.split(X), 1):
        est = clone(estimator)
        est.fit(X.iloc[tr] if hasattr(X, "iloc") else X[tr], y[tr])
        pred = est.predict(X.iloc[te] if hasattr(X, "iloc") else X[te])
        s = regression_scores(y[te], pred)
        s.update({"scheme": "random_kfold", "fold": fold})
        rows.append(s)
    # Group CV
    gkf = GroupKFold(n_splits=n_splits)
    for fold, (tr, te) in enumerate(gkf.split(X, y, groups), 1):
        est = clone(estimator)
        est.fit(X.iloc[tr] if hasattr(X, "iloc") else X[tr], y[tr])
        pred = est.predict(X.iloc[te] if hasattr(X, "iloc") else X[te])
        s = regression_scores(y[te], pred)
        s.update({"scheme": "group_kfold_su", "fold": fold})
        rows.append(s)
    df = pd.DataFrame(rows)
    summary = (
        df.groupby("scheme")[["r2", "rmse", "mae", "bias"]]
        .agg(["mean", "std"])
        .reset_index()
    )
    # flatten columns
    summary.columns = ["_".join([c for c in col if c]).strip("_") for col in summary.columns.values]
    rand_rmse = df.loc[df.scheme == "random_kfold", "rmse"].mean()
    grp_rmse = df.loc[df.scheme == "group_kfold_su", "rmse"].mean()
    gap = {
        "random_rmse_mean": float(rand_rmse),
        "group_su_rmse_mean": float(grp_rmse),
        "optimism_gap_rmse": float(grp_rmse - rand_rmse),
        "interpretation": (
            "Positive gap means random CV was optimistic relative to SU-blocked CV "
            "(expected under spatial/cluster dependence)."
        ),
    }
    return df, summary, gap
