# PyMOL Publication Styles — Palettes & Rendering Settings Reference

Complete RGB/Hex palettes and PyMOL rendering parameters for all **10 built-in publication & AIDD presets**.

---

## 1. `baker_rfd` — Baker Lab / IPD (RFdiffusion 1–3)

Derived from Watson et al. (*Nature* 2023), Krishna et al. (*Science* 2024), Ahern et al. (*Nature Methods* 2025/2026), and Butcher et al. (*bioRxiv* 2025).

| PyMOL Color Name | Hex | RGB `[R, G, B]` | Role |
|---|---|---|---|
| `ipd_pastel_peach` | `#FCD4AC` | `[0.988, 0.831, 0.675]` | N-terminal stop 1; Oligomer chain 1 |
| `ipd_pastel_rose` | `#FCACB4` | `[0.988, 0.675, 0.706]` | Stop 2; Oligomer chain 2 |
| `ipd_pastel_lavender` | `#9494C4` | `[0.580, 0.580, 0.769]` | Stop 3; Default de novo binder |
| `ipd_pastel_slate` | `#6C88C4` | `[0.424, 0.533, 0.769]` | Stop 4 (light) |
| `ipd_pastel_deepblue` | `#5064AC` | `[0.314, 0.392, 0.675]` | C-terminal stop 4 (deep); Oligomer chain 4 |
| `ipd_pastel_iceblue` | `#A8BCE0` | `[0.659, 0.737, 0.878]` | RFD2 soft periwinkle scaffold; DNA duplex |
| `ipd_motif_teal` | `#4CB8AC` | `[0.298, 0.722, 0.675]` | Signature functional motif & catalytic side-chain carbons |
| `ipd_target_sand` | `#FCDCA8` | `[0.988, 0.863, 0.659]` | Target surface in binder design |
| `ipd_hotspot_orange` | `#F08828` | `[0.941, 0.533, 0.157]` | Target epitope hotspot surface/residues |
| `ipd_strand_gold` | `#E8BC58` | `[0.910, 0.737, 0.345]` | Conditioned β-strand / 2Fo-Fc map |
| `ipd_model_gray` | `#C8C8CD` | `[0.784, 0.784, 0.804]` | Overlay reference / AF2 / crystal gray |
| `ipd_surface_gray` | `#E6E6EB` | `[0.902, 0.902, 0.922]` | Neutral target surface / cryo-EM envelope |
| `ipd_slate_gray` | `#7A828E` | `[0.478, 0.510, 0.557]` | RFD2 non-motif Cα/Cβ connector atoms |
| `ipd_ligand_carbon` | `#48484C` | `[0.282, 0.282, 0.298]` | Substrate / small-molecule carbon sticks |
| `ipd_metal_green` | `#587038` | `[0.345, 0.439, 0.220]` | Mg(II) cofactor sphere |
| `ipd_metal_ochre` | `#A85838` | `[0.659, 0.345, 0.220]` | Zn(II) / Fe / Ni cofactor sphere |
| `ipd_vh_navy` | `#344888` | `[0.204, 0.282, 0.533]` | Antibody VH chain |

**Key Lighting (Paper Cutout Illustration Theme for `baker_rfd`, `antibody_cdr`, `spotlight`)**: `specular 0`, `ray_shadow 0`, `valence 0`, `antialias 2`, `ray_trace_mode 1`, `ray_trace_disco_factor 1`, `ray_trace_gain 0.1`, `power 0.2`, `ambient 0.4`, `ray_trace_color gray30`, `stick_ball 0`, `ambient_occlusion_mode 0`, `cartoon_side_chain_helper 1`, `cartoon_smooth_loops 0`.

### Paper Cutout Illustration Colors (`paper_*`)

| PyMOL Color Name | Hex | RGB `[R, G, B]` | Role |
|---|---|---|---|
| `paper_paleblue` | `#E6EBF5` | `[0.902, 0.922, 0.961]` | Pale cool highlight / background |
| `paper_lightblue` | `#9596C6` | `[0.584, 0.588, 0.776]` | VH framework |
| `paper_blue` | `#6686C5` | `[0.400, 0.525, 0.773]` | CDR-H1 |
| `paper_darkblue` | `#4B5FAA` | `[0.294, 0.373, 0.667]` | CDR-H2 |
| `paper_palepurple` | `#F5E6EE` | `[0.961, 0.902, 0.933]` | Pale lavender highlight |
| `paper_lightpurple` | `#E4B9CD` | `[0.894, 0.725, 0.804]` | VL framework |
| `paper_purple` | `#D59AB5` | `[0.835, 0.604, 0.710]` | CDR-L1 / CDR-L2 |
| `paper_darkpurple` | `#AF698C` | `[0.686, 0.412, 0.549]` | CDR-L3 |
| `paper_melon` | `#FFC6B2` | `[1.000, 0.776, 0.698]` | Antigen / base scaffold cartoon |
| `paper_teal` | `#4FB9AF` | `[0.310, 0.725, 0.686]` | CDR-H3 / focal mutation highlight |

