"""
PyMOL Publication Styles Engine.

Supports 10 classic structural biology & AIDD publication styles:
  1. baker_rfd          : Baker Lab / IPD RFdiffusion 1-3 matte cel-shaded pastel style (default)
  2. goodsell           : David Goodsell / RCSB Molecule of the Month watercolor sphere style
  3. cylindrical        : Nature / Cell minimalist cylindrical-helix architecture style
  4. chimerax_soft      : ChimeraX soft-shadow / matte ceramic ambient-occlusion cryo-EM style
  5. spotlight          : Monochrome ghost scaffold + jewel-tone focal spotlight style
  6. alphafold_plddt    : Canonical AlphaFold / ColabFold pLDDT confidence threshold style
  7. antibody_cdr       : Antibody VH/VL framework + color-coded CDR loops + 4.5 A epitope footprint
  8. hydrophobic_surface: Eisenberg hydrophobicity surface + binder hydrophobic anchor sticks
  9. pocket_cavity      : Local pocket cutaway surface + dual-color ligand pose overlay
 10. diffusion_ensemble : Multi-state diffusion/MD ghost ensemble or putty flexibility rendering

Provides transparent background & auto-cropping, global+inset composite stitching,
in-pocket ligand heavy-atom RMSD, trajectory strips, and multi-style showcase grids.
"""

from __future__ import annotations

import math
import os
import shutil
from typing import Dict, List, Optional, Sequence, Tuple

VALID_STYLES = (
    "baker_rfd",
    "goodsell",
    "cylindrical",
    "chimerax_soft",
    "spotlight",
    "alphafold_plddt",
    "antibody_cdr",
    "hydrophobic_surface",
    "pocket_cavity",
    "diffusion_ensemble",
)

CORE_SHOWCASE_STYLES = (
    "baker_rfd",
    "goodsell",
    "cylindrical",
    "chimerax_soft",
    "spotlight",
    "alphafold_plddt",
)

# Exact RGB float triplets [R, G, B]
PUBLICATION_PALETTES: Dict[str, List[float]] = {
    # 1. Baker Lab / IPD RFdiffusion 1-3 Palette
    "ipd_pastel_peach": [0.988, 0.831, 0.675],     # #FCD4AC
    "ipd_pastel_rose": [0.988, 0.675, 0.706],      # #FCACB4
    "ipd_pastel_lavender": [0.580, 0.580, 0.769],  # #9494C4
    "ipd_pastel_slate": [0.424, 0.533, 0.769],     # #6C88C4
    "ipd_pastel_deepblue": [0.314, 0.392, 0.675],  # #5064AC
    "ipd_pastel_iceblue": [0.659, 0.737, 0.878],   # #A8BCE0
    "ipd_motif_teal": [0.298, 0.722, 0.675],       # #4CB8AC
    "ipd_target_sand": [0.988, 0.863, 0.659],      # #FCDCA8
    "ipd_hotspot_orange": [0.941, 0.533, 0.157],   # #F08828
    "ipd_strand_gold": [0.910, 0.737, 0.345],      # #E8BC58
    "ipd_model_gray": [0.784, 0.784, 0.804],       # #C8C8CD
    "ipd_surface_gray": [0.902, 0.902, 0.922],     # #E6E6EB
    "ipd_slate_gray": [0.478, 0.510, 0.557],       # #7A828E
    "ipd_ligand_carbon": [0.282, 0.282, 0.298],    # #48484C
    "ipd_metal_green": [0.345, 0.439, 0.220],      # #587038
    "ipd_metal_ochre": [0.659, 0.345, 0.220],      # #A85838
    "ipd_vh_navy": [0.204, 0.282, 0.533],          # #344888

    # 2. David Goodsell Watercolor Palette
    "goodsell_coral": [0.949, 0.620, 0.557],       # #F29E8E
    "goodsell_sage": [0.596, 0.788, 0.639],        # #98C9A3
    "goodsell_sky": [0.561, 0.722, 0.871],         # #8FB8DE
    "goodsell_ochre": [0.949, 0.800, 0.561],       # #F2CC8F
    "goodsell_plum": [0.765, 0.608, 0.827],        # #C39BD3
    "goodsell_sand": [0.902, 0.835, 0.722],        # #E6D5B8
    "goodsell_oxygen": [0.851, 0.420, 0.420],      # #D96B6B
    "goodsell_nitrogen": [0.357, 0.510, 0.722],    # #5B82B8

    # 3. Minimalist Cylindrical Architecture Palette
    "arch_navy": [0.169, 0.361, 0.561],            # #2B5C8F
    "arch_coral": [0.878, 0.478, 0.373],           # #E07A5F
    "arch_teal": [0.239, 0.600, 0.439],            # #3D9970
    "arch_gold": [0.914, 0.769, 0.416],            # #E9C46A
    "arch_slate": [0.553, 0.600, 0.682],           # #8D99AE

    # 4. ChimeraX Soft-Shadow / Cryo-EM Ceramic Palette
    "em_cobalt": [0.290, 0.486, 0.608],            # #4A7C9B
    "em_salmon": [0.886, 0.529, 0.459],            # #E28775
    "em_mint": [0.431, 0.710, 0.600],              # #6EB599
    "em_ochre": [0.898, 0.722, 0.412],             # #E5B869
    "em_clay": [0.847, 0.831, 0.808],              # #D8D4CE

    # 5. Monochrome Ghost + Spotlight Palette
    "spot_ghost_gray": [0.886, 0.894, 0.910],      # #E2E4E8
    "spot_crimson": [0.902, 0.224, 0.275],         # #E63946
    "spot_cyan": [0.000, 0.706, 0.847],            # #00B4D8
    "spot_amber": [0.957, 0.635, 0.380],           # #F4A261
    "spot_dash_gray": [0.333, 0.345, 0.376],       # #555860

    # 6. AlphaFold Canonical pLDDT Palette
    "af_very_high": [0.000, 0.325, 0.839],         # #0053D6
    "af_confident": [0.396, 0.796, 0.953],         # #65CBF3
    "af_low": [1.000, 0.859, 0.075],               # #FFDB13
    "af_very_low": [1.000, 0.490, 0.271],          # #FF7D45

    # 7. Antibody CDR & Epitope Footprint Palette
    "ab_framework_vh": [0.361, 0.420, 0.541],      # #5C6B8A
    "ab_framework_vl": [0.604, 0.647, 0.722],      # #9AA5B8
    "ab_cdr_h1": [0.306, 0.659, 0.871],            # #4EA8DE
    "ab_cdr_h2": [0.322, 0.718, 0.533],            # #52B788
    "ab_cdr_h3": [0.902, 0.224, 0.275],            # #E63946
    "ab_cdr_l1": [0.957, 0.635, 0.380],            # #F4A261
    "ab_cdr_l2": [0.914, 0.769, 0.416],            # #E9C46A
    "ab_cdr_l3": [0.616, 0.306, 0.867],            # #9D4EDD
    "ab_antigen_surf": [0.925, 0.933, 0.937],      # #ECEEEF

    # 8. Hydrophobic Surface & Physicochemical Complementarity Palette
    "hydro_polar": [0.863, 0.910, 0.949],          # #DCE8F2
    "hydro_neutral": [0.961, 0.953, 0.933],        # #F5F3EE
    "hydro_moderate": [0.949, 0.773, 0.486],       # #F2C57C
    "hydro_core": [0.851, 0.420, 0.263],           # #D96B43
    "hydro_binder_bg": [0.659, 0.737, 0.878],      # #A8BCE0

    # 9. Local Pocket Cavity & Pose Comparison Palette
    "pocket_surf_tint": [0.847, 0.886, 0.925],     # #D8E2EC
    "pocket_res_carbon": [0.553, 0.600, 0.682],    # #8D99AE
    "pose_ref_carbon": [0.298, 0.722, 0.675],      # #4CB8AC
    "pose_pred_carbon": [0.878, 0.337, 0.608],     # #E0569B

    # 10. Diffusion Trajectory / Conformational Ensemble Palette
    "ens_state_early": [0.847, 0.863, 0.902],      # #D8DCE6
    "ens_state_final": [0.282, 0.361, 0.659],      # #485CA8
}

IPD_PALETTE = PUBLICATION_PALETTES

STYLE_CHAIN_CYCLES: Dict[str, List[str]] = {
    "baker_rfd": [
        "ipd_pastel_peach",
        "ipd_pastel_rose",
        "ipd_pastel_lavender",
        "ipd_pastel_deepblue",
        "ipd_pastel_slate",
        "ipd_motif_teal",
    ],
    "goodsell": [
        "goodsell_coral",
        "goodsell_sage",
        "goodsell_sky",
        "goodsell_ochre",
        "goodsell_plum",
        "goodsell_sand",
    ],
    "cylindrical": [
        "arch_navy",
        "arch_coral",
        "arch_teal",
        "arch_gold",
        "arch_slate",
    ],
    "chimerax_soft": [
        "em_cobalt",
        "em_salmon",
        "em_mint",
        "em_ochre",
        "em_clay",
    ],
    "spotlight": [
        "spot_ghost_gray",
        "spot_cyan",
        "spot_crimson",
        "spot_amber",
    ],
    "alphafold_plddt": [
        "af_very_high",
        "af_confident",
        "af_low",
        "af_very_low",
    ],
    "antibody_cdr": [
        "ab_framework_vh",
        "ab_framework_vl",
        "ab_cdr_h1",
        "ab_cdr_h2",
        "ab_cdr_h3",
    ],
    "hydrophobic_surface": [
        "hydro_binder_bg",
        "hydro_core",
        "hydro_moderate",
        "hydro_polar",
    ],
    "pocket_cavity": [
        "pocket_res_carbon",
        "pose_ref_carbon",
        "pose_pred_carbon",
        "pocket_surf_tint",
    ],
    "diffusion_ensemble": [
        "ens_state_final",
        "ipd_pastel_lavender",
        "ipd_motif_teal",
        "ipd_pastel_rose",
    ],
}

OLIGOMER_CHAIN_CYCLE = STYLE_CHAIN_CYCLES["baker_rfd"]

STYLE_SPECTRUM_STOPS: Dict[str, str] = {
    "baker_rfd": "ipd_pastel_peach ipd_pastel_rose ipd_pastel_lavender ipd_pastel_deepblue",
    "baker_rfd2": "ipd_pastel_peach ipd_pastel_rose ipd_pastel_lavender ipd_pastel_iceblue",
    "goodsell": "goodsell_coral goodsell_ochre goodsell_sage goodsell_sky",
    "cylindrical": "arch_navy arch_teal arch_gold arch_coral",
    "chimerax_soft": "em_cobalt em_mint em_ochre em_salmon",
    "spotlight": "spot_ghost_gray",
    "antibody_cdr": "ab_framework_vl ab_framework_vh ab_cdr_h1 ab_cdr_h3",
    "hydrophobic_surface": "hydro_polar hydro_neutral hydro_moderate hydro_core",
    "pocket_cavity": "pocket_surf_tint pocket_res_carbon pose_ref_carbon",
    "diffusion_ensemble": "ens_state_early ipd_pastel_lavender ens_state_final",
}

