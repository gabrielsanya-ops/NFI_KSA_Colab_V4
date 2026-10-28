# Phase 0: Inputs inventory

Generated: 2026-10-28  
Workspace: `F:\1.KSA\29.NFI`  
Rules: no em or en dashes; cite only verified local or opened sources.

## 0.1 Environment

| Item | Status |
|------|--------|
| Virtual environment | `F:\1.KSA\29.NFI\.venv` (Python 3.13.2) |
| Starter requirements | `requirements_nfi_kit.txt` (from nfi-cursor-kit) |
| Cursor kit rules | `.cursor/rules/nfi-geopipeline.mdc` |
| Dash checker | `tools/check_dashes.py` |
| Calculation extract | `docs/_calc_doc_extract.md` |

Pinned package versions are written to `outputs_v4/requirements.txt` after install completes.

## 0.2 Key guidance inputs

| Input | Path | Format | Readable |
|-------|------|--------|----------|
| Statistical guide notes | `1.reference_findings\` (junction to `reference_findings\`) | Markdown, DOCX, PDF, CSV | Yes |
| Calculation document | `NFI_ KSA Calculation_Trees&shrubs.docx` | DOCX | Yes (via python-docx / OMML extract) |
| Kit task prompt | `PROMPT_TASK.md` | Markdown | Yes |

### Recommended practices from `1.reference_findings` (field data handling)

| Practice | Source file |
|----------|-------------|
| Keep full SU universe (anti-clip). Do not drop zero-tree SUs. | `01_qualitative/themes_anti_clip_and_gates.md` |
| Field heights are authoritative. Remote height imputation OFF. | `01_qualitative/themes_field_authority_and_AI.md` |
| Label Gate 1 (surveyed zero vs not surveyed vs missing). | `04_validation_gates/trees_gate1_su.md` |
| Gate 2 is completeness, not automatic ecological absence. | `04_validation_gates/trees_gate2_plots.md` |
| Absent regeneration record does not equal zero regeneration. | `04_validation_gates/regeneration_gate1.md` |
| Prefer medians / robust tests when DBH is right-skewed. | `01_qualitative/themes_ecological_structure.md` |
| FV / carbon are provisional equation outputs until certified. | `01_qualitative/themes_provisional_carbon.md` |
| Design-based national estimates blocked without weights, plot areas, inclusion probabilities. | `03_quantitative_national_production/design_gate_blocked.md` |
| Do not overwrite clipped Excel as the master source. | `01_qualitative/excerpts_verbatim.md` |
| Prefer country/biome allometrics (higher FRA tier) when available. | `06_internet_references/INTERNET_REFERENCES.md` |

### Verified internet references (opened locally)

| Reference | Local copy or URL verified |
|-----------|----------------------------|
| FAO Why NFI e-learning PDF | `1.reference_findings/06_internet_references/FAO_NFI_Why_NFI_elearning.pdf` |
| FAO FRA 2025 guidelines PDF | `.../FAO_FRA2025_Guidelines.pdf` |
| FAO allometric equations manual PDF | `.../FAO_Allometric_Equations_Manual.pdf` |
| FAO NFI field manual intro HTML | `.../FAO_NFI_Field_Manual_Intro.html` |
| Henry et al. 2015 PDF | Not downloaded (HTTP 403). URL listed but not cited as verified content. |

## 0.3 Existing notebooks (GeoAI prep)

Location: `KSA_NFI_GeoAI_Data_Preparation_Cursor\nfi_geoai_data_preparation\`

| Notebook | Size (MB) | Role |
|----------|----------:|------|
| `NFI_GeoAI_Data_Preparation_V3_LiDAR_Validation.ipynb` | 15.9 | Latest V3 LiDAR validation lineage (primary audit target) |
| `NFI_GeoAI_Data_Preparation_V3_LiDAR_Validation (1).ipynb` | 15.9 | Duplicate copy |
| `NFI_GeoAI_Data_Preparation_V3_LiDAR_Validation_executed.ipynb` | 22.4 | Executed V3 |
| `NFI_GeoAI_Data_Preparation_V4_Refined.ipynb` | 19.2 | Earlier V4 draft (not kit outputs_v4) |
| `NFI_GeoAI_Data_Preparation_improved*.ipynb` | 9 to 23 | Earlier improved / HTML maps variants |
| `NFI_GeoAI_Data_Preparation.ipynb` | 22.5 | Original |

**Primary existing pipeline for audit:** V3 LiDAR Validation notebook family plus stage outputs under `C:\Users\Admin\NFI_GeoAI_Data_Preparation_Outputs\`.

## 0.4 Field data (cleansed Excel)

Path used in this workspace: `F:\1.KSA\29.NFI\Clensed Data\`  
Note: `config.yaml` still points to `F:\1.KSA\32.NFI\...` which **does not exist** on this machine. V4 config must retarget to `29.NFI`.

| File | Present |
|------|---------|
| trees.xlsx | Yes |
| plot.xlsx | Yes |
| shrubs_bushes.xlsx | Yes |
| regeneration1.xlsx | Yes |
| lucs1.xlsx | Yes |
| vegetation_cover.xlsx | Yes |
| litter1.xlsx | Yes |
| deadwood1.xlsx | Yes |
| fire_evidence1.xlsx | Yes |
| fauna.xlsx | Yes |
| environmental_problems.xlsx | Yes |
| nfi_of_ksa_program_su.xlsx | Yes |
| reference_tbl.xlsx | Yes |
| teams_members.xlsx | Yes |

## 0.5 Spatial layers

| Layer | Path | Present |
|-------|------|---------|
| Asir SU | `Shapefile\Asir NFI Shapefiles\Asir_SU_Final.shp` | Yes |
| Asir Grid | `...\Asir_Grid_15_30_Final.shp` | Yes |
| Makkah SU / Grid | `Shapefile\Makkah NFI Shapefiles\` | Yes |
| NCVC land GDB | `Shapefile\NcvcLandDatabaseVer25.gdb` | Present (container) |

## 0.6 LiDAR / remote height products

| Product | Location | Notes |
|---------|----------|-------|
| GEDI L2A parquet / disparity tables | `C:\Users\Admin\NFI_GeoAI_Data_Preparation_Outputs\lidar\` | Present |
| Meta CHM cache / tiles parquet | same `\lidar\` and `\lidar_cache\` | Present |
| Field vs CHM / GEDI figures | `\lidar\figures\` | Present |
| Raw .las / .laz in workspace | Not found under `29.NFI` | Unreadable / absent here |
| `data\gedi\raw` under notebook project | Empty / minimal | Present folder only |
| H:\Asir_Forest_GeoAI | `H:\Asir_Forest_GeoAI\` | Present (outputs/final). H:\3.NFI path from move note is missing |

## 0.7 Prior pipeline stage outputs (reusable)

`C:\Users\Admin\NFI_GeoAI_Data_Preparation_Outputs\` contains audit CSVs, gates, validated tables, lidar comparisons, maps, SPSS Asir pipeline products. These are **derived** products. Raw cleansed Excel remains authoritative for re-runs.

## 0.8 Calculation document formulas (summary)

Full extract: `docs/_calc_doc_extract.md`.

Trees (individual, then expand):
- BA (m2) = pi * DBH_cm^2 / 40000
- Volume (m3) = BA * height_m * 0.65
- AGB (Mg) = Volume * 0.6 * 2
- BGB (Mg) = AGB * 0.28
- Carbon (Mg) = (AGB + BGB) * 0.47   [Total biomass implied]
- CO2eq (Mg) = Carbon * 3.67
- Plot area for trees: 1000 m2 = 0.1 ha; conversion factor = 10
- Exclude grass, Calotropis, palms from live-tree analysis

Shrubs:
- AGB equation with CD (m) and H (cm); CF = 10; exclude grasses
- BGB = AGB * 0.28; carbon fraction 0.47

Land use:
- Proportion = plots in class / 5; area = proportion * SU area

## 0.9 Unreadable or blocked items

| Item | Issue |
|------|-------|
| `F:\1.KSA\32.NFI\` paths in old config | Path missing; use `29.NFI` copies |
| `H:\3.NFI\` from move note | Not mounted / not found |
| Henry 2015 PDF download | HTTP 403; not used as verified content |
| Worked numeric examples in calculation DOCX | None present |
| Log base in shrub AGB equation | Not stated in source (`[UNCLEAR]`) |
| Whether shrub AGB equation is per-shrub or already Mg/ha | Unclear in source |

## 0.10 Next phase

Phase 1 audits the V3 notebook and stage outputs against this inventory and the calculation document.