---

## 2. `goodsell` — David Goodsell Watercolor Style

Full-atom `spheres` with `ray_trace_mode 3`, flat high ambient (`ambient 0.68`, `spec_reflect 0.0`, `ray_shadow 0`), and gentle O/N tints:
`goodsell_coral` (`#F29E8E`), `goodsell_sage` (`#98C9A3`), `goodsell_sky` (`#8FB8DE`), `goodsell_ochre` (`#F2CC8F`), `goodsell_plum` (`#C39BD3`), `goodsell_sand` (`#E6D5B8`), `goodsell_oxygen` (`#D96B6B`), `goodsell_nitrogen` (`#5B82B8`).

---

## 3. `cylindrical` — Minimalist Cylindrical-Helix Architecture

`cartoon_cylindrical_helices 1`, `cartoon_helix_radius 1.95`, `cartoon_flat_sheets 1`, `cartoon_loop_radius 0.16`, `ray_trace_mode 1`, `ray_trace_gain 0.06`:
`arch_navy` (`#2B5C8F`), `arch_coral` (`#E07A5F`), `arch_teal` (`#3D9970`), `arch_gold` (`#E9C46A`), `arch_slate` (`#8D99AE`).

---

## 4. `chimerax_soft` — ChimeraX Soft-Shadow Ceramic Cryo-EM Style

Outline-free (`ray_trace_mode 0`) with strong AO & soft shadows (`ray_shadow 1`, `ambient_occlusion_mode 1`, `ambient_occlusion_scale 25.0`, `surface_quality 1`):
`em_cobalt` (`#4A7C9B`), `em_salmon` (`#E28775`), `em_mint` (`#6EB599`), `em_ochre` (`#E5B869`), `em_clay` (`#D8D4CE`).

---

## 5. `spotlight` — Monochrome Ghost + Jewel-Tone Spotlight

Transparent porcelain scaffold (`spot_ghost_gray #E2E4E8`, `cartoon_transparency 0.62`) + opaque ball-and-stick focal sites (`spot_crimson #E63946`, `spot_cyan #00B4D8`, `spot_amber #F4A261`, `spot_dash_gray #555860`).

---

## 6. `alphafold_plddt` — Canonical AlphaFold pLDDT Confidence Style

`af_very_high` (`#0053D6`, $\ge 90$), `af_confident` (`#65CBF3`, $70\text{–}90$), `af_low` (`#FFDB13`, $50\text{–}70$), `af_very_low` (`#FF7D45`, $< 50$).

---

## 7. `antibody_cdr` — Paper-Illustration Antibody CDR Loops

Uses the `paper_*` palette and clean paper-cutout ray-tracing (`ray_trace_color gray30`, `valence 0`, `stick_ball 0`, `power 0.2`, `ambient 0.4`):
`paper_melon` (`#FFC6B2`, antigen), `paper_lightblue` (`#9596C6`, VH), `paper_blue` (`#6686C5`, CDR-H1), `paper_darkblue` (`#4B5FAA`, CDR-H2), `paper_teal` (`#4FB9AF`, CDR-H3), `paper_lightpurple` (`#E4B9CD`, VL), `paper_purple` (`#D59AB5`, CDR-L1/L2), `paper_darkpurple` (`#AF698C`, CDR-L3).

---

## 8. `hydrophobic_surface` — Eisenberg Hydrophobic Complementarity

`hydro_polar` (`#DCE8F2`), `hydro_neutral` (`#F5F3EE`), `hydro_moderate` (`#F2C57C`), `hydro_core` (`#D96B43`), `hydro_binder_bg` (`#A8BCE0`). Highlights binder hydrophobic anchor sidechains (`I/V/L/F/W/Y/M`) within 4.5 Å of the target.

---

## 9. `pocket_cavity` — Local Pocket Cutaway & Pose Overlay

`pocket_surf_tint` (`#D8E2EC`, local `surface` within 6 Å at `transparency 0.42`), `pocket_res_carbon` (`#8D99AE`), `pose_ref_carbon` (`#4CB8AC`), `pose_pred_carbon` (`#E0569B`).

---

## 10. `diffusion_ensemble` — Multi-State Ghost Ensemble & Putty Flexibility

`ens_state_early` (`#D8DCE6`, `cartoon_transparency 0.78`), `ens_state_final` (`#485CA8`, solid). Falls back to `cartoon putty` flexibility scaling when a single-state structure is supplied.