STYLE_DEFAULTS: Dict[str, Dict[str, str]] = {
    "baker_rfd": {
        "target_color": "ipd_target_sand",
        "hotspot_color": "ipd_hotspot_orange",
        "binder_color": "ipd_pastel_lavender",
        "motif_color": "ipd_motif_teal",
        "connector_color": "ipd_slate_gray",
        "ligand_color": "ipd_ligand_carbon",
        "reference_color": "ipd_model_gray",
        "dash_color": "white",
    },
    "goodsell": {
        "target_color": "goodsell_sand",
        "hotspot_color": "goodsell_ochre",
        "binder_color": "goodsell_sky",
        "motif_color": "goodsell_coral",
        "connector_color": "goodsell_sage",
        "ligand_color": "goodsell_plum",
        "reference_color": "ipd_model_gray",
        "dash_color": "spot_dash_gray",
    },
    "cylindrical": {
        "target_color": "arch_slate",
        "hotspot_color": "arch_gold",
        "binder_color": "arch_navy",
        "motif_color": "arch_coral",
        "connector_color": "arch_slate",
        "ligand_color": "ipd_ligand_carbon",
        "reference_color": "ipd_model_gray",
        "dash_color": "arch_gold",
    },
    "chimerax_soft": {
        "target_color": "em_clay",
        "hotspot_color": "em_salmon",
        "binder_color": "em_cobalt",
        "motif_color": "em_mint",
        "connector_color": "em_clay",
        "ligand_color": "ipd_ligand_carbon",
        "reference_color": "ipd_model_gray",
        "dash_color": "em_ochre",
    },
    "spotlight": {
        "target_color": "spot_ghost_gray",
        "hotspot_color": "spot_amber",
        "binder_color": "spot_cyan",
        "motif_color": "spot_crimson",
        "connector_color": "spot_ghost_gray",
        "ligand_color": "spot_cyan",
        "reference_color": "ipd_model_gray",
        "dash_color": "spot_dash_gray",
    },
    "alphafold_plddt": {
        "target_color": "ipd_surface_gray",
        "hotspot_color": "af_very_low",
        "binder_color": "af_very_high",
        "motif_color": "af_confident",
        "connector_color": "ipd_slate_gray",
        "ligand_color": "ipd_ligand_carbon",
        "reference_color": "ipd_model_gray",
        "dash_color": "white",
    },
    "antibody_cdr": {
        "target_color": "ab_antigen_surf",
        "hotspot_color": "ab_cdr_h3",
        "binder_color": "ab_framework_vh",
        "motif_color": "ab_cdr_h3",
        "connector_color": "ab_framework_vl",
        "ligand_color": "ab_cdr_h1",
        "reference_color": "ipd_model_gray",
        "dash_color": "spot_dash_gray",
    },
    "hydrophobic_surface": {
        "target_color": "hydro_neutral",
        "hotspot_color": "hydro_core",
        "binder_color": "hydro_binder_bg",
        "motif_color": "hydro_core",
        "connector_color": "pocket_res_carbon",
        "ligand_color": "hydro_core",
        "reference_color": "ipd_model_gray",
        "dash_color": "spot_dash_gray",
    },
    "pocket_cavity": {
        "target_color": "pocket_surf_tint",
        "hotspot_color": "pose_pred_carbon",
        "binder_color": "pose_ref_carbon",
        "motif_color": "pose_ref_carbon",
        "connector_color": "pocket_res_carbon",
        "ligand_color": "pose_ref_carbon",
        "reference_color": "pose_pred_carbon",
        "dash_color": "spot_dash_gray",
    },
    "diffusion_ensemble": {
        "target_color": "ipd_surface_gray",
        "hotspot_color": "ens_state_final",
        "binder_color": "ens_state_final",
        "motif_color": "ipd_motif_teal",
        "connector_color": "ens_state_early",
        "ligand_color": "ipd_ligand_carbon",
        "reference_color": "ens_state_early",
        "dash_color": "white",
    },
}


def _rec(pml_lines: Optional[List[str]], line: str) -> None:
    if pml_lines is not None:
        pml_lines.append(line)


def _validate_style(style: str) -> str:
    if style not in VALID_STYLES:
        raise ValueError(f"Unknown style '{style}'. Valid styles: {', '.join(VALID_STYLES)}")
    return style


def register_palette(cmd, pml_lines: Optional[List[str]] = None) -> None:
    """Register all publication RGB colors in PyMOL."""
    _rec(pml_lines, "# --- Register Publication Color Palettes ---")
    for name, rgb in PUBLICATION_PALETTES.items():
        cmd.set_color(name, rgb)
        _rec(pml_lines, f"set_color {name}, [{rgb[0]:.3f}, {rgb[1]:.3f}, {rgb[2]:.3f}]")


register_ipd_palette = register_palette


def apply_theme(
    cmd,
    style: str = "baker_rfd",
    cylindrical_helices: Optional[bool] = None,
    transparent: bool = False,
    pml_lines: Optional[List[str]] = None,
) -> None:
    """Apply lighting, ray-tracing, and geometry parameters for a given publication style."""
    _validate_style(style)
    register_palette(cmd, pml_lines=pml_lines)

    opaque_bg = 0 if transparent else 1
    base_settings: List[Tuple[str, object]] = [
        ("ray_opaque_background", opaque_bg),
        ("orthoscopic", 1),
        ("depth_cue", 1),
        ("fog_start", 0.45),
        ("two_sided_lighting", 1),
        ("antialias", 2),
        ("cartoon_oval_length", 1.20),
        ("cartoon_oval_width", 0.25),
        ("cartoon_rect_length", 1.20),
        ("cartoon_rect_width", 0.28),
        ("cartoon_loop_radius", 0.18),
        ("cartoon_tube_radius", 0.45),
        ("cartoon_sampling", 14),
        ("cartoon_smooth_loops", 1),
        ("cartoon_fancy_helices", 0),
        ("cartoon_highlight_color", -1),
        ("stick_radius", 0.22),
        ("stick_ball", 1),
        ("stick_ball_ratio", 1.4),
        ("dash_gap", 0.35),
        ("dash_radius", 0.07),
        ("dash_round_ends", 1),
    ]

    if style == "goodsell":
        style_settings: List[Tuple[str, object]] = [
            ("ray_trace_mode", 3),
            ("ray_trace_gain", 0.12),
            ("ray_trace_color", "black"),
            ("ray_trace_disco_factor", 1.0),
            ("ray_trace_slope_factor", 0.6),
            ("ambient", 0.68),
            ("direct", 0.35),
            ("reflect", 0.15),
            ("spec_reflect", 0.0),
            ("spec_power", 200),
            ("light_count", 2),
            ("ray_shadow", 0),
            ("ambient_occlusion_mode", 1),
            ("ambient_occlusion_scale", 20.0),
            ("ambient_occlusion_smooth", 10),
            ("sphere_quality", 2),
            ("cartoon_cylindrical_helices", 1 if cylindrical_helices else 0),
        ]
    elif style == "cylindrical":
        cyl = True if cylindrical_helices is None else cylindrical_helices
        style_settings = [
            ("ray_trace_mode", 1),
            ("ray_trace_gain", 0.06),
            ("ray_trace_color", "black"),
            ("ambient", 0.48),
            ("direct", 0.45),
            ("reflect", 0.25),
            ("spec_reflect", 0.0),
            ("light_count", 4),
            ("ray_shadow", 0),
            ("ambient_occlusion_mode", 1),
            ("ambient_occlusion_scale", 12.0),
            ("ambient_occlusion_smooth", 8),
            ("cartoon_cylindrical_helices", 1 if cyl else 0),
            ("cartoon_helix_radius", 1.95),
            ("cartoon_flat_sheets", 1),
            ("cartoon_loop_radius", 0.16),
        ]
    elif style == "chimerax_soft":
        style_settings = [
            ("ray_trace_mode", 0),
            ("ambient", 0.42),
            ("direct", 0.48),
            ("reflect", 0.20),
            ("spec_reflect", 0.05),
            ("spec_power", 80),
            ("light_count", 4),
            ("ray_shadow", 1),
            ("ambient_occlusion_mode", 1),
            ("ambient_occlusion_scale", 25.0),
            ("ambient_occlusion_smooth", 15),
            ("surface_quality", 1),
            ("cartoon_cylindrical_helices", 1 if cylindrical_helices else 0),
        ]
    elif style == "spotlight":
        style_settings = [
            ("ray_trace_mode", 1),
            ("ray_trace_gain", 0.07),
            ("ray_trace_color", "black"),
            ("ambient", 0.50),
            ("direct", 0.45),
            ("reflect", 0.22),
            ("spec_reflect", 0.0),
            ("light_count", 4),
            ("ray_shadow", 0),
            ("ambient_occlusion_mode", 1),
            ("ambient_occlusion_scale", 15.0),
            ("ambient_occlusion_smooth", 10),
            ("stick_radius", 0.25),
            ("cartoon_cylindrical_helices", 1 if cylindrical_helices else 0),
        ]
    elif style == "alphafold_plddt":
        style_settings = [
            ("ray_trace_mode", 1),
            ("ray_trace_gain", 0.08),
            ("ray_trace_color", "black"),
            ("ambient", 0.50),
            ("direct", 0.45),
            ("reflect", 0.25),
            ("spec_reflect", 0.0),
            ("light_count", 4),
            ("ray_shadow", 0),
            ("ambient_occlusion_mode", 1),
            ("ambient_occlusion_scale", 12.0),
            ("ambient_occlusion_smooth", 8),
            ("cartoon_cylindrical_helices", 1 if cylindrical_helices else 0),
        ]
    elif style == "antibody_cdr":
        style_settings = [
            ("ray_trace_mode", 1),
            ("ray_trace_gain", 0.09),
            ("ray_trace_color", "black"),
            ("ambient", 0.50),
            ("direct", 0.45),
            ("reflect", 0.25),
            ("spec_reflect", 0.0),
            ("light_count", 4),
            ("ray_shadow", 0),
            ("ambient_occlusion_mode", 1),
            ("ambient_occlusion_scale", 15.0),
            ("ambient_occlusion_smooth", 10),
            ("surface_quality", 1),
            ("cartoon_cylindrical_helices", 1 if cylindrical_helices else 0),
        ]
    elif style == "hydrophobic_surface":
        style_settings = [
            ("ray_trace_mode", 1),
            ("ray_trace_gain", 0.06),
            ("ray_trace_color", "black"),
            ("ambient", 0.45),
            ("direct", 0.48),
            ("reflect", 0.22),
            ("spec_reflect", 0.05),
            ("light_count", 4),
            ("ray_shadow", 0),
            ("ambient_occlusion_mode", 1),
            ("ambient_occlusion_scale", 20.0),
            ("ambient_occlusion_smooth", 12),
            ("surface_quality", 1),
            ("cartoon_cylindrical_helices", 1 if cylindrical_helices else 0),
        ]
    elif style == "pocket_cavity":
        style_settings = [
            ("ray_trace_mode", 1),
            ("ray_trace_gain", 0.08),
            ("ray_trace_color", "black"),
            ("ambient", 0.52),
            ("direct", 0.44),
            ("reflect", 0.24),
            ("spec_reflect", 0.0),
            ("light_count", 4),
            ("ray_shadow", 0),
            ("ambient_occlusion_mode", 1),
            ("ambient_occlusion_scale", 15.0),
            ("ambient_occlusion_smooth", 10),
            ("surface_quality", 1),
            ("cartoon_cylindrical_helices", 1 if cylindrical_helices else 0),
        ]
    else:  # baker_rfd & diffusion_ensemble
        style_settings = [
            ("ray_trace_mode", 1),
            ("ray_trace_gain", 0.10 if style == "baker_rfd" else 0.08),
            ("ray_trace_color", "black"),
            ("ray_trace_disco_factor", 1.0),
            ("ray_trace_slope_factor", 0.6),
            ("ambient", 0.50),
            ("direct", 0.45),
            ("reflect", 0.25),
            ("spec_reflect", 0.0),
            ("spec_power", 200),
            ("light_count", 4),
            ("ray_shadow", 0),
            ("ambient_occlusion_mode", 1),
            ("ambient_occlusion_scale", 15.0 if style == "baker_rfd" else 12.0),
            ("ambient_occlusion_smooth", 10),
            ("cartoon_cylindrical_helices", 1 if cylindrical_helices else 0),
        ]

    _rec(pml_lines, f"\n# --- Apply Publication Theme Settings ({style}) ---")
    cmd.bg_color("white")
    _rec(pml_lines, "bg_color white")
    for key, val in base_settings + style_settings:
        cmd.set(key, val)
        _rec(pml_lines, f"set {key}, {val}")


