# NFI_KSA_Colab_V4 (scientific revision 4.2 — **national / entire Kingdom**)

End-to-end GeoAI / inventory notebook for the **full KSA NFI** cleansed tables
(≈3,671 SUs · 18,355 plots · 12,732 trees across 13 regions).

Asir Gate 1/2 (430/240/190) remains an **optional validation** when the Asir shapefile is present; it does **not** restrict the national frame.

## Colab (no Drive sync required)

1. Open `NFI_GeoAI_Pipeline_V4_SCIENTIFIC_Colab.ipynb` in Colab.
2. Run cell 0. It will:
   - try Drive paths (`NFI_KSA_Colab_V4` / `NFI_Asir_Colab_V4`), else
   - **auto-clone** this public repo to `/content/NFI_KSA_Colab_V4`.
3. Run remaining cells top-to-bottom.

Optional: sync the whole folder to Drive MyDrive — cell 0 still finds it.

## Design rules

- Anti-clip national SU universe (zero-tree SUs retained)
- No circular BA→height features
- Random vs SU-blocked CV optimism gap
- Provisional carbon constants (FF 0.65, WD 0.6, BEF 2, RS 0.28, C 0.47)
- Sample stats / bootstrap CIs only — national stock totals **BLOCKED** without design weights
