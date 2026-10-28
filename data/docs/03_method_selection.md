# Phase 3: Method selection (decision matrix)

References used only if verified locally or opened: calculation DOCX extract; `1.reference_findings` themes; FAO PDFs in `1.reference_findings/06_internet_references/`.

| Problem | Candidate methods | Chosen method | Evidence | Reference |
|---------|-------------------|---------------|----------|-----------|
| Zero-tree SUs | Clip to tree SUs; impute zeros; anti-clip LEFT join | **Anti-clip LEFT join; retain 190 zeros** | Gate 1 match 430/240/190 | `themes_anti_clip_and_gates.md`; V3 Stage 3-4 |
| Missing tree heights | Mean/median impute; kNN; MICE; GEDI/CHM overwrite; leave missing | **Leave missing for biomass; no remote overwrite** | Field authority; imputation OFF | `themes_field_authority_and_AI.md`; V3 LiDAR banners; calc doc uses field H |
| Missing DBH or height for equations | Impute then expand; drop row from metric table but keep in gate lattice | **Complete-case for metric columns only; gates use full lattice** | Sensitivity: inventing H/DBH would fabricate carbon | Calc doc requires DBH and H; open questions log |
| Missingness mechanism | Assume MCAR; formal Little test; MAR via covariates | **Describe patterns; treat regeneration/fire as MNAR-risk (survey process)** | Regeneration absence != zero; fire cause 100% missing | Gate regeneration note; profile missingness |
| Outliers | Delete IQR outliers; winsorize; robust stats + flag | **Flag / report; do not delete for Gates** | V3 QA: no deletion | V3 statistical QA banner; reference skew guidance |
| Field vs LiDAR conflict | Prefer LiDAR; average; disparity only | **Disparity / corroboration only** | Remote imputation OFF | V3 GEDI stage; reference findings |
| National totals | Naive mean * area; design-based HT; model-assisted | **Do not publish design-based totals** | Weights/plot areas missing | `design_gate_blocked.md`; FRA guidance needs proper expansion |
| Tree biomass | Prior provisional fields; DOCX chain | **DOCX chain: BA, V=BA*H*0.65, AGB=V*0.6*2, BGB=0.28*AGB, C=0.47** | Unit tests pass | `_calc_doc_extract.md`; FAO allometrics manual (tier context) |
| Shrub biomass | Skip; tree equations; DOCX shrub AGB | **DOCX shrub AGB with natural log assumption** | n=968 processed | Calc extract; log base unclear documented |
| Inference language | Call means "national estimates" | **Label SAMPLE_STATISTICS_NOT_DESIGN_BASED** | Blocked gate | Production audit |
| Baseline height model | None; OLS only | **OLS height ~ DBH** | R2=0.392 sample fit | Classical baseline first |
| Advanced model | RF without blocking; deep net | **RF with GroupKFold by SU** | Mean CV R2=0.437 | Spatial leakage control; GeoAI protocol spirit |
| Uncertainty | Point only | **CV RMSE/MAE/bias; provisional carbon label** | Model metrics table | Method reporting good practice |
| Qualitative lineage | Ad hoc notes | **Phase docs + decision log + run_summary.json** | Kit Phase 3 requirement | PROMPT_TASK |

## Sensitivity note (missingness)

Inventing heights for incomplete trees would change carbon totals without field evidence. V4 therefore restricts biomass to complete DBH+height cases while Gate tables keep the full 430 x 5 universe. This follows reference guidance to leave values missing where absence is structural or unverified.