def apply_ipd_theme(
    cmd,
    cylindrical_helices: bool = False,
    ray_outline: bool = True,
    ambient_occlusion: bool = True,
    transparent: bool = False,
    pml_lines: Optional[List[str]] = None,
) -> None:
    """Backwards-compatible wrapper for applying the baker_rfd IPD theme."""
    apply_theme(
        cmd,
        style="baker_rfd",
        cylindrical_helices=cylindrical_helices,
        transparent=transparent,
        pml_lines=pml_lines,
    )
    if not ray_outline:
        cmd.set("ray_trace_mode", 0)
        _rec(pml_lines, "set ray_trace_mode, 0")
    if not ambient_occlusion:
        cmd.set("ambient_occlusion_mode", 0)
        _rec(pml_lines, "set ambient_occlusion_mode, 0")


def verify_and_load(
    cmd,
    path: str,
    obj_name: str,
    pml_lines: Optional[List[str]] = None,
) -> int:
    """Verify a local structure file exists, load it, and confirm atom count > 0."""
    abs_path = os.path.abspath(path)
    if not os.path.isfile(abs_path):
        raise FileNotFoundError(f"Structure file not found: {abs_path}")

    cmd.load(abs_path, obj_name)
    _rec(pml_lines, f"load {abs_path}, {obj_name}")

    n_atoms = cmd.count_atoms(obj_name)
    if n_atoms == 0:
        raise RuntimeError(f"Loaded 0 atoms from {abs_path} into object '{obj_name}'.")

    cmd.remove(f"{obj_name} and solvent")
    _rec(pml_lines, f"remove {obj_name} and solvent")
    return n_atoms


def ensure_cartoon_trace(
    cmd,
    obj_name: str,
    pml_lines: Optional[List[str]] = None,
) -> bool:
    """Auto-detect C-alpha-only structures and enable cartoon_trace if needed."""
    prot_atoms = cmd.count_atoms(f"({obj_name}) and polymer.protein")
    ca_atoms = cmd.count_atoms(f"({obj_name}) and polymer.protein and name CA")
    if prot_atoms > 0 and prot_atoms == ca_atoms:
        cmd.set("cartoon_trace", 1, obj_name)
        _rec(pml_lines, f"set cartoon_trace, 1, {obj_name}")
        return True
    return False


def align_structures(
    cmd,
    mobile: str,
    target: str,
    pml_lines: Optional[List[str]] = None,
) -> Tuple[str, float, int]:
    """Superimpose mobile onto target using align with automatic cealign fallback."""
    try:
        res = cmd.align(f"({mobile}) and polymer.protein", f"({target}) and polymer.protein")
        rmsd, n_aligned = float(res[0]), int(res[1])
        if n_aligned < 20:
            raise ValueError(f"Too few aligned atoms ({n_aligned}); falling back to cealign.")
        _rec(pml_lines, f"align ({mobile}) and polymer.protein, ({target}) and polymer.protein")
        return ("align", rmsd, n_aligned)
    except Exception:
        res = cmd.cealign(f"({target}) and polymer.protein", f"({mobile}) and polymer.protein")
        rmsd = float(res["RMSD"])
        n_aligned = int(res["alignment_length"])
        _rec(pml_lines, f"cealign ({target}) and polymer.protein, ({mobile}) and polymer.protein")
        return ("cealign", rmsd, n_aligned)


def color_alphafold_plddt(
    cmd,
    selection: str = "polymer.protein",
    pml_lines: Optional[List[str]] = None,
) -> None:
    """Apply canonical AlphaFold pLDDT threshold colors, normalizing 0..1 B-factors if needed."""
    sel = f"({selection}) and polymer.protein"
    model = cmd.get_model(f"{sel} and name CA")
    b_vals = [a.b for a in model.atom] if model.atom else []
    max_b = max(b_vals) if b_vals else 0.0
    if 0.0 < max_b <= 1.0:
        cmd.alter(selection, "b=b*100.0")
        _rec(pml_lines, f"alter {selection}, b=b*100.0")

    cmd.color("af_very_low", sel)
    cmd.color("af_low", f"({sel}) and b > 50")
    cmd.color("af_confident", f"({sel}) and b > 70")
    cmd.color("af_very_high", f"({sel}) and b > 90")
    _rec(
        pml_lines,
        f"color af_very_low, {sel}\n"
        f"color af_low, ({sel}) and b > 50\n"
        f"color af_confident, ({sel}) and b > 70\n"
        f"color af_very_high, ({sel}) and b > 90",
    )


def color_hydrophobic_eisenberg(
    cmd,
    selection: str,
    pml_lines: Optional[List[str]] = None,
) -> None:
    """Color protein residues by 4-tier Eisenberg hydrophobicity scale."""
    sel = f"({selection}) and polymer.protein"
    polar = "resn ARG+LYS+ASP+GLU+ASN+GLN+SER+THR+HIS"
    neutral = "resn GLY+ALA+PRO+CYS"
    moderate = "resn TYR+MET+VAL"
    core = "resn ILE+LEU+PHE+TRP"

    cmd.color("hydro_neutral", sel)
    cmd.color("hydro_polar", f"({sel}) and ({polar})")
    cmd.color("hydro_moderate", f"({sel}) and ({moderate})")
    cmd.color("hydro_core", f"({sel}) and ({core})")
    cmd.set("surface_color", "hydro_neutral", sel)
    cmd.set("surface_color", "hydro_polar", f"({sel}) and ({polar})")
    cmd.set("surface_color", "hydro_moderate", f"({sel}) and ({moderate})")
    cmd.set("surface_color", "hydro_core", f"({sel}) and ({core})")
    _rec(
        pml_lines,
        f"color hydro_neutral, {sel}\n"
        f"color hydro_polar, ({sel}) and ({polar})\n"
        f"color hydro_moderate, ({sel}) and ({moderate})\n"
        f"color hydro_core, ({sel}) and ({core})\n"
        f"set surface_color, hydro_neutral, {sel}\n"
        f"set surface_color, hydro_polar, ({sel}) and ({polar})\n"
        f"set surface_color, hydro_moderate, ({sel}) and ({moderate})\n"
        f"set surface_color, hydro_core, ({sel}) and ({core})",
    )


def color_style_spectrum(
    cmd,
    selection: str = "polymer.protein",
    style: str = "baker_rfd",
    palette_mode: str = "rfd1",
    pml_lines: Optional[List[str]] = None,
) -> None:
    """Apply a style-appropriate gradient or confidence coloring to a protein selection."""
    if style == "alphafold_plddt":
        color_alphafold_plddt(cmd, selection=selection, pml_lines=pml_lines)
        return
    if style == "hydrophobic_surface":
        color_hydrophobic_eisenberg(cmd, selection=selection, pml_lines=pml_lines)
        return
    if style == "spotlight":
        cmd.color("spot_ghost_gray", f"({selection}) and polymer.protein")
        _rec(pml_lines, f"color spot_ghost_gray, ({selection}) and polymer.protein")
        return

    if style == "baker_rfd" and palette_mode == "rfd2":
        stops = STYLE_SPECTRUM_STOPS["baker_rfd2"]
    else:
        stops = STYLE_SPECTRUM_STOPS.get(style, STYLE_SPECTRUM_STOPS["baker_rfd"])
    cmd.spectrum("count", stops, f"({selection}) and polymer.protein")
    _rec(pml_lines, f"spectrum count, {stops}, ({selection}) and polymer.protein")


def color_ipd_spectrum(
    cmd,
    selection: str = "polymer.protein",
    palette_mode: str = "rfd1",
    pml_lines: Optional[List[str]] = None,
) -> None:
    color_style_spectrum(cmd, selection=selection, style="baker_rfd", palette_mode=palette_mode, pml_lines=pml_lines)


def _apply_goodsell_spheres(
    cmd,
    selection: str,
    base_color: Optional[str] = None,
    transparency: float = 0.0,
    pml_lines: Optional[List[str]] = None,
) -> None:
    """Display full-atom space-filling spheres with subtle Goodsell O/N heteroatom tints."""
    sel = f"({selection}) and not solvent and not hydro"
    cmd.show("spheres", sel)
    cmd.set("sphere_scale", 1.0, sel)
    _rec(pml_lines, f"show spheres, {sel}\nset sphere_scale, 1.0, {sel}")
    if transparency > 0.0:
        cmd.set("sphere_transparency", transparency, sel)
        _rec(pml_lines, f"set sphere_transparency, {transparency}, {sel}")
    if base_color:
        cmd.color(base_color, sel)
        _rec(pml_lines, f"color {base_color}, {sel}")
    cmd.color("goodsell_oxygen", f"({sel}) and elem O")
    cmd.color("goodsell_nitrogen", f"({sel}) and elem N")
    _rec(pml_lines, f"color goodsell_oxygen, ({sel}) and elem O\ncolor goodsell_nitrogen, ({sel}) and elem N")


def _get_font(size: int = 24):
    from PIL import ImageFont

    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def _apply_diffusion_ensemble(
    cmd,
    obj_name: str,
    pml_lines: Optional[List[str]] = None,
) -> None:
    """Apply multi-state ghost ensemble or single-state putty flexibility styling."""
    n_states = cmd.count_states(obj_name)
    if n_states > 1:
        cmd.dss(obj_name, state=n_states)
        cmd.create(f"{obj_name}_final", obj_name, n_states, 1)
        cmd.dss(f"{obj_name}_final")
        cmd.set("all_states", 1, obj_name)
        cmd.show("cartoon", f"({obj_name} or {obj_name}_final) and polymer.protein")
        cmd.color("ens_state_early", obj_name)
        cmd.set("cartoon_transparency", 0.78, obj_name)
        cmd.color("ens_state_final", f"{obj_name}_final")
        cmd.set("cartoon_transparency", 0.0, f"{obj_name}_final")
        _rec(
            pml_lines,
            f"dss {obj_name}, state={n_states}\n"
            f"create {obj_name}_final, {obj_name}, {n_states}, 1\n"
            f"set all_states, 1, {obj_name}\n"
            f"show cartoon, ({obj_name} or {obj_name}_final) and polymer.protein\n"
            f"color ens_state_early, {obj_name}\n"
            f"set cartoon_transparency, 0.78, {obj_name}\n"
            f"color ens_state_final, {obj_name}_final\n"
            f"set cartoon_transparency, 0.0, {obj_name}_final",
        )
    else:
        cmd.show("cartoon", f"{obj_name} and polymer.protein")
        cmd.cartoon("putty", f"{obj_name} and polymer.protein")
        cmd.set("cartoon_putty_scale_min", 0.35)
        cmd.set("cartoon_putty_scale_max", 1.8)
        cmd.set("cartoon_putty_transform", 0)
        model = cmd.get_model(f"{obj_name} and polymer.protein and name CA")
        b_vals = [a.b for a in model.atom] if model.atom else []
        if b_vals and (max(b_vals) - min(b_vals)) > 1e-3:
            cmd.spectrum("b", STYLE_SPECTRUM_STOPS["diffusion_ensemble"], f"{obj_name} and polymer.protein")
            _rec(
                pml_lines,
                f"show cartoon, {obj_name} and polymer.protein\n"
                f"cartoon putty, {obj_name} and polymer.protein\n"
                f"spectrum b, {STYLE_SPECTRUM_STOPS['diffusion_ensemble']}, {obj_name} and polymer.protein",
            )
        else:
            color_style_spectrum(cmd, obj_name, style="diffusion_ensemble", pml_lines=pml_lines)


