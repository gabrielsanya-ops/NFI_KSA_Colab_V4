# Phase 2: Data understanding

Sources: `Clensed Data\*.xlsx`, Asir shapefile `Asir_SU_Final.shp`, V4 run outputs under `outputs_v4/tables/`.  
All statistics below are **sample statistics** (design-based gate blocked).

## Plot design

- Sampling unit (SU) with **5 plots** per SU (calculation document; config `plots_per_su: 5`).
- Tree plot area stated in calculation document: **1000 m2 = 0.1 ha**, conversion factor **10**.
- Asir analytical frame from GIS: **430 SUs**, lattice **2,150** SU x plot rows.

## National cleansed table profile (full Excel)

| Table | Rows | Notes |
|-------|-----:|-------|
| nfi_of_ksa_program_su.xlsx | 3,671 | SU master; high missingness on village/altitude/teams |
| plot.xlsx | 18,355 | Field coords missing ~68% |
| trees.xlsx | 12,732 | Core biometrics present; many photo/agent fields empty |
| shrubs_bushes.xlsx | 4,823 | crown_diam1/2, sh_height |
| lucs1.xlsx | 18,360 | Low missingness |
| regeneration1.xlsx | 527 | Sparse vs SU universe |
| vegetation_cover.xlsx | 18,326 | |
| litter1.xlsx | 5,689 | |
| fire_evidence1.xlsx | 4,148 | Most cause/area fields ~100% missing |
| deadwood1.xlsx | 244 | |
| fauna.xlsx | 664 | |
| environmental_problems.xlsx | 7,977 | Severity/trends ~46% missing |
| teams_members.xlsx | 4,061 | |
| reference_tbl.xlsx | 148 | |

Full column lists: `docs/_profile_raw.txt`.

## Asir V4 analytical population (computed)

| Metric | Value |
|--------|------:|
| SU frame | 430 |
| SUs with trees | 240 |
| SUs zero trees retained | 190 |
| Tree records with DBH and height | 6,513 |
| Plots with trees (lattice) | 656 |
| Gate 2 candidate plots | 544 |

Gate 1 and Gate 2 **exact match** to validation targets (see `outputs_v4/tables/gate1_summary.csv`, `gate2_summary.csv`).

## Data dictionary (key fields)

| Field | Table | Type | Unit | Valid range (ops) | Source |
|-------|-------|------|------|-------------------|--------|
| su_no | SU master | ID | - | unique SU | cleansed SU |
| nfi_of_ksa_program_su_su_no | child tables | ID | - | joins to su_no | cleansed |
| plot_id1 / plot_plot_id1 | plot / trees | ID | - | 1 to 5 typical | cleansed |
| tree_dbh | trees | float | cm (implied by BA formula) | >0 | field |
| tree_height | trees | float | m | >0 | field |
| tree_species_scientific_name | trees | text | - | - | field |
| crown_diam1 / crown_diam2 | shrubs | float | m (assumed) | >0 | field |
| sh_height | shrubs | float | m or cm (V4 detects) | >0 | field |
| plot_info1_plot_coor1_x/y | plot | float | geographic | finite | field GPS |
| Area_H (GIS) | Asir SU shp | float | ha | >0 | shapefile |

Derived V4 fields: `basal_area_m2`, `volume_m3`, `agb_mg`, `bgb_mg`, `total_biomass_mg`, `carbon_mg_provisional`, `co2eq_mg_provisional` (calculation document).

## Quality audit (Asir trees used in V4)

- DBH / height completeness for metric subset: required non-null (6,513 rows).
- Species exclusion substrings (Calotropis, palm, grass): **0** rows removed in this run (no matching scientific names under those substrings).
- Impossible values: not dropped; flagged for review if DBH or height <= 0 (none in metric subset).
- CRS: field coordinates treated as geographic WGS84 for mapping when SRS present; no silent reprojection.
- Logical conflict: Gate 2 plots lack trees while parent SU has some trees elsewhere (completeness issue, not auto-zero).

## Missingness highlights

- Plot field coordinates: ~68% missing nationally (limits map n).
- Fire cause/area: nearly empty.
- Regeneration: only 527 rows nationally; absence at SU is not zero regeneration.
- Shrub language variety / photos: largely missing; crown diameters and height usable for a subset.

## Species / growth form

- Trees: live-tree analysis after stump/condition filters in calc doc; V4 applies species substring exclusions and requires DBH+height.
- Shrubs: separate table; grasses excluded per calc doc; AGB via crown diameter + height equation.

## Asir univariate biometrics (V4, n=6,513)

| Variable | Mean | Median | SD | Min | Max |
|----------|-----:|-------:|---:|----:|----:|
| tree_dbh (cm) | 7.81 | 6.00 | 5.11 | 0.5 | 64.3 |
| tree_height (m) | 3.68 | 3.30 | 1.70 | 0.2 | 20.0 |
| basal_area_m2 | 0.00684 | 0.00283 | 0.0130 | ~0 | 0.325 |
| volume_m3 | 0.0240 | 0.00625 | 0.0740 | ~0 | 2.12 |
| agb_mg (provisional) | 0.0288 | 0.00750 | 0.0888 | ~0 | 2.55 |
| carbon_mg_provisional | 0.0173 | 0.00451 | 0.0534 | ~0 | 1.53 |

See `outputs_v4/tables/univariate_tree_biometrics.csv`.
