"""
PyMOL Publication Styles Engine.

Supports 6 classic structural biology & protein design publication styles:
  - baker_rfd      : Baker Lab / IPD RFdiffusion 1-3 matte cel-shaded pastel style (default)
  - goodsell       : David Goodsell / RCSB Molecule of the Month watercolor sphere style
  - cylindrical    : Nature / Cell minimalist cylindrical-helix architecture style
  - chimerax_soft  : ChimeraX soft-shadow / matte ceramic ambient-occlusion cryo-EM style
  - spotlight      : Monochrome ghost scaffold + jewel-tone focal site spotlight style
  - alphafold_plddt: Canonical AlphaFold / ColabFold pLDDT confidence threshold style

Generates publication-ready PNG, interactive .pse session, and companion .pml script.
"""

from __future__ import annotations

import os
from typing import Dict, List, Optional, Tuple

VALID_STYLES = (
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
}

# Backwards-compatible alias
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
}

OLIGOMER_CHAIN_CYCLE = STYLE_CHAIN_CYCLES["baker_rfd"]

STYLE_SPECTRUM_STOPS: Dict[str, str] = {
    "baker_rfd": "ipd_pastel_peach ipd_pastel_rose ipd_pastel_lavender ipd_pastel_deepblue",
    "baker_rfd2": "ipd_pastel_peach ipd_pastel_rose ipd_pastel_lavender ipd_pastel_iceblue",
    "goodsell": "goodsell_coral goodsell_ochre goodsell_sage goodsell_sky",
    "cylindrical": "arch_navy arch_teal arch_gold arch_coral",
    "chimerax_soft": "em_cobalt em_mint em_ochre em_salmon",
    "spotlight": "spot_ghost_gray",
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


# Backwards-compatible alias
register_ipd_palette = register_palette


def apply_theme(
    cmd,
    style: str = "baker_rfd",
    cylindrical_helices: Optional[bool] = None,
    pml_lines: Optional[List[str]] = None,
) -> None:
    """Apply lighting, ray-tracing, and geometry parameters for a given publication style."""
    _validate_style(style)
    register_palette(cmd, pml_lines=pml_lines)

    # Common crisp white canvas & smooth geometry baseline
    base_settings: List[Tuple[str, object]] = [
        ("ray_opaque_background", 1),
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
    else:  # baker_rfd
        style_settings = [
            ("ray_trace_mode", 1),
            ("ray_trace_gain", 0.10),
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
            ("ambient_occlusion_scale", 15.0),
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
    pml_lines: Optional[List[str]] = None,
) -> None:
    """Backwards-compatible wrapper for applying the baker_rfd IPD theme."""
    apply_theme(cmd, style="baker_rfd", cylindrical_helices=cylindrical_helices, pml_lines=pml_lines)
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


# Backwards-compatible alias
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


def render_outputs(
    cmd,
    out_prefix: str,
    width: int = 2000,
    height: int = 1600,
    dpi: int = 300,
    use_ray: bool = True,
    pml_lines: Optional[List[str]] = None,
) -> Tuple[str, str, str]:
    """Render PNG, save .pse session, and write companion .pml script."""
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
) -> Tuple[str, str, str]:
    """Render a monomer, motif-scaffolded design, or design-vs-validation overlay."""
    _validate_style(style)
    defaults = STYLE_DEFAULTS[style]
    cycle = STYLE_CHAIN_CYCLES[style]
    pml: List[str] = [f"# Publication Style ({style}): Monomer & Overlay"]
    apply_theme(cmd, style=style, cylindrical_helices=cylindrical_helices, pml_lines=pml)

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
        cmd, out_prefix, width=width, height=height, dpi=dpi, use_ray=use_ray, pml_lines=pml
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
    cylindrical_helices: Optional[bool] = None,
    width: int = 2000,
    height: int = 1600,
    dpi: int = 300,
    use_ray: bool = True,
) -> Tuple[str, str, str]:
    """Render a target-binder complex in the selected publication style."""
    _validate_style(style)
    defaults = STYLE_DEFAULTS[style]
    t_color = target_color or defaults["target_color"]
    b_color = binder_color or defaults["binder_color"]

    pml: List[str] = [f"# Publication Style ({style}): Target-Binder Complex"]
    apply_theme(cmd, style=style, cylindrical_helices=cylindrical_helices, pml_lines=pml)

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
    else:
        # Target representation
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

        # Binder representation
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

    if (show_interface_sticks or zoom_interface) and style != "goodsell":
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

    if zoom_interface:
        cmd.orient("iface_binder or iface_target")
        cmd.zoom("iface_binder or iface_target", buffer=4.0)
        _rec(pml, "orient iface_binder or iface_target\nzoom iface_binder or iface_target, buffer=4.0")
    else:
        cmd.orient("complex")
        cmd.zoom("complex", buffer=3.0)
        _rec(pml, "orient complex\nzoom complex, buffer=3.0")

    return render_outputs(
        cmd, out_prefix, width=width, height=height, dpi=dpi, use_ray=use_ray, pml_lines=pml
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
) -> List[Tuple[str, str, str]]:
    """Render symmetric oligomers (Cn / Dn / cages) and optional cryo-EM density map."""
    _validate_style(style)
    defaults = STYLE_DEFAULTS[style]
    cycle = STYLE_CHAIN_CYCLES[style]

    pml: List[str] = [f"# Publication Style ({style}): Symmetric Oligomer"]
    apply_theme(cmd, style=style, cylindrical_helices=cylindrical_helices, pml_lines=pml)

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
    cylindrical_helices: Optional[bool] = None,
    width: int = 2000,
    height: int = 1600,
    dpi: int = 300,
    use_ray: bool = True,
) -> Tuple[str, str, str]:
    """Render an enzyme active site, small-molecule pocket, or DNA complex."""
    _validate_style(style)
    defaults = STYLE_DEFAULTS[style]
    transp = scaffold_transparency if scaffold_transparency is not None else (0.62 if style == "spotlight" else 0.55)

    pml: List[str] = [f"# Publication Style ({style}): Active Site & Ligand Pocket"]
    apply_theme(cmd, style=style, cylindrical_helices=cylindrical_helices, pml_lines=pml)

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

    if focus_parts:
        focus_expr = " or ".join(focus_parts)
        cmd.orient(focus_expr)
        cmd.zoom(focus_expr, buffer=zoom_buffer)
        _rec(pml, f"orient {focus_expr}\nzoom {focus_expr}, buffer={zoom_buffer}")
    else:
        cmd.orient("enzyme")
        cmd.zoom("enzyme", buffer=3.0)
        _rec(pml, "orient enzyme\nzoom enzyme, buffer=3.0")

    return render_outputs(
        cmd, out_prefix, width=width, height=height, dpi=dpi, use_ray=use_ray, pml_lines=pml
    )