def auto_crop_png(png_path: str, padding: int = 24, transparent: bool = False) -> None:
    """Trim surrounding empty alpha or solid white border with fixed pixel padding."""
    from PIL import Image, ImageChops

    im = Image.open(png_path)
    if transparent or im.mode == "RGBA":
        rgba = im.convert("RGBA")
        alpha = rgba.split()[-1]
        bbox = alpha.point(lambda p: 255 if p > 5 else 0).getbbox()
        if not bbox and not transparent:
            rgb = rgba.convert("RGB")
            bg = Image.new("RGB", rgb.size, (255, 255, 255))
            bbox = ImageChops.difference(rgb, bg).getbbox()
        target = rgba if transparent else rgba.convert("RGB")
    else:
        rgb = im.convert("RGB")
        bg = Image.new("RGB", rgb.size, (255, 255, 255))
        bbox = ImageChops.difference(rgb, bg).getbbox()
        target = rgb

    if not bbox:
        return

    w, h = target.size
    left = max(0, bbox[0] - padding)
    top = max(0, bbox[1] - padding)
    right = min(w, bbox[2] + padding)
    bottom = min(h, bbox[3] + padding)
    cropped = target.crop((left, top, right, bottom))
    cropped.save(png_path)


def _stitch_inset_composite(
    global_png: str,
    inset_png: str,
    out_composite_png: str,
    transparent: bool = False,
) -> str:
    """Stitch global overview (left) and framed inset zoom (right) side-by-side."""
    from PIL import Image, ImageDraw, ImageOps

    im_g = Image.open(global_png).convert("RGBA" if transparent else "RGB")
    im_i = Image.open(inset_png).convert("RGBA" if transparent else "RGB")

    target_h = max(im_g.height, im_i.height)
    if im_g.height != target_h:
        new_w = max(1, int(round(im_g.width * target_h / im_g.height)))
        im_g = im_g.resize((new_w, target_h), Image.Resampling.LANCZOS)
    if im_i.height != target_h:
        new_w = max(1, int(round(im_i.width * target_h / im_i.height)))
        im_i = im_i.resize((new_w, target_h), Image.Resampling.LANCZOS)

    border = 6
    im_i_framed = ImageOps.expand(im_i, border=border, fill=(72, 72, 76, 255) if transparent else (72, 72, 76))
    gap = 36
    canvas_w = im_g.width + gap + im_i_framed.width
    canvas_h = max(im_g.height, im_i_framed.height)
    bg_col = (255, 255, 255, 0) if transparent else (255, 255, 255)
    canvas = Image.new("RGBA" if transparent else "RGB", (canvas_w, canvas_h), bg_col)

    y_g = (canvas_h - im_g.height) // 2
    y_i = (canvas_h - im_i_framed.height) // 2
    canvas.paste(im_g, (0, y_g), im_g if transparent else None)
    canvas.paste(im_i_framed, (im_g.width + gap, y_i), im_i_framed if transparent else None)

    draw = ImageDraw.Draw(canvas)
    ax1 = im_g.width + 6
    ax2 = im_g.width + gap - 8
    ay = canvas_h // 2
    line_col = (72, 72, 76, 255) if transparent else (72, 72, 76)
    draw.line([(ax1, ay), (ax2, ay)], fill=line_col, width=4)
    draw.polygon([(ax2 + 4, ay), (ax2 - 10, ay - 8), (ax2 - 10, ay + 8)], fill=line_col)

    canvas.save(out_composite_png)
    return out_composite_png


def render_outputs(
    cmd,
    out_prefix: str,
    width: int = 2000,
    height: int = 1600,
    dpi: int = 300,
    use_ray: bool = True,
    transparent: bool = False,
    auto_crop: bool = False,
    crop_padding: int = 24,
    pml_lines: Optional[List[str]] = None,
) -> Tuple[str, str, str]:
    """Render PNG, optionally auto-crop, save .pse session, and write companion .pml script."""
    out_dir = os.path.dirname(os.path.abspath(out_prefix))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    png_path = f"{out_prefix}.png"
    pse_path = f"{out_prefix}.pse"
    pml_path = f"{out_prefix}.pml"

    if use_ray:
        cmd.ray(width, height)
        _rec(pml_lines, f"ray {width}, {height}")
    cmd.png(png_path, width=width, height=height, dpi=dpi, ray=1 if use_ray else 0)
    _rec(pml_lines, f"png {png_path}, width={width}, height={height}, dpi={dpi}, ray={1 if use_ray else 0}")

    if auto_crop:
        auto_crop_png(png_path, padding=crop_padding, transparent=transparent)

    cmd.save(pse_path)
    _rec(pml_lines, f"save {pse_path}")

    if pml_lines is not None:
        with open(pml_path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(pml_lines) + "\n")

    return (png_path, pse_path, pml_path)


def render_monomer(
    cmd,
    structure: str,
    out_prefix: str,
    style: str = "baker_rfd",
    reference: Optional[str] = None,
    motif_sele: Optional[str] = None,
    color_mode: str = "spectrum",
    design_role: str = "gray",
    palette_mode: str = "rfd1",
    cylindrical_helices: Optional[bool] = None,
    width: int = 2000,
    height: int = 1600,
    dpi: int = 300,
    use_ray: bool = True,
    transparent: bool = False,
    auto_crop: bool = False,
    crop_padding: int = 24,
) -> Tuple[str, str, str]:
    """Render a monomer, motif-scaffolded design, or design-vs-validation overlay."""
    _validate_style(style)
    defaults = STYLE_DEFAULTS[style]
    cycle = STYLE_CHAIN_CYCLES[style]
    pml: List[str] = [f"# Publication Style ({style}): Monomer & Overlay"]
    apply_theme(cmd, style=style, cylindrical_helices=cylindrical_helices, transparent=transparent, pml_lines=pml)

    verify_and_load(cmd, structure, "design", pml_lines=pml)
    ensure_cartoon_trace(cmd, "design", pml_lines=pml)

    cmd.hide("everything", "all")
    _rec(pml, "hide everything, all")

    if style == "goodsell":
        chains = cmd.get_chains("design")
        if color_mode == "solid":
            _apply_goodsell_spheres(cmd, "design", base_color=cycle[0], pml_lines=pml)
        else:
            for idx, ch in enumerate(chains):
                _apply_goodsell_spheres(
                    cmd, f"design and chain {ch}", base_color=cycle[idx % len(cycle)], pml_lines=pml
                )
    elif style == "diffusion_ensemble" and not reference:
        _apply_diffusion_ensemble(cmd, "design", pml_lines=pml)
    else:
        cmd.show("cartoon", "polymer.protein")
        _rec(pml, "show cartoon, polymer.protein")

        if style == "spotlight":
            cmd.color("spot_ghost_gray", "design and polymer.protein")
            if motif_sele:
                cmd.set("cartoon_transparency", 0.62, "design and polymer.protein")
                _rec(pml, "color spot_ghost_gray, design and polymer.protein\nset cartoon_transparency, 0.62, design and polymer.protein")
            else:
                _rec(pml, "color spot_ghost_gray, design and polymer.protein")
        elif reference:
            verify_and_load(cmd, reference, "reference", pml_lines=pml)
            ensure_cartoon_trace(cmd, "reference", pml_lines=pml)
            cmd.show("cartoon", "reference and polymer.protein")
            method, rmsd, n_aligned = align_structures(cmd, "reference", "design", pml_lines=pml)
            print(f"Alignment ({method}): RMSD = {rmsd:.3f} A over {n_aligned} atoms")

            if design_role == "gray":
                cmd.color(defaults["reference_color"], "design")
                _rec(pml, f"color {defaults['reference_color']}, design")
                color_style_spectrum(cmd, "reference", style=style, palette_mode=palette_mode, pml_lines=pml)
            else:
                cmd.color(defaults["reference_color"], "reference")
                _rec(pml, f"color {defaults['reference_color']}, reference")
                color_style_spectrum(cmd, "design", style=style, palette_mode=palette_mode, pml_lines=pml)
        else:
            if color_mode == "solid":
                cmd.color(defaults["binder_color"], "design and polymer.protein")
                _rec(pml, f"color {defaults['binder_color']}, design and polymer.protein")
            elif color_mode == "chain":
                for idx, ch in enumerate(cmd.get_chains("design")):
                    col = cycle[idx % len(cycle)]
                    cmd.color(col, f"design and chain {ch}")
                    _rec(pml, f"color {col}, design and chain {ch}")
            else:
                color_style_spectrum(cmd, "design", style=style, palette_mode=palette_mode, pml_lines=pml)

    if motif_sele:
        cmd.select("motif_region", f"design and ({motif_sele})")
        if style == "goodsell":
            _apply_goodsell_spheres(cmd, "motif_region", base_color=defaults["motif_color"], pml_lines=pml)
        else:
            cmd.color(defaults["motif_color"], "motif_region")
            cmd.set("cartoon_transparency", 0.0, "motif_region")
            cmd.show("sticks", "motif_region and not name C+O+N")
            cmd.hide("sticks", "motif_region and hydro")
            cmd.util.cnc("motif_region")
            _rec(
                pml,
                f"select motif_region, design and ({motif_sele})\n"
                f"color {defaults['motif_color']}, motif_region\n"
                "set cartoon_transparency, 0.0, motif_region\n"
                "show sticks, motif_region and not name C+O+N\n"
                "hide sticks, motif_region and hydro\n"
                "util.cnc motif_region",
            )

    cmd.orient("all")
    cmd.zoom("all", buffer=3.0)
    _rec(pml, "orient all\nzoom all, buffer=3.0")
    return render_outputs(
        cmd,
        out_prefix,
        width=width,
        height=height,
        dpi=dpi,
        use_ray=use_ray,
        transparent=transparent,
        auto_crop=auto_crop,
        crop_padding=crop_padding,
        pml_lines=pml,
    )


