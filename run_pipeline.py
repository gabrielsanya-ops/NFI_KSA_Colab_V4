"""NFI GeoAI Pipeline V4 runner. All outputs under outputs_v4/. Does not overwrite raw data."""

from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupKFold

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from nfi_v4.biomass import (  # noqa: E402
    apply_tree_metrics,
    exclude_by_substrings,
    shrub_agb_mg,
    tree_bgb_mg,
    carbon_mg,
    total_biomass_mg,
)
from nfi_v4.gates import (  # noqa: E402
    anti_clip_su_tree_counts,
    build_su_plot_lattice,
    gate1_summary,
    gate2_summary,
)

warnings.filterwarnings("ignore", category=UserWarning)


def resolve_path(p) -> Path:
    """Resolve config paths relative to project ROOT (Colab-safe)."""
    path = Path(p)
    if path.is_absolute():
        return path
    return (ROOT / path).resolve()


def load_config():
    with open(ROOT / "config.yaml", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    # Normalize all relative paths against ROOT
    for key in list(cfg.get("paths", {})):
        cfg["paths"][key] = str(resolve_path(cfg["paths"][key]))
    for key in list(cfg.get("tables", {})):
        cfg["tables"][key] = str(resolve_path(cfg["tables"][key]))
    return cfg


def ensure_dirs(cfg):
    out = Path(cfg["paths"]["output_root"])
    for sub in ["tables", "figures", "maps", "reports", "logs"]:
        (out / sub).mkdir(parents=True, exist_ok=True)
    return out


def find_col(df, candidates):
    cols = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand.lower() in cols:
            return cols[cand.lower()]
    # partial
    for c in df.columns:
        cl = c.lower()
        for cand in candidates:
            if cand.lower() in cl:
                return c
    return None


def load_tables(cfg):
    tables = {}
    for key, path in cfg["tables"].items():
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(p)
        tables[key] = pd.read_excel(p)
    return tables


def national_scope(su: pd.DataFrame, plot: pd.DataFrame, trees: pd.DataFrame, cfg) -> dict:
    """Entire-country frame: all master SUs (anti-clip). Asir is optional validation only."""
    region_col = find_col(su, [cfg["columns"]["region_en"], "su_group_region_e", "region"])
    su_id = find_col(su, [cfg["columns"]["su_id_in_su_master"], "su_no"])
    su_f = su.copy()
    child_su = find_col(plot, [cfg["columns"]["su_id_in_child"], "nfi_of_ksa_program_su_su_no", "su_no"])
    tree_su = find_col(trees, [cfg["columns"]["su_id_in_child"], "nfi_of_ksa_program_su_su_no", "su_no"])
    ids = set(su_f[su_id].astype(str).str.strip())
    plot_f = plot[plot[child_su].astype(str).str.strip().isin(ids)].copy() if child_su else plot.copy()
    trees_f = trees[trees[tree_su].astype(str).str.strip().isin(ids)].copy() if tree_su else trees.copy()
    n_regions = int(su_f[region_col].nunique()) if region_col else None
    return {
        "su": su_f,
        "plot": plot_f,
        "trees": trees_f,
        "su_id_col": su_id,
        "plot_su_col": child_su,
        "tree_su_col": tree_su,
        "region_col": region_col,
        "n_su": len(ids),
        "n_regions": n_regions,
        "scope": "national_KSA",
    }


def asir_filter(su: pd.DataFrame, plot: pd.DataFrame, trees: pd.DataFrame, cfg) -> dict:
    """Legacy Asir-only filter retained for optional validation callers."""
    region_col = find_col(su, [cfg["columns"]["region_en"], "su_group_region_e", "region"])
    su_id = find_col(su, [cfg["columns"]["su_id_in_su_master"], "su_no"])
    asir_su_ids = None
    shp = Path(cfg["paths"]["asir_su"])
    if shp.exists():
        try:
            import shapefile

            r = shapefile.Reader(str(shp))
            fields = [f[0] for f in r.fields[1:]]
            su_field = None
            for name in fields:
                if name.upper() in ("SU", "SU_NO", "SU_ID"):
                    su_field = name
                    break
            if su_field is None:
                su_field = fields[0]
            idx = fields.index(su_field)
            asir_su_ids = [rec[idx] for rec in r.records()]
        except Exception as e:
            print("shapefile read note:", e)

    if asir_su_ids is not None:
        asir_su_ids = [str(x).strip() for x in asir_su_ids]
        su_f = su[su[su_id].astype(str).str.strip().isin(asir_su_ids)].copy()
    elif region_col is not None:
        mask = su[region_col].astype(str).str.contains("Aseer|Asir", case=False, na=False)
        su_f = su.loc[mask].copy()
    else:
        su_f = su.copy()

    child_su = find_col(plot, [cfg["columns"]["su_id_in_child"], "nfi_of_ksa_program_su_su_no", "su_no"])
    tree_su = find_col(trees, [cfg["columns"]["su_id_in_child"], "nfi_of_ksa_program_su_su_no", "su_no"])
    ids = set(su_f[su_id].astype(str).str.strip())
    plot_f = plot[plot[child_su].astype(str).str.strip().isin(ids)].copy() if child_su else plot.copy()
    trees_f = trees[trees[tree_su].astype(str).str.strip().isin(ids)].copy() if tree_su else trees.copy()
    return {
        "su": su_f,
        "plot": plot_f,
        "trees": trees_f,
        "su_id_col": su_id,
        "plot_su_col": child_su,
        "tree_su_col": tree_su,
        "n_asir_su": len(ids),
    }


def make_plot_uid(df, su_col, plot_col):
    return df[su_col].astype(str).str.strip() + "-" + df[plot_col].astype(str).str.strip()


def run():
    cfg = load_config()
    out = ensure_dirs(cfg)
    seed = int(cfg["project"]["random_seed"])
    np.random.seed(seed)
    log = []

    print("Loading tables...")
    tables = load_tables(cfg)
    log.append(f"Loaded tables: { {k: len(v) for k, v in tables.items()} }")

    scoped = national_scope(tables["su"], tables["plot"], tables["trees"], cfg)
    su, plot, trees = scoped["su"], scoped["plot"], scoped["trees"]
    su_col = scoped["su_id_col"]
    tree_su = scoped["tree_su_col"]
    plot_su = scoped["plot_su_col"]
    log.append(
        f"NATIONAL SU frame: {scoped['n_su']} SUs across {scoped.get('n_regions')} regions"
    )

    # Column resolution
    dbh_col = find_col(trees, [cfg["columns"]["dbh"], "tree_dbh", "dbh"])
    ht_col = find_col(trees, [cfg["columns"]["height"], "tree_height", "height"])
    species_col = find_col(trees, ["tree_species", "species", "scientific", "sp_name", "tree_sp"])
    plot_id_col = find_col(plot, [cfg["columns"]["plot_id"], "plot_id1", "plot_id"])
    lat_col = find_col(plot, [cfg["columns"]["lat"], "plot_info1_plot_coor1_y", "lat", "y"])
    lon_col = find_col(plot, [cfg["columns"]["lon"], "plot_info1_plot_coor1_x", "lon", "x"])
    tree_plot_col = find_col(trees, ["plot_plot_id1", "plot_id1", "plot_id"])

    # Exclusions per calculation document
    if species_col:
        keep = exclude_by_substrings(trees[species_col], cfg["exclusions"]["tree_species_substrings"])
        trees_live = trees.loc[keep].copy()
        n_excl = int((~keep).sum())
    else:
        trees_live = trees.copy()
        n_excl = 0
    log.append(f"Tree exclusion rows removed by species substrings: {n_excl}")

    # Drop rows missing DBH or height for metric calc (leave missing elsewhere)
    valid = trees_live[dbh_col].notna() & trees_live[ht_col].notna()
    trees_m = trees_live.loc[valid].copy()
    trees_m = apply_tree_metrics(trees_m, dbh_col, ht_col)
    trees_m["plot_uid"] = make_plot_uid(trees_m, tree_su, tree_plot_col) if tree_plot_col else np.nan

    # Anti-clip Gate 1 — NATIONAL master SU universe (retain zero-tree SUs)
    su_ids = su[su_col].astype(str).str.strip().tolist()

    trees_for_gate = trees_m.copy()
    trees_for_gate["su_key"] = trees_for_gate[tree_su].astype(str).str.strip()
    if tree_plot_col is not None:
        trees_for_gate["plot_uid"] = (
            trees_for_gate["su_key"] + "-" + trees_for_gate[tree_plot_col].astype(str).str.strip()
        )
    su_tree = anti_clip_su_tree_counts(su_ids, trees_for_gate, "su_key")
    g1 = {
        "scope": "national_KSA",
        "observed_total_sus": int(len(su_tree)),
        "observed_sus_with_trees": int(su_tree["has_trees"].sum()),
        "observed_sus_no_trees": int((~su_tree["has_trees"]).sum()),
        "note": "SAMPLE_FRAME_ANTI_CLIP_NOT_DESIGN_BASED",
    }

    lattice = build_su_plot_lattice(su_ids, cfg["project"]["plots_per_su"], "su_key")
    g2 = gate2_summary(
        lattice,
        trees_for_gate,
        "su_key",
        plot_uid_col="plot_uid",
        expected=None,
    )

    # Optional Asir GIS validation (does not redefine national frame)
    asir_note = "asir shapefile absent"
    shp = Path(cfg["paths"]["asir_su"])
    if shp.exists():
        try:
            import shapefile

            r = shapefile.Reader(str(shp))
            fields = [f[0] for f in r.fields[1:]]
            su_field = next((n for n in fields if n.upper() in ("SU", "SU_NO", "SU_ID")), fields[0])
            asir_ids = [str(rec[fields.index(su_field)]).strip() for rec in r.records()]
            asir_trees = trees_for_gate[trees_for_gate["su_key"].isin(set(asir_ids))]
            asir_su_tree = anti_clip_su_tree_counts(asir_ids, asir_trees, "su_key")
            g1_asir = gate1_summary(asir_su_tree, cfg["aseer_gate_expected"])
            g2_asir = gate2_summary(
                build_su_plot_lattice(asir_ids, cfg["project"]["plots_per_su"], "su_key"),
                asir_trees,
                "su_key",
                plot_uid_col="plot_uid",
                expected=cfg["aseer_gate_expected"],
            )
            pd.DataFrame([g1_asir]).to_csv(out / "tables" / "asir_gate1_summary.csv", index=False)
            pd.DataFrame([g2_asir["summary"]]).to_csv(out / "tables" / "asir_gate2_summary.csv", index=False)
            asir_note = f"asir validation SUs={len(asir_ids)}"
        except Exception as e:
            asir_note = f"asir validation failed: {e}"
    log.append(asir_note)

    # Save tables
    trees_m.to_csv(out / "tables" / "national_trees_with_provisional_biomass.csv", index=False)
    su_tree.to_csv(out / "tables" / "national_su_anti_clip_tree_counts.csv", index=False)
    g2["lattice"].to_csv(out / "tables" / "national_su_plot_lattice_gate2.csv", index=False)
    pd.DataFrame([g1]).to_csv(out / "tables" / "national_gate1_summary.csv", index=False)
    pd.DataFrame([g2["summary"]]).to_csv(out / "tables" / "national_gate2_summary.csv", index=False)

    # Univariate sample stats (trees with metrics)
    uni_rows = []
    for col in [dbh_col, ht_col, "basal_area_m2", "volume_m3", "agb_mg", "carbon_mg_provisional"]:
        s = trees_m[col].dropna()
        uni_rows.append(
            {
                "variable": col,
                "n": int(s.shape[0]),
                "mean": float(s.mean()),
                "median": float(s.median()),
                "sd": float(s.std(ddof=1)) if len(s) > 1 else np.nan,
                "min": float(s.min()),
                "max": float(s.max()),
                "note": "SAMPLE_STATISTICS_NOT_DESIGN_BASED",
            }
        )
    uni = pd.DataFrame(uni_rows)
    uni.to_csv(out / "tables" / "univariate_tree_biometrics.csv", index=False)

    # Shrubs if columns available
    shrubs = tables.get("shrubs")
    shrub_note = "shrubs not processed (required CD/H columns missing or empty)"
    if shrubs is not None and len(shrubs):
        cd1 = find_col(shrubs, ["crown_diam1", "crown_diameterl1", "crown_diameter_1", "cd1", "crown_d1"])
        cd2 = find_col(shrubs, ["crown_diam2", "crown_diameterl2", "crown_diameter_2", "cd2", "crown_d2"])
        sh_h = find_col(shrubs, ["sh_height", "tree_height", "shrub_height", "height", "height_m"])
        sh_su = find_col(shrubs, [cfg["columns"]["su_id_in_child"], "nfi_of_ksa_program_su_su_no", "su_no"])
        sp = find_col(shrubs, ["species", "shrub_species", "sp_name"])
        sh = shrubs.copy()
        if sh_su is not None:
            sh = sh[sh[sh_su].astype(str).str.strip().isin(set(su_ids))]
        if sp is not None:
            sh = sh.loc[exclude_by_substrings(sh[sp], cfg["exclusions"]["shrub_exclude_substrings"])]
        if cd1 and cd2 and sh_h and len(sh):
            sh = sh.copy()
            sh["mean_CD_m"] = (pd.to_numeric(sh[cd1], errors="coerce") + pd.to_numeric(sh[cd2], errors="coerce")) / 2.0
            h_m = pd.to_numeric(sh[sh_h], errors="coerce")
            # if values look like meters (median < 20), convert to cm per calc doc
            height_cm = np.where(h_m.median(skipna=True) < 20, h_m * 100.0, h_m)
            sh["height_cm"] = height_cm
            ok = sh["mean_CD_m"].notna() & sh["height_cm"].notna() & (sh["mean_CD_m"] > 0) & (sh["height_cm"] > 0)
            sh_ok = sh.loc[ok].copy()
            sh_ok["agb_mg"] = shrub_agb_mg(sh_ok["mean_CD_m"], sh_ok["height_cm"])
            sh_ok["bgb_mg"] = tree_bgb_mg(sh_ok["agb_mg"])
            sh_ok["total_biomass_mg"] = total_biomass_mg(sh_ok["agb_mg"], sh_ok["bgb_mg"])
            sh_ok["carbon_mg_provisional"] = carbon_mg(sh_ok["total_biomass_mg"])
            sh_ok.to_csv(out / "tables" / "national_shrubs_with_provisional_biomass.csv", index=False)
            shrub_note = f"shrubs processed n={len(sh_ok)}"
        else:
            shrub_note = f"shrub columns found cd1={cd1} cd2={cd2} h={sh_h}; insufficient for equation"
    log.append(shrub_note)

    # Modelling: baseline OLS + RF with GroupKFold by SU (spatial-ish block)
    model_rows = []
    X = trees_m[[dbh_col]].to_numpy()
    y = trees_m[ht_col].to_numpy()
    groups = trees_m[tree_su].astype(str).to_numpy()
    # Baseline OLS full sample (descriptive)
    ols = LinearRegression().fit(X, y)
    yhat = ols.predict(X)
    model_rows.append(
        {
            "model": "OLS_height_on_dbh_full_sample",
            "n": int(len(y)),
            "r2": float(r2_score(y, yhat)),
            "rmse": float(np.sqrt(mean_squared_error(y, yhat))),
            "mae": float(mean_absolute_error(y, yhat)),
            "bias": float(np.mean(yhat - y)),
            "coef_dbh": float(ols.coef_[0]),
            "intercept": float(ols.intercept_),
            "note": "SAMPLE_FIT_NOT_DESIGN_BASED",
        }
    )

    gkf = GroupKFold(n_splits=5)
    rf_scores = []
    for fold, (tr, te) in enumerate(gkf.split(X, y, groups), 1):
        rf = RandomForestRegressor(n_estimators=200, random_state=seed, n_jobs=-1, min_samples_leaf=5)
        rf.fit(X[tr], y[tr])
        pred = rf.predict(X[te])
        rf_scores.append(
            {
                "fold": fold,
                "r2": float(r2_score(y[te], pred)),
                "rmse": float(np.sqrt(mean_squared_error(y[te], pred))),
                "mae": float(mean_absolute_error(y[te], pred)),
                "bias": float(np.mean(pred - y[te])),
            }
        )
    rf_df = pd.DataFrame(rf_scores)
    rf_df.to_csv(out / "tables" / "rf_groupkfold_height_on_dbh.csv", index=False)
    model_rows.append(
        {
            "model": "RF_height_on_dbh_GroupKFold5",
            "n": int(len(y)),
            "r2": float(rf_df["r2"].mean()),
            "rmse": float(rf_df["rmse"].mean()),
            "mae": float(rf_df["mae"].mean()),
            "bias": float(rf_df["bias"].mean()),
            "coef_dbh": np.nan,
            "intercept": np.nan,
            "note": "SPATIALLY_BLOCKED_BY_SU_SAMPLE_ONLY",
        }
    )
    pd.DataFrame(model_rows).to_csv(out / "tables" / "model_metrics_summary.csv", index=False)

    # Feature importance from RF fit on all data (report only)
    rf_all = RandomForestRegressor(n_estimators=200, random_state=seed, n_jobs=-1, min_samples_leaf=5)
    # add BA as feature for importance demo
    X2 = np.column_stack([trees_m[dbh_col], trees_m["basal_area_m2"]])
    rf_all.fit(X2, y)
    pd.DataFrame(
        {"feature": [dbh_col, "basal_area_m2"], "importance": rf_all.feature_importances_}
    ).to_csv(out / "tables" / "rf_feature_importance.csv", index=False)

    # Figures
    fig, ax = plt.subplots(figsize=(7, 5), dpi=150)
    ax.hist(trees_m[dbh_col].dropna(), bins=40, color="#2f4f4f", edgecolor="white")
    ax.set_xlabel("DBH (cm)")
    ax.set_ylabel("Count")
    ax.set_title("Figure 1. National KSA tree DBH distribution (sample)")
    fig.tight_layout()
    fig.savefig(out / "figures" / "fig01_dbh_hist.png", dpi=300)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 5), dpi=150)
    ax.scatter(trees_m[dbh_col], trees_m[ht_col], s=8, alpha=0.35, c="#1f4e79")
    xs = np.linspace(trees_m[dbh_col].min(), trees_m[dbh_col].max(), 100).reshape(-1, 1)
    ax.plot(xs, ols.predict(xs), color="#c0392b", lw=2, label="OLS fit")
    ax.set_xlabel("DBH (cm)")
    ax.set_ylabel("Height (m)")
    ax.set_title("Figure 2. Height vs DBH with OLS (sample)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / "figures" / "fig02_height_dbh_ols.png", dpi=300)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 5), dpi=150)
    ax.hist(trees_m["carbon_mg_provisional"].dropna(), bins=40, color="#556b2f", edgecolor="white")
    ax.set_xlabel("Provisional carbon (Mg / tree)")
    ax.set_ylabel("Count")
    ax.set_title("Figure 3. Provisional tree carbon (equation outputs)")
    fig.tight_layout()
    fig.savefig(out / "figures" / "fig03_carbon_hist.png", dpi=300)
    plt.close(fig)

    # Map: plot locations
    if lat_col and lon_col:
        coords = plot[[plot_su, lat_col, lon_col]].copy() if plot_su else plot[[lat_col, lon_col]].copy()
        coords[lat_col] = pd.to_numeric(coords[lat_col], errors="coerce")
        coords[lon_col] = pd.to_numeric(coords[lon_col], errors="coerce")
        coords = coords.dropna(subset=[lat_col, lon_col])
        if plot_su is not None:
            coords = coords[coords[plot_su].astype(str).str.strip().isin(set(su_ids))]
        fig, ax = plt.subplots(figsize=(8, 8), dpi=150)
        ax.scatter(coords[lon_col], coords[lat_col], s=6, c="#0b3d0b", alpha=0.5)
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        ax.set_title("Figure 4. National KSA NFI plot locations (field coordinates)\nCRS: geographic WGS84 assumed from field SRS")
        ax.grid(True, alpha=0.3)
        # north arrow and scale bar (approximate)
        xmin, xmax = ax.get_xlim()
        ymin, ymax = ax.get_ylim()
        ax.annotate("N", xy=(xmax - 0.05 * (xmax - xmin), ymax - 0.08 * (ymax - ymin)),
                    xytext=(xmax - 0.05 * (xmax - xmin), ymax - 0.02 * (ymax - ymin)),
                    arrowprops=dict(arrowstyle="->", color="black"), ha="center")
        # rough 10 km scale at mid-lat
        mid_lat = float(coords[lat_col].median())
        deg_per_km = 1.0 / (111.32 * np.cos(np.deg2rad(mid_lat)))
        x0 = xmin + 0.1 * (xmax - xmin)
        y0 = ymin + 0.05 * (ymax - ymin)
        ax.plot([x0, x0 + 10 * deg_per_km], [y0, y0], color="black", lw=3)
        ax.text(x0 + 5 * deg_per_km, y0 + 0.01 * (ymax - ymin), "10 km", ha="center", fontsize=8)
        fig.tight_layout()
        fig.savefig(out / "maps" / "map01_plot_locations.png", dpi=300)
        plt.close(fig)
        coords.to_csv(out / "tables" / "national_plot_coordinates.csv", index=False)

    # SU tree presence map using plot means if possible
    fig, ax = plt.subplots(figsize=(6, 4), dpi=150)
    ax.bar(["SUs with trees", "SUs zero trees retained"], [g1["observed_sus_with_trees"], g1["observed_sus_no_trees"]],
           color=["#2e7d32", "#9e9e9e"])
    ax.set_title("Figure 5. Anti-clip Gate 1 SU classes (observed)")
    ax.set_ylabel("Count")
    fig.tight_layout()
    fig.savefig(out / "figures" / "fig05_gate1_counts.png", dpi=300)
    plt.close(fig)

    # Decision / run log
    summary = {
        "n_trees_metrics": int(len(trees_m)),
        "n_su_frame": int(len(su_ids)),
        "gate1": g1,
        "gate2": g2["summary"],
        "models": model_rows,
        "shrub_note": shrub_note,
        "policy": cfg["policy"],
        "log": log,
    }
    (out / "logs" / "run_summary.json").write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    print(json.dumps({"gate1": g1, "gate2": g2["summary"], "n_trees": len(trees_m)}, indent=2))
    print("V4 pipeline complete.")
    return summary


if __name__ == "__main__":
    run()
