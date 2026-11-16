# PyMOL Publication Styles — Palettes & Rendering Settings Reference

Complete RGB/Hex palettes and PyMOL rendering parameters for all six built-in publication presets.

---

## 1. `baker_rfd` — Baker Lab / IPD (RFdiffusion 1–3)

Derived directly from:
- Watson et al., *Nature* 620, 1089–1100 (2023) (`10.1038/s41586-023-06415-8`)
- Krishna et al., *Science* 384, eadl2528 (2024) (`10.1126/science.adl2528`)
- Ahern et al., *Nature Methods* (2025/2026) (`10.1038/s41592-025-02975-x`)
- Butcher et al., *bioRxiv* (2025) (`10.1101/2025.09.18.676967`)

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

**Key Lighting**: `ray_trace_mode 1`, `ray_trace_gain 0.10`, `spec_reflect 0.0`, `ambient 0.50`, `direct 0.45`, `ambient_occlusion_mode 1`, `ambient_occlusion_scale 15.0`.

---

## 2. `goodsell` — David Goodsell Watercolor Style

Inspired by RCSB PDB *Molecule of the Month* illustrations. Full-atom space-filling `spheres` with quantized cel-shaded outlines (`ray_trace_mode 3`), high ambient flat lighting (`ambient 0.68`, `spec_reflect 0.0`, `ray_shadow 0`), and gentle watercolor tints.

| PyMOL Color Name | Hex | RGB `[R, G, B]` | Role |
|---|---|---|---|
| `goodsell_coral` | `#F29E8E` | `[0.949, 0.620, 0.557]` | Chain 1 / Motif |
| `goodsell_sage` | `#98C9A3` | `[0.596, 0.788, 0.639]` | Chain 2 |
| `goodsell_sky` | `#8FB8DE` | `[0.561, 0.722, 0.871]` | Chain 3 / Binder |
| `goodsell_ochre` | `#F2CC8F` | `[0.949, 0.800, 0.561]` | Chain 4 / Hotspot |
| `goodsell_plum` | `#C39BD3` | `[0.765, 0.608, 0.827]` | Chain 5 / Ligand |
| `goodsell_sand` | `#E6D5B8` | `[0.902, 0.835, 0.722]` | Chain 6 / Target |
| `goodsell_oxygen` | `#D96B6B` | `[0.851, 0.420, 0.420]` | Oxygen atom tint |
| `goodsell_nitrogen` | `#5B82B8` | `[0.357, 0.510, 0.722]` | Nitrogen atom tint |

---

## 3. `cylindrical` — Minimalist Cylindrical-Helix Architecture

`cartoon_cylindrical_helices 1`, `cartoon_helix_radius 1.95`, `cartoon_flat_sheets 1`, `cartoon_loop_radius 0.16`, `ray_trace_mode 1`, `ray_trace_gain 0.06`.

| PyMOL Color Name | Hex | RGB `[R, G, B]` | Role |
|---|---|---|---|
| `arch_navy` | `#2B5C8F` | `[0.169, 0.361, 0.561]` | Primary domain / binder |
| `arch_coral` | `#E07A5F` | `[0.878, 0.478, 0.373]` | Secondary domain / motif |
| `arch_teal` | `#3D9970` | `[0.239, 0.600, 0.439]` | Chain 3 / spectrum stop |
| `arch_gold` | `#E9C46A` | `[0.914, 0.769, 0.416]` | Chain 4 / hotspot |
| `arch_slate` | `#8D99AE` | `[0.553, 0.600, 0.682]` | Neutral target scaffold |

---

## 4. `chimerax_soft` — ChimeraX Soft-Shadow Ceramic Cryo-EM Style

Outline-free (`ray_trace_mode 0`) with strong soft shadows and ambient occlusion (`ray_shadow 1`, `ambient_occlusion_mode 1`, `ambient_occlusion_scale 25.0`, `ambient_occlusion_smooth 15`, `surface_quality 1`, `spec_reflect 0.05`).

| PyMOL Color Name | Hex | RGB `[R, G, B]` | Role |
|---|---|---|---|
| `em_cobalt` | `#4A7C9B` | `[0.290, 0.486, 0.608]` | Subunit 1 / Binder |
| `em_salmon` | `#E28775` | `[0.886, 0.529, 0.459]` | Subunit 2 / Hotspot |
| `em_mint` | `#6EB599` | `[0.431, 0.710, 0.600]` | Subunit 3 / Motif |
| `em_ochre` | `#E5B869` | `[0.898, 0.722, 0.412]` | Subunit 4 |
| `em_clay` | `#D8D4CE` | `[0.847, 0.831, 0.808]` | Matte ceramic target surface |

---

## 5. `spotlight` — Monochrome Ghost + Jewel-Tone Spotlight

Transparent porcelain scaffold (`spot_ghost_gray #E2E4E8`, `cartoon_transparency 0.62`) with opaque ball-and-stick focal residues (`stick_radius 0.25`, `stick_ball 1`).

| PyMOL Color Name | Hex | RGB `[R, G, B]` | Role |
|---|---|---|---|
| `spot_ghost_gray` | `#E2E4E8` | `[0.886, 0.894, 0.910]` | Semi-transparent background protein |
| `spot_crimson` | `#E63946` | `[0.902, 0.224, 0.275]` | Catalytic residues / mutation highlight |
| `spot_cyan` | `#00B4D8` | `[0.000, 0.706, 0.847]` | Ligand / partner binder highlight |
| `spot_amber` | `#F4A261` | `[0.957, 0.635, 0.380]` | Secondary hotspot highlight |
| `spot_dash_gray` | `#555860` | `[0.333, 0.345, 0.376]` | Minimalist H-bond dashes |

---

## 6. `alphafold_plddt` — Canonical AlphaFold pLDDT Confidence Style

| PyMOL Color Name | Hex | RGB `[R, G, B]` | pLDDT Range |
|---|---|---|---|
| `af_very_high` | `#0053D6` | `[0.000, 0.325, 0.839]` | $\text{pLDDT} \ge 90$ |
| `af_confident` | `#65CBF3` | `[0.396, 0.796, 0.953]` | $70 \le \text{pLDDT} < 90$ |
| `af_low` | `#FFDB13` | `[1.000, 0.859, 0.075]` | $50 \le \text{pLDDT} < 70$ |
| `af_very_low` | `#FF7D45` | `[1.000, 0.490, 0.271]` | $\text{pLDDT} < 50$ |