def render_binder(
    cmd,
    complex_path: str,
    target_chain: str,
    binder_chain: str,
    out_prefix: str,
    style: str = "baker_rfd",
    reference_binder: Optional[str] = None,
    hotspots: Optional[str] = None,
    target_repr: str = "surface",
    target_color: Optional[str] = None,
    binder_color: Optional[str] = None,
    show_interface_sticks: bool = False,
    zoom_interface: bool = False,
    with_inset: bool = False,
    cylindrical_helices: Optional[bool] = None,
    width: int = 2000,
    height: int = 1600,
    dpi: int = 300,
    use_ray: bool = True,
    transparent: bool = False,
    auto_crop: bool = False,
    crop_padding: int = 24,
) -> Tuple[str, ...]:
    """Render a target-binder complex in the selected publication style."""
    _validate_style(style)
    defaults = STYLE_DEFAULTS[style]
    t_color = target_color or defaults["target_color"]
    b_color = binder_color or defaults["binder_color"]

    pml: List[str] = [f"# Publication Style ({style}): Target-Binder Complex"]
    apply_theme(cmd, style=style, cylindrical_helices=cylindrical_helices, transparent=transparent, pml_lines=pml)

    verify_and_load(cmd, complex_path, "complex", pml_lines=pml)
    ensure_cartoon_trace(cmd, "complex", pml_lines=pml)

    cmd.hide("everything", "all")
    _rec(pml, "hide everything, all")

    target_sel = f"complex and chain {target_chain} and polymer.protein"
    binder_sel = f"complex and chain {binder_chain} and polymer.protein"

    if cmd.count_atoms(target_sel) == 0:
        raise ValueError(f"Target selection '{target_sel}' matched 0 atoms.")
    if cmd.count_atoms(binder_sel) == 0:
        raise ValueError(f"Binder selection '{binder_sel}' matched 0 atoms.")

    if style == "goodsell":
        _apply_goodsell_spheres(cmd, target_sel, base_color=t_color, pml_lines=pml)
        if hotspots:
            hs_sel = f"({target_sel}) and ({hotspots})"
            _apply_goodsell_spheres(cmd, hs_sel, base_color=defaults["hotspot_color"], pml_lines=pml)
        _apply_goodsell_spheres(cmd, binder_sel, base_color=b_color, pml_lines=pml)
    elif style == "hydrophobic_surface":
        cmd.show("surface", target_sel)
        color_hydrophobic_eisenberg(cmd, target_sel, pml_lines=pml)
        cmd.show("cartoon", binder_sel)
        cmd.color(b_color, binder_sel)
        cmd.set("cartoon_transparency", 0.30, binder_sel)
        hydro_anchors = f"byres (({binder_sel}) and resn ILE+VAL+LEU+PHE+TRP+TYR+MET within 4.5 of ({target_sel}))"
        cmd.select("binder_anchors", hydro_anchors)
        if cmd.count_atoms("binder_anchors") > 0:
            cmd.show("sticks", "binder_anchors and not name C+O+N")
            cmd.hide("sticks", "binder_anchors and hydro")
            cmd.color("hydro_core", "binder_anchors")
            cmd.util.cnc("binder_anchors")
        _rec(
            pml,
            f"show surface, {target_sel}\nshow cartoon, {binder_sel}\ncolor {b_color}, {binder_sel}\n"
            f"set cartoon_transparency, 0.30, {binder_sel}\n"
            f"select binder_anchors, {hydro_anchors}\n"
            "show sticks, binder_anchors and not name C+O+N\ncolor hydro_core, binder_anchors\nutil.cnc binder_anchors",
        )
    else:
        if target_repr in ("surface", "both"):
            cmd.show("surface", target_sel)
            cmd.set("surface_color", t_color, target_sel)
            _rec(pml, f"show surface, {target_sel}\nset surface_color, {t_color}, {target_sel}")
            if target_repr == "both":
                cmd.set("transparency", 0.35, target_sel)
                cmd.show("cartoon", target_sel)
                cmd.color(t_color, target_sel)
                _rec(
                    pml,
                    f"set transparency, 0.35, {target_sel}\n"
                    f"show cartoon, {target_sel}\ncolor {t_color}, {target_sel}",
                )
        else:
            cmd.show("cartoon", target_sel)
            cmd.color(t_color, target_sel)
            _rec(pml, f"show cartoon, {target_sel}\ncolor {t_color}, {target_sel}")

        if hotspots:
            hs_sel = f"({target_sel}) and ({hotspots})"
            cmd.color(defaults["hotspot_color"], hs_sel)
            cmd.set("surface_color", defaults["hotspot_color"], hs_sel)
            _rec(
                pml,
                f"color {defaults['hotspot_color']}, {hs_sel}\n"
                f"set surface_color, {defaults['hotspot_color']}, {hs_sel}",
            )

        cmd.show("cartoon", binder_sel)
        _rec(pml, f"show cartoon, {binder_sel}")
        if style == "alphafold_plddt":
            color_alphafold_plddt(cmd, binder_sel, pml_lines=pml)
        elif b_color == "spectrum":
            color_style_spectrum(cmd, binder_sel, style=style, pml_lines=pml)
        else:
            cmd.color(b_color, binder_sel)
            _rec(pml, f"color {b_color}, {binder_sel}")

        if style == "spotlight":
            cmd.set("cartoon_transparency", 0.62, target_sel)
            cmd.set("transparency", 0.35, target_sel)
            _rec(pml, f"set cartoon_transparency, 0.62, {target_sel}\nset transparency, 0.35, {target_sel}")

    if reference_binder:
        verify_and_load(cmd, reference_binder, "ref_binder", pml_lines=pml)
        ensure_cartoon_trace(cmd, "ref_binder", pml_lines=pml)
        cmd.show("cartoon", "ref_binder and polymer.protein")
        method, rmsd, n_aligned = align_structures(cmd, "ref_binder", binder_sel, pml_lines=pml)
        print(f"Binder Alignment ({method}): RMSD = {rmsd:.3f} A over {n_aligned} atoms")
        cmd.color(defaults["reference_color"], "ref_binder")
        _rec(pml, f"show cartoon, ref_binder and polymer.protein\ncolor {defaults['reference_color']}, ref_binder")

    if (show_interface_sticks or zoom_interface or with_inset) and style != "goodsell":
        cmd.select("iface_binder", f"byres (({binder_sel}) within 4.0 of ({target_sel}))")
        cmd.select("iface_target", f"byres (({target_sel}) within 4.0 of ({binder_sel}))")
        cmd.show("sticks", "(iface_binder or iface_target) and not name C+O+N")
        cmd.hide("sticks", "(iface_binder or iface_target) and hydro")
        cmd.util.cnc("iface_binder or iface_target")
        cmd.distance("iface_hbonds", "iface_binder", "iface_target", cutoff=3.5, mode=2)
        cmd.set("dash_color", defaults["dash_color"])
        cmd.hide("labels", "iface_hbonds")
        _rec(
            pml,
            f"select iface_binder, byres (({binder_sel}) within 4.0 of ({target_sel}))\n"
            f"select iface_target, byres (({target_sel}) within 4.0 of ({binder_sel}))\n"
            "show sticks, (iface_binder or iface_target) and not name C+O+N\n"
            "hide sticks, (iface_binder or iface_target) and hydro\n"
            "util.cnc iface_binder or iface_target\n"
            "distance iface_hbonds, iface_binder, iface_target, cutoff=3.5, mode=2\n"
            f"set dash_color, {defaults['dash_color']}\nhide labels, iface_hbonds",
        )

    if with_inset:
        cmd.orient("complex")
        cmd.zoom("complex", buffer=3.0)
        g_out = render_outputs(
            cmd,
            f"{out_prefix}_global",
            width=width,
            height=height,
            dpi=dpi,
            use_ray=use_ray,
            transparent=transparent,
            auto_crop=auto_crop,
            crop_padding=crop_padding,
            pml_lines=list(pml),
        )
        focus_sel = "iface_binder or iface_target" if cmd.count_atoms("iface_binder or iface_target") > 0 else binder_sel
        cmd.orient(focus_sel)
        cmd.zoom(focus_sel, buffer=4.0)
        _rec(pml, f"orient {focus_sel}\nzoom {focus_sel}, buffer=4.0")
        i_out = render_outputs(
            cmd,
            f"{out_prefix}_inset",
            width=width,
            height=height,
            dpi=dpi,
            use_ray=use_ray,
            transparent=transparent,
            auto_crop=auto_crop,
            crop_padding=crop_padding,
            pml_lines=pml,
        )
        comp = _stitch_inset_composite(g_out[0], i_out[0], f"{out_prefix}_composite.png", transparent=transparent)
        return (g_out[0], i_out[0], comp)

    if zoom_interface:
        cmd.orient("iface_binder or iface_target")
        cmd.zoom("iface_binder or iface_target", buffer=4.0)
        _rec(pml, "orient iface_binder or iface_target\nzoom iface_binder or iface_target, buffer=4.0")
    else:
        cmd.orient("complex")
        cmd.zoom("complex", buffer=3.0)
        _rec(pml, "orient complex\nzoom complex, buffer=3.0")

    return render_outputs(
        cmd,
        out_prefix,
        width=width,
        height=height,
        dpi=dpi,
        use_ray=use_ray,
        transparent=transparent,
        auto_crop=auto_crop,
        crop_padding=crop_padding,
        pml_lines=pml,
    )


def render_oligomer(
    cmd,
    structure: str,
    out_prefix: str,
    style: str = "baker_rfd",
    reference_asu: Optional[str] = None,
    motif_sele: Optional[str] = None,
    metal_sele: Optional[str] = None,
    em_map: Optional[str] = None,
    em_contour: float = 1.5,
    view: str = "single",
    cylindrical_helices: Optional[bool] = None,
    width: int = 2000,
    height: int = 2000,
    dpi: int = 300,
    use_ray: bool = True,
    transparent: bool = False,
    auto_crop: bool = False,
    crop_padding: int = 24,
) -> List[Tuple[str, str, str]]:
    """Render symmetric oligomers (Cn / Dn / cages) and optional cryo-EM density map."""
    _validate_style(style)
    defaults = STYLE_DEFAULTS[style]
    cycle = STYLE_CHAIN_CYCLES[style]

    pml: List[str] = [f"# Publication Style ({style}): Symmetric Oligomer"]
    apply_theme(cmd, style=style, cylindrical_helices=cylindrical_helices, transparent=transparent, pml_lines=pml)

    verify_and_load(cmd, structure, "oligomer", pml_lines=pml)
    ensure_cartoon_trace(cmd, "oligomer", pml_lines=pml)

    cmd.hide("everything", "all")
    _rec(pml, "hide everything, all")

    chains = cmd.get_chains("oligomer")
    print(f"Oligomer chains ({len(chains)}): {', '.join(chains)}")

    if style == "goodsell":
        for idx, ch in enumerate(chains):
            _apply_goodsell_spheres(
                cmd, f"oligomer and chain {ch}", base_color=cycle[idx % len(cycle)], pml_lines=pml
            )
    elif style == "alphafold_plddt":
        cmd.show("cartoon", "oligomer and polymer.protein")
        color_alphafold_plddt(cmd, "oligomer", pml_lines=pml)
    elif style == "diffusion_ensemble":
        _apply_diffusion_ensemble(cmd, "oligomer", pml_lines=pml)
    else:
        cmd.show("cartoon", "oligomer and polymer.protein")
        _rec(pml, "show cartoon, oligomer and polymer.protein")
        for idx, ch in enumerate(chains):
            col = cycle[idx % len(cycle)]
            cmd.color(col, f"oligomer and chain {ch}")
            _rec(pml, f"color {col}, oligomer and chain {ch}")

    if reference_asu and style != "goodsell":
        verify_and_load(cmd, reference_asu, "ref_asu", pml_lines=pml)
        ensure_cartoon_trace(cmd, "ref_asu", pml_lines=pml)
        first_chain = chains[0]
        method, rmsd, n_aligned = align_structures(
            cmd, "ref_asu", f"oligomer and chain {first_chain}", pml_lines=pml
        )
        print(f"ASU Alignment ({method}): RMSD = {rmsd:.3f} A over {n_aligned} atoms")
        cmd.show("cartoon", "ref_asu and polymer.protein")
        cmd.color(defaults["reference_color"], "ref_asu")
        _rec(pml, f"show cartoon, ref_asu and polymer.protein\ncolor {defaults['reference_color']}, ref_asu")

    if motif_sele:
        cmd.select("sym_motif", f"oligomer and ({motif_sele})")
        if style == "goodsell":
            _apply_goodsell_spheres(cmd, "sym_motif", base_color=defaults["motif_color"], pml_lines=pml)
        else:
            cmd.color(defaults["motif_color"], "sym_motif")
            cmd.show("sticks", "sym_motif and not name C+O+N")
            cmd.hide("sticks", "sym_motif and hydro")
            cmd.util.cnc("sym_motif")
            _rec(
                pml,
                f"select sym_motif, oligomer and ({motif_sele})\n"
                f"color {defaults['motif_color']}, sym_motif\n"
                "show sticks, sym_motif and not name C+O+N\n"
                "hide sticks, sym_motif and hydro\n"
                "util.cnc sym_motif",
            )

    if metal_sele and cmd.count_atoms(f"oligomer and ({metal_sele})") > 0:
        cmd.select("sym_metal", f"oligomer and ({metal_sele})")
        cmd.show("spheres", "sym_metal")
        cmd.color("ipd_metal_ochre", "sym_metal")
        cmd.set("sphere_scale", 0.65, "sym_metal")
        _rec(
            pml,
            f"select sym_metal, oligomer and ({metal_sele})\n"
            "show spheres, sym_metal\ncolor ipd_metal_ochre, sym_metal\nset sphere_scale, 0.65, sym_metal",
        )

    if em_map:
        abs_map = os.path.abspath(em_map)
        cmd.load(abs_map, "em_density")
        cmd.isosurface("em_surf", "em_density", em_contour)
        cmd.color("ipd_surface_gray", "em_surf")
        cmd.set("transparency", 0.72, "em_surf")
        _rec(
            pml,
            f"load {abs_map}, em_density\n"
            f"isosurface em_surf, em_density, {em_contour}\n"
            "color ipd_surface_gray, em_surf\nset transparency, 0.72, em_surf",
        )

    cmd.orient("oligomer")
    cmd.zoom("oligomer", buffer=3.0)
    _rec(pml, "orient oligomer\nzoom oligomer, buffer=3.0")

    outputs: List[Tuple[str, str, str]] = []
    if view == "both":
        outputs.append(
            render_outputs(
                cmd,
                f"{out_prefix}_top",
                width=width,
                height=height,
                dpi=dpi,
                use_ray=use_ray,
                transparent=transparent,
                auto_crop=auto_crop,
                crop_padding=crop_padding,
                pml_lines=list(pml),
            )
        )
        cmd.turn("x", 90)
        _rec(pml, "turn x, 90")
        outputs.append(
            render_outputs(
                cmd,
                f"{out_prefix}_side",
                width=width,
                height=height,
                dpi=dpi,
                use_ray=use_ray,
                transparent=transparent,
                auto_crop=auto_crop,
                crop_padding=crop_padding,
                pml_lines=pml,
            )
        )
    else:
        if view == "side":
            cmd.turn("x", 90)
            _rec(pml, "turn x, 90")
        outputs.append(
            render_outputs(
                cmd,
                out_prefix,
                width=width,
                height=height,
                dpi=dpi,
                use_ray=use_ray,
                transparent=transparent,
                auto_crop=auto_crop,
                crop_padding=crop_padding,
                pml_lines=pml,
            )
        )
    return outputs


