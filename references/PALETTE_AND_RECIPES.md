# IPD / RFdiffusion 1–3 Palette & Visual Reference

Exact RGB triplets and PyMOL settings extracted from:
- **RFdiffusion 1**: Watson et al., *Nature* 620, 1089–1100 (2023) (`10.1038/s41586-023-06415-8`)
- **RFdiffusion2**: Ahern et al., *Nature Methods* (2025/2026) (`10.1038/s41592-025-02975-x`)
- **RFdiffusion3**: Butcher et al., *bioRxiv* (2025) (`10.1101/2025.09.18.676967`)
- **RFdiffusionAA**: Krishna et al., *Science* 384, eadl2528 (2024) (`10.1126/science.adl2528`)

## 1. Registered Color Table

| PyMOL Color Name | Hex | RGB `[R, G, B]` | Paper Usage |
|---|---|---|---|
| `ipd_pastel_peach` | `#FCD4AC` | `[0.988, 0.831, 0.675]` | N-terminal spectrum stop 1; Oligomer chain 1 |
| `ipd_pastel_rose` | `#FCACB4` | `[0.988, 0.675, 0.706]` | Spectrum stop 2; Oligomer chain 2; RFD1 Fig. 4c binder |
| `ipd_pastel_lavender` | `#9494C4` | `[0.580, 0.580, 0.769]` | Spectrum stop 3; Oligomer chain 3; RFD1 Fig. 6 binder |
| `ipd_pastel_slate` | `#6C88C4` | `[0.424, 0.533, 0.769]` | Spectrum stop 4 (light); RFD2 scaffold |
| `ipd_pastel_deepblue` | `#5064AC` | `[0.314, 0.392, 0.675]` | C-terminal spectrum stop 4 (deep); Oligomer chain 4 |
| `ipd_pastel_iceblue` | `#A8BCE0` | `[0.659, 0.737, 0.878]` | RFD2 Fig. 1/4 ultra-soft periwinkle scaffold; DNA backbone |
| `ipd_motif_teal` | `#4CB8AC` | `[0.298, 0.722, 0.675]` | Signature IPD functional motif / catalytic side-chain carbons |
| `ipd_target_sand` | `#FCDCA8` | `[0.988, 0.863, 0.659]` | RFD1 Fig. 6 target molecular surface |
| `ipd_hotspot_orange` | `#F08828` | `[0.941, 0.533, 0.157]` | RFD1 Fig. 6 target epitope hotspot patch |
| `ipd_strand_gold` | `#E8BC58` | `[0.910, 0.737, 0.345]` | Conditioned β-strand / 2Fo-Fc density |
| `ipd_model_gray` | `#C8C8CD` | `[0.784, 0.784, 0.804]` | Design / AF2 / Crystal overlay comparison gray |
| `ipd_surface_gray` | `#E6E6EB` | `[0.902, 0.902, 0.922]` | Neutral target surface / cryo-EM density envelope |
| `ipd_slate_gray` | `#7A828E` | `[0.478, 0.510, 0.557]` | RFD2 non-motif Cα–Cβ side-chain connector atoms |
| `ipd_ligand_carbon` | `#48484C` | `[0.282, 0.282, 0.298]` | Substrate / reactant / cofactor carbon sticks |
| `ipd_metal_green` | `#587038` | `[0.345, 0.439, 0.220]` | Mg(II) cofactor sphere |
| `ipd_metal_ochre` | `#A85838` | `[0.659, 0.345, 0.220]` | Zn(II) / Fe / Ni cofactor sphere |
| `ipd_vh_navy` | `#344888` | `[0.204, 0.282, 0.533]` | Antibody VH chain (RFD-Ab Fig. 5) |

## 2. Core Theme Parameters

- **Background & Orthographic Projection**: `bg_color white`, `ray_opaque_background 1`, `orthoscopic 1`, `depth_cue 1`, `fog_start 0.45`.
- **Cel-Shaded Matte Outlines**: `ray_trace_mode 1`, `ray_trace_gain 0.10`, `ray_trace_color black`, `spec_reflect 0.0`, `ambient 0.50`, `direct 0.45`, `reflect 0.25`, `light_count 4`, `ray_shadow 0`, `ambient_occlusion_mode 1`, `ambient_occlusion_scale 15.0`, `antialias 2`.
- **Clean Cartoon & Ball-and-Stick**: `cartoon_loop_radius 0.18`, `cartoon_oval_length 1.20`, `cartoon_oval_width 0.25`, `cartoon_highlight_color -1`, `stick_radius 0.22`, `stick_ball 1`, `stick_ball_ratio 1.4`.
