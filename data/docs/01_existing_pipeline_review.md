# Phase 1: Existing pipeline audit (V3 LiDAR Validation)

Primary target: `KSA_NFI_GeoAI_Data_Preparation_Cursor/nfi_geoai_data_preparation/NFI_GeoAI_Data_Preparation_V3_LiDAR_Validation.ipynb` (45 cells).  
Stage products: `C:\Users\Admin\NFI_GeoAI_Data_Preparation_Outputs\` (pre-existing; V4 does not require writing there).  
Calculation authority: `docs/_calc_doc_extract.md`.

## Stages observed in V3

| Stage | Cell banners | Purpose |
|------:|--------------|---------|
| 1 | Tabular ingest and Asir SU universe | Load Excel, join keys, 430-SU GIS master |
| 2 | Area appropriation | Attach Area_H, compare equal-area vs Mercator misuse |
| 3 | SU x plot lattice | Anti-clip long-form (2,150 rows) |
| 4 | Gate 1 and Gate 2 | Reconcile validation-package targets |
| 5 | Regional roll-ups | Region / governorate tables |
| 6 | Cleaning / QC | Spelling, types, corrections |
| 7 / 7b | Ready deliverables; field vs office coords | Clean joins; GPS cross-check |
| 8 | Analytical population | Eligibility without imputation |
| 9 / 10 | Statistical QA and EDA | Completeness, outliers, figures |
| 11 | Integrity scorecard | Clip/pivot vs anti-clip |
| 12 / 13 | Cartography / HTML atlas | Leaflet maps |
| 14 | Spatial left-join QA | Plots to grid without silent drop |
| 15 | GEDI L2A LiDAR | RH98 vs field; no imputation |
| 16 | GeoAI protocol | Spatial CV, uncertainty, no imputation |
| 17 / 18 | StageStore / ledger | Exports and sign-off |

## Issue table

| Issue | Evidence | Proposed fix (V4) | Justification |
|-------|----------|-------------------|---------------|
| Config paths point to missing `F:\1.KSA\32.NFI` | `config.yaml` paths; Phase 0 inventory | Retarget all paths to `F:\1.KSA\29.NFI` in `outputs_v4/config.yaml` | Workspace reality; avoid silent load failure |
| Biomass constants not unit-tested against calculation DOCX | V3 provisional FV fields; no pytest suite in notebook project | `nfi_v4.biomass` + `tests/test_biomass_formulas.py` | Calculation document is authoritative for tree/shrub equations |
| Design-based estimates still not possible | `survey_design_readiness.md` BLOCKED; reference notes | Keep `design_based_estimates: false`; label all outputs as sample statistics | Missing weights, plot areas, inclusion probabilities |
| Risk of treating absence as zero regeneration / zero trees | Gate docs; qualitative themes | Explicit Gate 1 / Gate 2 tables; regeneration absence rule documented | Reference findings anti-clip / gate themes |
| Remote height imputation temptation | V3 banners: NO IMPUTATION; LiDAR as disparity only | `policy.remote_height_imputation: false` enforced in config and report | Field authority theme |
| Notebook monolith hard to test | 15 to 22 MB notebooks | Modular `src/nfi_v4` + `run_pipeline.py` + thin V4 notebook | Reproducibility and unit tests |
| Leakage risk if random CV used on clustered plots | GeoAI protocol cell mentions spatial CV | GroupKFold by SU in V4 models | Spatial blocking reduces plot-within-SU leakage |
| Carbon / volume may not match DOCX constants exactly in older provisional fields | Need verification vs form factor 0.65, WD 0.6, BEF 2, RS 0.28, C 0.47 | Recompute metrics in V4 from DOCX constants only | Formula integrity |
| Disk / path fragility (F: full historically) | Phase 0 disk incident | Keep all V4 outputs under workspace `outputs_v4/` only | User constraint: everything in workspace |
| Shrub allometric log base unclear | Calc extract `[UNCLEAR]` | Document assumption (natural log) in config and open questions | No hallucination of undocumented base |

## Strengths to retain

- Anti-clip SU universe and Gate 1 / Gate 2 targets (430 / 240 / 190; 2150 / 656 / 544).
- Field-first height policy and GEDI as corroboration, not overwrite.
- StageStore pattern for intermediate products.
- Explicit sample-vs-design-based language in production audit.