def render_active_site(
    cmd,
    structure: str,
    out_prefix: str,
    style: str = "baker_rfd",
    reference: Optional[str] = None,
    catalytic_sele: Optional[str] = None,
    ligand_sele: str = "organic",
    metal_sele: str = "resn MG+ZN+FE+MN+CU+NI+CO+CA",
    scaffold_transparency: Optional[float] = None,
    zoom_buffer: float = 6.0,
    with_inset: bool = False,
    cylindrical_helices: Optional[bool] = None,
    width: int = 2000,
    height: int = 1600,
    dpi: int = 300,
    use_ray: bool = True,
    transparent: bool = False,
    auto_crop: bool = False,
    crop_padding: int = 24,
) -> Tuple[str, ...]:
    """Render an enzyme active site, small-molecule pocket, or DNA complex."""
    _validate_style(style)
    defaults = STYLE_DEFAULTS[style]
    transp = scaffold_transparency if scaffold_transparency is not None else (0.62 if style == "spotlight" else 0.55)

    pml: List[str] = [f"# Publication Style ({style}): Active Site & Ligand Pocket"]
    apply_theme(cmd, style=style, cylindrical_helices=cylindrical_helices, transparent=transparent, pml_lines=pml)

    verify_and_load(cmd, structure, "enzyme", pml_lines=pml)
    ensure_cartoon_trace(cmd, "enzyme", pml_lines=pml)

    cmd.hide("everything", "all")
    _rec(pml, "hide everything, all")

    if style == "goodsell":
        _apply_goodsell_spheres(
            cmd, "enzyme and polymer.protein", base_color=defaults["target_color"], transparency=0.35, pml_lines=pml
        )
    else:
        cmd.show("cartoon", "enzyme and polymer.protein")
        color_style_spectrum(cmd, "enzyme", style=style, palette_mode="rfd2", pml_lines=pml)
        cmd.set("cartoon_transparency", transp, "enzyme and polymer.protein")
        _rec(
            pml,
            "show cartoon, enzyme and polymer.protein\n"
            f"set cartoon_transparency, {transp}, enzyme and polymer.protein",
        )

    if cmd.count_atoms("enzyme and polymer.nucleic") > 0:
        if style == "goodsell":
            _apply_goodsell_spheres(cmd, "enzyme and polymer.nucleic", base_color=defaults["binder_color"], pml_lines=pml)
        else:
            cmd.show("cartoon", "enzyme and polymer.nucleic")
            cmd.show("sticks", "enzyme and polymer.nucleic and not hydro")
            cmd.color("ipd_pastel_iceblue" if style == "baker_rfd" else defaults["binder_color"], "enzyme and polymer.nucleic")
            cmd.util.cnc("enzyme and polymer.nucleic")
            _rec(
                pml,
                "show cartoon, enzyme and polymer.nucleic\n"
                "show sticks, enzyme and polymer.nucleic and not hydro\n"
                "util.cnc enzyme and polymer.nucleic",
            )

    if reference and style != "goodsell":
        verify_and_load(cmd, reference, "ref_pred", pml_lines=pml)
        ensure_cartoon_trace(cmd, "ref_pred", pml_lines=pml)
        method, rmsd, n_aligned = align_structures(cmd, "ref_pred", "enzyme", pml_lines=pml)
        print(f"Active-Site Alignment ({method}): RMSD = {rmsd:.3f} A over {n_aligned} atoms")
        cmd.show("cartoon", "ref_pred and polymer.protein")
        cmd.color(defaults["reference_color"], "ref_pred")
        cmd.set("cartoon_transparency", min(0.78, transp + 0.15), "ref_pred")
        _rec(
            pml,
            f"show cartoon, ref_pred and polymer.protein\n"
            f"color {defaults['reference_color']}, ref_pred\n"
            f"set cartoon_transparency, {min(0.78, transp + 0.15)}, ref_pred",
        )

    focus_parts: List[str] = []

    if catalytic_sele and cmd.count_atoms(f"enzyme and ({catalytic_sele})") > 0:
        cmd.select("catalytic_res", f"enzyme and ({catalytic_sele})")
        if style == "goodsell":
            _apply_goodsell_spheres(cmd, "catalytic_res", base_color=defaults["motif_color"], pml_lines=pml)
        else:
            cmd.show("sticks", "catalytic_res and not name C+O")
            cmd.hide("sticks", "catalytic_res and hydro")
            cmd.color(defaults["connector_color"], "catalytic_res and name CA+CB+N+C+O")
            cmd.color(defaults["motif_color"], "catalytic_res and not name CA+CB+N+C+O")
            cmd.util.cnc("catalytic_res")
            _rec(
                pml,
                f"select catalytic_res, enzyme and ({catalytic_sele})\n"
                "show sticks, catalytic_res and not name C+O\n"
                "hide sticks, catalytic_res and hydro\n"
                f"color {defaults['connector_color']}, catalytic_res and name CA+CB+N+C+O\n"
                f"color {defaults['motif_color']}, catalytic_res and not name CA+CB+N+C+O\n"
                "util.cnc catalytic_res",
            )
        focus_parts.append("catalytic_res")

    if ligand_sele and cmd.count_atoms(f"enzyme and ({ligand_sele})") > 0:
        cmd.select("active_ligand", f"enzyme and ({ligand_sele})")
        if style == "goodsell":
            _apply_goodsell_spheres(cmd, "active_ligand", base_color=defaults["ligand_color"], pml_lines=pml)
        else:
            cmd.show("sticks", "active_ligand")
            cmd.hide("sticks", "active_ligand and hydro")
            cmd.color(defaults["ligand_color"], "active_ligand")
            cmd.util.cnc("active_ligand")
            _rec(
                pml,
                f"select active_ligand, enzyme and ({ligand_sele})\n"
                "show sticks, active_ligand\n"
                "hide sticks, active_ligand and hydro\n"
                f"color {defaults['ligand_color']}, active_ligand\n"
                "util.cnc active_ligand",
            )
        focus_parts.append("active_ligand")

    if metal_sele and cmd.count_atoms(f"enzyme and ({metal_sele})") > 0:
        cmd.select("active_metal", f"enzyme and ({metal_sele})")
        cmd.show("spheres", "active_metal")
        cmd.set("sphere_scale", 0.55, "active_metal")
        if cmd.count_atoms("active_metal and resn MG") > 0:
            cmd.color("ipd_metal_green", "active_metal and resn MG")
        if cmd.count_atoms("active_metal and not resn MG") > 0:
            cmd.color("ipd_metal_ochre", "active_metal and not resn MG")
        focus_parts.append("active_metal")
        _rec(
            pml,
            f"select active_metal, enzyme and ({metal_sele})\n"
            "show spheres, active_metal\nset sphere_scale, 0.55, active_metal\n"
            "color ipd_metal_ochre, active_metal",
        )

    focus_expr = " or ".join(focus_parts) if focus_parts else "enzyme"
    if with_inset:
        cmd.orient("enzyme")
        cmd.zoom("enzyme", buffer=3.0)
        g_out = render_outputs(
            cmd,
            f"{out_prefix}_global",
            width=width,
            height=height,
            dpi=dpi,
            use_ray=use_ray,
            transparent=transparent,
            auto_crop=auto_crop,
            crop_padding=crop_padding,
            pml_lines=list(pml),
        )
        cmd.orient(focus_expr)
        cmd.zoom(focus_expr, buffer=zoom_buffer)
        _rec(pml, f"orient {focus_expr}\nzoom {focus_expr}, buffer={zoom_buffer}")
        i_out = render_outputs(
            cmd,
            f"{out_prefix}_inset",
            width=width,
            height=height,
            dpi=dpi,
            use_ray=use_ray,
            transparent=transparent,
            auto_crop=auto_crop,
            crop_padding=crop_padding,
            pml_lines=pml,
        )
        comp = _stitch_inset_composite(g_out[0], i_out[0], f"{out_prefix}_composite.png", transparent=transparent)
        return (g_out[0], i_out[0], comp)

    if focus_parts:
        cmd.orient(focus_expr)
        cmd.zoom(focus_expr, buffer=zoom_buffer)
        _rec(pml, f"orient {focus_expr}\nzoom {focus_expr}, buffer={zoom_buffer}")
    else:
        cmd.orient("enzyme")
        cmd.zoom("enzyme", buffer=3.0)
        _rec(pml, "orient enzyme\nzoom enzyme, buffer=3.0")

    return render_outputs(
        cmd,
        out_prefix,
        width=width,
        height=height,
        dpi=dpi,
        use_ray=use_ray,
        transparent=transparent,
        auto_crop=auto_crop,
        crop_padding=crop_padding,
        pml_lines=pml,
    )


def render_antibody(
    cmd,
    complex_path: str,
    antigen_chain: str,
    heavy_chain: str,
    out_prefix: str,
    light_chain: Optional[str] = None,
    style: str = "antibody_cdr",
    cdr_h1: str = "26-35",
    cdr_h2: str = "50-65",
    cdr_h3: str = "95-102",
    cdr_l1: str = "24-34",
    cdr_l2: str = "50-56",
    cdr_l3: str = "89-97",
    footprint_cutoff: float = 4.5,
    with_inset: bool = False,
    cylindrical_helices: Optional[bool] = None,
    width: int = 2000,
    height: int = 1600,
    dpi: int = 300,
    use_ray: bool = True,
    transparent: bool = False,
    auto_crop: bool = False,
    crop_padding: int = 24,
) -> Tuple[str, ...]:
    """Render an antibody/nanobody-antigen complex with color-coded CDR loops and 4.5 A epitope footprints."""
    _validate_style(style)
    pml: List[str] = [f"# Publication Style ({style}): Antibody CDR & Epitope Footprint"]
    apply_theme(cmd, style=style, cylindrical_helices=cylindrical_helices, transparent=transparent, pml_lines=pml)

    verify_and_load(cmd, complex_path, "ab_complex", pml_lines=pml)
    ensure_cartoon_trace(cmd, "ab_complex", pml_lines=pml)
    cmd.hide("everything", "all")
    _rec(pml, "hide everything, all")

    ag_sel = f"ab_complex and chain {antigen_chain} and polymer.protein"
    vh_sel = f"ab_complex and chain {heavy_chain} and polymer.protein"
    if cmd.count_atoms(ag_sel) == 0:
        raise ValueError(f"Antigen selection '{ag_sel}' matched 0 atoms.")
    if cmd.count_atoms(vh_sel) == 0:
        raise ValueError(f"Heavy chain selection '{vh_sel}' matched 0 atoms.")

    # Antigen surface
    cmd.show("surface", ag_sel)
    cmd.set("surface_color", "ab_antigen_surf", ag_sel)
    cmd.color("ab_antigen_surf", ag_sel)
    _rec(pml, f"show surface, {ag_sel}\nset surface_color, ab_antigen_surf, {ag_sel}\ncolor ab_antigen_surf, {ag_sel}")

    # Heavy & optional light framework
    cmd.show("cartoon", vh_sel)
    cmd.color("ab_framework_vh", vh_sel)
    _rec(pml, f"show cartoon, {vh_sel}\ncolor ab_framework_vh, {vh_sel}")

    cdr_specs: List[Tuple[str, str, str, str]] = [
        ("cdr_h1", heavy_chain, cdr_h1, "ab_cdr_h1"),
        ("cdr_h2", heavy_chain, cdr_h2, "ab_cdr_h2"),
        ("cdr_h3", heavy_chain, cdr_h3, "ab_cdr_h3"),
    ]
    if light_chain:
        vl_sel = f"ab_complex and chain {light_chain} and polymer.protein"
        if cmd.count_atoms(vl_sel) == 0:
            raise ValueError(f"Light chain selection '{vl_sel}' matched 0 atoms.")
        cmd.show("cartoon", vl_sel)
        cmd.color("ab_framework_vl", vl_sel)
        _rec(pml, f"show cartoon, {vl_sel}\ncolor ab_framework_vl, {vl_sel}")
        cdr_specs.extend(
            [
                ("cdr_l1", light_chain, cdr_l1, "ab_cdr_l1"),
                ("cdr_l2", light_chain, cdr_l2, "ab_cdr_l2"),
                ("cdr_l3", light_chain, cdr_l3, "ab_cdr_l3"),
            ]
        )

    cdr_names: List[str] = []
    for name, ch, rng, col in cdr_specs:
        sel_expr = f"ab_complex and chain {ch} and resi {rng} and polymer.protein"
        if cmd.count_atoms(sel_expr) == 0:
            continue
        cmd.select(name, sel_expr)
        cmd.color(col, name)
        _rec(pml, f"select {name}, {sel_expr}\ncolor {col}, {name}")
        if name == "cdr_h3":
            cmd.set("cartoon_loop_radius", 0.28, name)
            cmd.show("sticks", f"{name} and not name C+O+N")
            cmd.hide("sticks", f"{name} and hydro")
            cmd.util.cnc(name)
            _rec(
                pml,
                f"set cartoon_loop_radius, 0.28, {name}\n"
                f"show sticks, {name} and not name C+O+N\n"
                f"hide sticks, {name} and hydro\nutil.cnc {name}",
            )
        cdr_names.append(name)

        # Project epitope footprint on antigen surface
        fp_name = f"epitope_{name}"
        fp_expr = f"byres (({ag_sel}) within {footprint_cutoff} of ({name}))"
        if cmd.count_atoms(fp_expr) > 0:
            cmd.select(fp_name, fp_expr)
            cmd.color(col, fp_name)
            cmd.set("surface_color", col, fp_name)
            _rec(pml, f"select {fp_name}, {fp_expr}\ncolor {col}, {fp_name}\nset surface_color, {col}, {fp_name}")

    # H-bonds between CDR loops and antigen
    if cdr_names:
        all_cdr_expr = " or ".join(cdr_names)
        cmd.select("cdr_all", all_cdr_expr)
        cmd.select("epitope_all", f"byres (({ag_sel}) within {footprint_cutoff} of cdr_all)")
        cmd.distance("ab_hbonds", "cdr_all", "epitope_all", cutoff=3.5, mode=2)
        cmd.set("dash_color", "spot_dash_gray")
        cmd.hide("labels", "ab_hbonds")
        _rec(
            pml,
            f"select cdr_all, {all_cdr_expr}\n"
            f"select epitope_all, byres (({ag_sel}) within {footprint_cutoff} of cdr_all)\n"
            "distance ab_hbonds, cdr_all, epitope_all, cutoff=3.5, mode=2\n"
            "set dash_color, spot_dash_gray\nhide labels, ab_hbonds",
        )

    if with_inset:
        cmd.orient("ab_complex")
        cmd.zoom("ab_complex", buffer=3.0)
        g_out = render_outputs(
            cmd,
            f"{out_prefix}_global",
            width=width,
            height=height,
            dpi=dpi,
            use_ray=use_ray,
            transparent=transparent,
            auto_crop=auto_crop,
            crop_padding=crop_padding,
            pml_lines=list(pml),
        )
        focus_sel = "cdr_all or epitope_all" if cmd.count_atoms("cdr_all or epitope_all") > 0 else vh_sel
        cmd.orient(focus_sel)
        cmd.zoom(focus_sel, buffer=4.5)
        _rec(pml, f"orient {focus_sel}\nzoom {focus_sel}, buffer=4.5")
        i_out = render_outputs(
            cmd,
            f"{out_prefix}_inset",
            width=width,
            height=height,
            dpi=dpi,
            use_ray=use_ray,
            transparent=transparent,
            auto_crop=auto_crop,
            crop_padding=crop_padding,
            pml_lines=pml,
        )
        comp = _stitch_inset_composite(g_out[0], i_out[0], f"{out_prefix}_composite.png", transparent=transparent)
        return (g_out[0], i_out[0], comp)

    cmd.orient("ab_complex")
    cmd.zoom("ab_complex", buffer=3.0)
    _rec(pml, "orient ab_complex\nzoom ab_complex, buffer=3.0")
    return render_outputs(
        cmd,
        out_prefix,
        width=width,
        height=height,
        dpi=dpi,
        use_ray=use_ray,
        transparent=transparent,
        auto_crop=auto_crop,
        crop_padding=crop_padding,
        pml_lines=pml,
    )


def _compute_in_pocket_ligand_rmsd(cmd, sel_a: str, sel_b: str) -> Tuple[float, int]:
    """Compute heavy-atom in-pocket ligand RMSD (without moving coordinates)."""
    try:
        rmsd = float(cmd.rms_cur(f"({sel_a}) and not hydro", f"({sel_b}) and not hydro", matchmaker=0))
        n_heavy = cmd.count_atoms(f"({sel_a}) and not hydro")
        return (rmsd, n_heavy)
    except Exception:
        pass

    # Fallback: align by nearest heavy-atom coordinates of matching element (e.g. different atom names)
    m_a = cmd.get_model(f"({sel_a}) and not hydro")
    m_b = cmd.get_model(f"({sel_b}) and not hydro")
    atoms_a = [(a.symbol, a.coord) for a in m_a.atom]
    atoms_b = [(b.symbol, b.coord) for b in m_b.atom]
    if not atoms_a or not atoms_b:
        raise ValueError("Cannot compute ligand RMSD: empty ligand heavy-atom selection.")

    used = set()
    sq_dists: List[float] = []
    for sym, ca in atoms_a:
        best_j = -1
        best_d2 = float("inf")
        for j, (sym_b, cb) in enumerate(atoms_b):
            if j in used or (sym and sym_b and sym != sym_b):
                continue
            d2 = (ca[0] - cb[0]) ** 2 + (ca[1] - cb[1]) ** 2 + (ca[2] - cb[2]) ** 2
            if d2 < best_d2:
                best_d2 = d2
                best_j = j
        if best_j >= 0:
            used.add(best_j)
            sq_dists.append(best_d2)
    if not sq_dists:
        raise ValueError("No matching heavy atoms found between reference and predicted ligands.")
    return (math.sqrt(sum(sq_dists) / len(sq_dists)), len(sq_dists))


def render_ligand_pocket(
    cmd,
    structure: str,
    out_prefix: str,
    style: str = "pocket_cavity",
    reference: Optional[str] = None,
    ligand_sele: str = "organic",
    ref_ligand_sele: Optional[str] = None,
    pocket_radius: float = 6.0,
    with_inset: bool = False,
    cylindrical_helices: Optional[bool] = None,
    width: int = 2000,
    height: int = 1600,
    dpi: int = 300,
    use_ray: bool = True,
    transparent: bool = False,
    auto_crop: bool = False,
    crop_padding: int = 24,
) -> Tuple[str, ...]:
    """Render local binding-site cutaway cavity with optional reference ligand pose RMSD."""
    _validate_style(style)
    defaults = STYLE_DEFAULTS[style]
    pml: List[str] = [f"# Publication Style ({style}): Local Pocket Cavity & Pose Overlay"]
    apply_theme(cmd, style=style, cylindrical_helices=cylindrical_helices, transparent=transparent, pml_lines=pml)

    verify_and_load(cmd, structure, "complex", pml_lines=pml)
    ensure_cartoon_trace(cmd, "complex", pml_lines=pml)
    cmd.hide("everything", "all")
    _rec(pml, "hide everything, all")

    lig_sel = f"complex and ({ligand_sele})"
    if cmd.count_atoms(lig_sel) == 0:
        raise ValueError(f"Ligand selection '{lig_sel}' matched 0 atoms.")

    # Faint full protein backbone
    cmd.show("cartoon", "complex and polymer.protein")
    cmd.color("pocket_res_carbon", "complex and polymer.protein")
    cmd.set("cartoon_transparency", 0.72, "complex and polymer.protein")
    _rec(
        pml,
        "show cartoon, complex and polymer.protein\n"
        "color pocket_res_carbon, complex and polymer.protein\n"
        "set cartoon_transparency, 0.72, complex and polymer.protein",
    )

    # Local pocket cutaway surface & sticks
    cmd.select("pocket_res", f"byres ((complex and polymer.protein) within {pocket_radius} of ({lig_sel}))")
    cmd.show("surface", "pocket_res")
    cmd.set("surface_color", defaults["target_color"], "pocket_res")
    cmd.set("transparency", 0.42, "pocket_res")
    cmd.show("sticks", "pocket_res and not name C+O")
    cmd.hide("sticks", "pocket_res and hydro")
    cmd.color("pocket_res_carbon", "pocket_res")
    cmd.util.cnc("pocket_res")
    _rec(
        pml,
        f"select pocket_res, byres ((complex and polymer.protein) within {pocket_radius} of ({lig_sel}))\n"
        f"show surface, pocket_res\nset surface_color, {defaults['target_color']}, pocket_res\n"
        "set transparency, 0.42, pocket_res\n"
        "show sticks, pocket_res and not name C+O\nhide sticks, pocket_res and hydro\n"
        "color pocket_res_carbon, pocket_res\nutil.cnc pocket_res",
    )

    # Primary ligand sticks
    cmd.select("active_ligand", lig_sel)
    cmd.show("sticks", "active_ligand")
    cmd.hide("sticks", "active_ligand and hydro")
    cmd.color(defaults["ligand_color"], "active_ligand")
    cmd.util.cnc("active_ligand")
    cmd.distance("pocket_hbonds", "active_ligand", "pocket_res", cutoff=3.5, mode=2)
    cmd.set("dash_color", defaults["dash_color"])
    cmd.hide("labels", "pocket_hbonds")
    _rec(
        pml,
        f"select active_ligand, {lig_sel}\n"
        "show sticks, active_ligand\nhide sticks, active_ligand and hydro\n"
        f"color {defaults['ligand_color']}, active_ligand\nutil.cnc active_ligand\n"
        "distance pocket_hbonds, active_ligand, pocket_res, cutoff=3.5, mode=2\n"
        f"set dash_color, {defaults['dash_color']}\nhide labels, pocket_hbonds",
    )

    if reference:
        verify_and_load(cmd, reference, "ref_complex", pml_lines=pml)
        cmd.hide("everything", "ref_complex")
        if cmd.count_atoms("ref_complex and polymer.protein") > 0:
            method, prot_rmsd, n_prot = align_structures(cmd, "ref_complex", "complex", pml_lines=pml)
            print(f"Pocket Protein Alignment ({method}): RMSD = {prot_rmsd:.3f} A over {n_prot} atoms")
        rl_sel = f"ref_complex and ({ref_ligand_sele or ligand_sele})"
        if cmd.count_atoms(rl_sel) == 0:
            raise ValueError(f"Reference ligand selection '{rl_sel}' matched 0 atoms.")
        cmd.select("ref_ligand", rl_sel)
        cmd.show("sticks", "ref_ligand")
        cmd.hide("sticks", "ref_ligand and hydro")
        cmd.color(defaults["reference_color"], "ref_ligand")
        cmd.util.cnc("ref_ligand")
        lig_rmsd, n_lig = _compute_in_pocket_ligand_rmsd(cmd, "ref_ligand", "active_ligand")
        print(f"In-Pocket Ligand Heavy-Atom RMSD = {lig_rmsd:.3f} A ({n_lig} heavy atoms)")
        _rec(
            pml,
            "hide everything, ref_complex\n"
            f"select ref_ligand, {rl_sel}\n"
            "show sticks, ref_ligand\nhide sticks, ref_ligand and hydro\n"
            f"color {defaults['reference_color']}, ref_ligand\nutil.cnc ref_ligand",
        )

    focus_sel = "active_ligand or pocket_res"
    if with_inset:
        cmd.orient("complex")
        cmd.zoom("complex", buffer=3.0)
        g_out = render_outputs(
            cmd,
            f"{out_prefix}_global",
            width=width,
            height=height,
            dpi=dpi,
            use_ray=use_ray,
            transparent=transparent,
            auto_crop=auto_crop,
            crop_padding=crop_padding,
            pml_lines=list(pml),
        )
        cmd.orient(focus_sel)
        cmd.zoom(focus_sel, buffer=4.0)
        _rec(pml, f"orient {focus_sel}\nzoom {focus_sel}, buffer=4.0")
        i_out = render_outputs(
            cmd,
            f"{out_prefix}_inset",
            width=width,
            height=height,
            dpi=dpi,
            use_ray=use_ray,
            transparent=transparent,
            auto_crop=auto_crop,
            crop_padding=crop_padding,
            pml_lines=pml,
        )
        comp = _stitch_inset_composite(g_out[0], i_out[0], f"{out_prefix}_composite.png", transparent=transparent)
        return (g_out[0], i_out[0], comp)

    cmd.orient(focus_sel)
    cmd.zoom(focus_sel, buffer=4.0)
    _rec(pml, f"orient {focus_sel}\nzoom {focus_sel}, buffer=4.0")
    return render_outputs(
        cmd,
        out_prefix,
        width=width,
        height=height,
        dpi=dpi,
        use_ray=use_ray,
        transparent=transparent,
        auto_crop=auto_crop,
        crop_padding=crop_padding,
        pml_lines=pml,
    )


def render_trajectory_strip(
    cmd,
    out_prefix: str,
    structure: Optional[str] = None,
    structures: Optional[Sequence[str]] = None,
    n_frames: int = 5,
    style: str = "baker_rfd",
    cylindrical_helices: Optional[bool] = None,
    width: int = 900,
    height: int = 900,
    dpi: int = 300,
    use_ray: bool = True,
    transparent: bool = False,
) -> Tuple[str, str, str]:
    """Render N frames from a trajectory (multi-state or file list) with locked camera and stitch horizontally."""
    from PIL import Image, ImageDraw

    _validate_style(style)
    pml: List[str] = [f"# Publication Style ({style}): Trajectory Progression Strip"]
    apply_theme(cmd, style=style, cylindrical_helices=cylindrical_helices, transparent=transparent, pml_lines=pml)

    out_dir = os.path.dirname(os.path.abspath(out_prefix))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    frame_paths: List[str] = []
    frame_labels: List[str] = []

    if structures:
        files = list(structures)
        total = len(files)
        if total == 0:
            raise ValueError("No trajectory structure files provided.")
        indices = (
            [round(i * (total - 1) / (n_frames - 1)) for i in range(n_frames)]
            if total > n_frames and n_frames > 1
            else list(range(total))
        )
        # Lock camera to final frame
        verify_and_load(cmd, files[indices[-1]], "last_frame")
        ensure_cartoon_trace(cmd, "last_frame")
        cmd.orient("last_frame")
        cmd.zoom("last_frame", buffer=3.0)
        locked_view = cmd.get_view()
        cmd.delete("last_frame")

        for k, idx in enumerate(indices):
            cmd.delete("traj_frame")
            verify_and_load(cmd, files[idx], "traj_frame", pml_lines=pml)
            if not ensure_cartoon_trace(cmd, "traj_frame", pml_lines=pml):
                cmd.dss("traj_frame")
            cmd.hide("everything", "traj_frame")
            cmd.show("cartoon", "traj_frame and polymer.protein")
            color_style_spectrum(cmd, "traj_frame", style=style, pml_lines=pml)
            cmd.set_view(locked_view)
            fp = f"{out_prefix}_frame_{k}.png"
            if use_ray:
                cmd.ray(width, height)
            cmd.png(fp, width=width, height=height, dpi=dpi, ray=1 if use_ray else 0)
            frame_paths.append(fp)
            t_val = idx / max(1, total - 1)
            frame_labels.append(f"t = {t_val:.2f}")
    elif structure:
        verify_and_load(cmd, structure, "traj", pml_lines=pml)
        is_ca = ensure_cartoon_trace(cmd, "traj", pml_lines=pml)
        total_states = cmd.count_states("traj")
        if not is_ca:
            cmd.dss("traj", state=total_states)
        cmd.hide("everything", "traj")
        cmd.show("cartoon", "traj and polymer.protein")
        color_style_spectrum(cmd, "traj", style=style, pml_lines=pml)

        if total_states <= 1:
            state_indices = [1]
        elif total_states <= n_frames:
            state_indices = list(range(1, total_states + 1))
        else:
            state_indices = [1 + round(i * (total_states - 1) / (n_frames - 1)) for i in range(n_frames)]

        cmd.set("state", state_indices[-1])
        cmd.orient("traj")
        cmd.zoom("traj", buffer=3.0)
        locked_view = cmd.get_view()

        for k, st in enumerate(state_indices):
            cmd.set("state", st)
            cmd.set_view(locked_view)
            fp = f"{out_prefix}_frame_{k}.png"
            if use_ray:
                cmd.ray(width, height)
            cmd.png(fp, width=width, height=height, dpi=dpi, ray=1 if use_ray else 0)
            frame_paths.append(fp)
            t_val = (st - 1) / max(1, total_states - 1) if total_states > 1 else 1.0
            frame_labels.append(f"t = {t_val:.2f}")
    else:
        raise ValueError("Provide either --structure (multi-state) or --structures (comma-separated files).")

    # Stitch frames horizontally with labels
    imgs = [Image.open(p).convert("RGBA" if transparent else "RGB") for p in frame_paths]
    font = _get_font(size=28)
    label_h = 56
    gap = 24
    total_w = sum(im.width for im in imgs) + gap * (len(imgs) - 1)
    max_h = max(im.height for im in imgs) + label_h
    bg = (255, 255, 255, 0) if transparent else (255, 255, 255)
    canvas = Image.new("RGBA" if transparent else "RGB", (total_w, max_h), bg)
    draw = ImageDraw.Draw(canvas)

    x_off = 0
    for idx, (im, lbl) in enumerate(zip(imgs, frame_labels)):
        canvas.paste(im, (x_off, label_h), im if transparent else None)
        draw.text((x_off + im.width // 2 - 42, 12), lbl, font=font, fill=(45, 45, 50, 255) if transparent else (45, 45, 50))
        if idx < len(imgs) - 1:
            ax1 = x_off + im.width + 2
            ax2 = x_off + im.width + gap - 4
            ay = label_h + im.height // 2
            draw.line([(ax1, ay), (ax2, ay)], fill=(72, 72, 76), width=4)
        x_off += im.width + gap

    strip_png = f"{out_prefix}.png"
    canvas.save(strip_png)
    pse_path = f"{out_prefix}.pse"
    pml_path = f"{out_prefix}.pml"
    cmd.save(pse_path)
    with open(pml_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(pml) + "\n")
    return (strip_png, pse_path, pml_path)


def render_showcase(
    cmd,
    structure: str,
    out_prefix: str,
    mode: str = "monomer",
    styles: Sequence[str] = CORE_SHOWCASE_STYLES,
    target_chain: Optional[str] = None,
    binder_chain: Optional[str] = None,
    hotspots: Optional[str] = None,
    catalytic_sele: Optional[str] = None,
    ligand_sele: str = "organic",
    cell_width: int = 1000,
    cell_height: int = 800,
    dpi: int = 200,
    use_ray: bool = True,
) -> str:
    """Render a structure across multiple publication styles from the same camera view into a labeled grid."""
    from PIL import Image, ImageDraw

    out_dir = os.path.dirname(os.path.abspath(out_prefix))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    panel_paths: List[Tuple[str, str]] = []
    locked_view = None

    for style in styles:
        _validate_style(style)
        cmd.reinitialize()
        apply_theme(cmd, style=style)

        cell_prefix = f"{out_prefix}_cell_{style}"
        if mode == "binder":
            if not target_chain or not binder_chain:
                raise ValueError("--target-chain and --binder-chain are required for showcase --mode binder.")
            # Setup binder scene without immediate render so we can lock view
            render_binder(
                cmd,
                complex_path=structure,
                target_chain=target_chain,
                binder_chain=binder_chain,
                out_prefix=cell_prefix,
                style=style,
                hotspots=hotspots,
                width=cell_width,
                height=cell_height,
                dpi=dpi,
                use_ray=False,
            )
        elif mode == "active_site":
            render_active_site(
                cmd,
                structure=structure,
                out_prefix=cell_prefix,
                style=style,
                catalytic_sele=catalytic_sele,
                ligand_sele=ligand_sele,
                width=cell_width,
                height=cell_height,
                dpi=dpi,
                use_ray=False,
            )
        elif mode == "oligomer":
            render_oligomer(
                cmd,
                structure=structure,
                out_prefix=cell_prefix,
                style=style,
                width=cell_width,
                height=cell_height,
                dpi=dpi,
                use_ray=False,
            )
        else:
            render_monomer(
                cmd,
                structure=structure,
                out_prefix=cell_prefix,
                style=style,
                width=cell_width,
                height=cell_height,
                dpi=dpi,
                use_ray=False,
            )

        if locked_view is None:
            locked_view = cmd.get_view()
        else:
            cmd.set_view(locked_view)

        if use_ray:
            cmd.ray(cell_width, cell_height)
        cmd.png(f"{cell_prefix}.png", width=cell_width, height=cell_height, dpi=dpi, ray=1 if use_ray else 0)
        panel_paths.append((style, f"{cell_prefix}.png"))

    cols = 3 if len(panel_paths) >= 3 else len(panel_paths)
    rows = math.ceil(len(panel_paths) / cols)
    font = _get_font(size=28)
    label_h = 56
    pad = 16
    grid_w = cols * cell_width + (cols + 1) * pad
    grid_h = rows * (cell_height + label_h) + (rows + 1) * pad
    grid = Image.new("RGB", (grid_w, grid_h), (255, 255, 255))
    draw = ImageDraw.Draw(grid)

    for idx, (style, p_path) in enumerate(panel_paths):
        r = idx // cols
        c = idx % cols
        x = pad + c * (cell_width + pad)
        y = pad + r * (cell_height + label_h + pad)
        im = Image.open(p_path).convert("RGB")
        grid.paste(im, (x, y + label_h))
        draw.rectangle([x, y, x + cell_width, y + cell_height + label_h], outline=(215, 218, 224), width=2)
        draw.text((x + 18, y + 12), f"--style {style}", font=font, fill=(35, 38, 45))

    grid_png = f"{out_prefix}.png"
    grid.save(grid_png)
    return grid_png
