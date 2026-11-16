"""
Baker Lab / IPD (RFdiffusion 1-3) PyMOL Styling Engine.

Provides exact RGB color palettes, matte cel-shaded ray-tracing parameters,
C-alpha trace auto-detection, structural alignment with fallback, and
companion .pml script generation for publication-grade figures.
"""

from __future__ import annotations

import os
from typing import List, Optional, Sequence, Tuple

# Exact RGB float triplets [R, G, B] sampled from RFdiffusion 1, 2, and 3 figures.
IPD_PALETTE = {
    # 4-stop N->C pastel topology spectrum & oligomer subunit cycling
    "ipd_pastel_peach": [0.988, 0.831, 0.675],     # #FCD4AC
    "ipd_pastel_rose": [0.988, 0.675, 0.706],      # #FCACB4
    "ipd_pastel_lavender": [0.580, 0.580, 0.769],  # #9494C4
    "ipd_pastel_slate": [0.424, 0.533, 0.769],     # #6C88C4
    "ipd_pastel_deepblue": [0.314, 0.392, 0.675],  # #5064AC
    "ipd_pastel_iceblue": [0.659, 0.737, 0.878],   # #A8BCE0

    # Signature IPD functional motif / catalytic residue teal
    "ipd_motif_teal": [0.298, 0.722, 0.675],       # #4CB8AC

    # Binder & target surface / hotspot colors (RFD1 Fig 6, RFD-beta)
    "ipd_target_sand": [0.988, 0.863, 0.659],      # #FCDCA8
    "ipd_hotspot_orange": [0.941, 0.533, 0.157],   # #F08828
    "ipd_strand_gold": [0.910, 0.737, 0.345],      # #E8BC58

    # Overlay / reference / surface grays
    "ipd_model_gray": [0.784, 0.784, 0.804],       # #C8C8CD
    "ipd_surface_gray": [0.902, 0.902, 0.922],     # #E6E6EB
    "ipd_slate_gray": [0.478, 0.510, 0.557],       # #7A828E

    # All-atom ligands, cofactors, and antibody chains
    "ipd_ligand_carbon": [0.282, 0.282, 0.298],    # #48484C
    "ipd_metal_green": [0.345, 0.439, 0.220],      # #587038
    "ipd_metal_ochre": [0.659, 0.345, 0.220],      # #A85838
    "ipd_vh_navy": [0.204, 0.282, 0.533],          # #344888
}

OLIGOMER_CHAIN_CYCLE = [
    "ipd_pastel_peach",
    "ipd_pastel_rose",
    "ipd_pastel_lavender",
    "ipd_pastel_deepblue",
    "ipd_pastel_slate",
    "ipd_motif_teal",
]


def _rec(pml_lines: Optional[List[str]], line: str) -> None:
    if pml_lines is not None:
        pml_lines.append(line)


def register_ipd_palette(cmd, pml_lines: Optional[List[str]] = None) -> None:
    """Register all RFdiffusion 1-3 IPD custom RGB colors in PyMOL."""
    _rec(pml_lines, "# --- Register IPD / RFdiffusion 1-3 Color Palette ---")
    for name, rgb in IPD_PALETTE.items():
        cmd.set_color(name, rgb)
        _rec(pml_lines, f"set_color {name}, [{rgb[0]:.3f}, {rgb[1]:.3f}, {rgb[2]:.3f}]")


def apply_ipd_theme(
    cmd,
    cylindrical_helices: bool = False,
    ray_outline: bool = True,
    ambient_occlusion: bool = True,
    pml_lines: Optional[List[str]] = None,
) -> None:
    """Apply the RFdiffusion 1-3 matte, outlined, high-ambient PyMOL visual theme."""
    register_ipd_palette(cmd, pml_lines=pml_lines)

    settings: List[Tuple[str, object]] = [
        ("ray_opaque_background", 1),
        ("orthoscopic", 1),
        ("depth_cue", 1),
        ("fog_start", 0.45),
        ("ray_trace_mode", 1 if ray_outline else 0),
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
        ("ambient_occlusion_mode", 1 if ambient_occlusion else 0),
        ("ambient_occlusion_scale", 15.0),
        ("ambient_occlusion_smooth", 10),
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
        ("cartoon_cylindrical_helices", 1 if cylindrical_helices else 0),
        ("cartoon_highlight_color", -1),
        ("stick_radius", 0.22),
        ("stick_ball", 1),
        ("stick_ball_ratio", 1.4),
        ("dash_gap", 0.35),
        ("dash_radius", 0.07),
        ("dash_round_ends", 1),
    ]

    _rec(pml_lines, "\n# --- Apply IPD / RFdiffusion 1-3 Theme Settings ---")
    cmd.bg_color("white")
    _rec(pml_lines, "bg_color white")
    for key, val in settings:
        cmd.set(key, val)
        _rec(pml_lines, f"set {key}, {val}")


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


def color_ipd_spectrum(
    cmd,
    selection: str = "polymer.protein",
    palette_mode: str = "rfd1",
    pml_lines: Optional[List[str]] = None,
) -> None:
    """Apply the 4-stop IPD N->C pastel topology gradient across a protein selection."""
    if palette_mode == "rfd2":
        stops = "ipd_pastel_peach ipd_pastel_rose ipd_pastel_lavender ipd_pastel_iceblue"
    else:
        stops = "ipd_pastel_peach ipd_pastel_rose ipd_pastel_lavender ipd_pastel_deepblue"
    cmd.spectrum("count", stops, f"({selection}) and polymer.protein")
    _rec(pml_lines, f"spectrum count, {stops}, ({selection}) and polymer.protein")


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
    reference: Optional[str] = None,
    motif_sele: Optional[str] = None,
    color_mode: str = "spectrum",
    design_role: str = "gray",
    palette_mode: str = "rfd1",
    cylindrical_helices: bool = False,
    width: int = 2000,
    height: int = 1600,
    dpi: int = 300,
    use_ray: bool = True,
) -> Tuple[str, str, str]:
    """Render a de novo monomer, motif-scaffolded design, or design-vs-validation overlay."""
    pml: List[str] = ["# Baker Lab / IPD Style: Monomer & Overlay"]
    apply_ipd_theme(cmd, cylindrical_helices=cylindrical_helices, pml_lines=pml)

    verify_and_load(cmd, structure, "design", pml_lines=pml)
    ensure_cartoon_trace(cmd, "design", pml_lines=pml)

    cmd.hide("everything", "all")
    cmd.show("cartoon", "polymer.protein")
    _rec(pml, "hide everything, all\nshow cartoon, polymer.protein")

    if reference:
        verify_and_load(cmd, reference, "reference", pml_lines=pml)
        ensure_cartoon_trace(cmd, "reference", pml_lines=pml)
        cmd.show("cartoon", "reference and polymer.protein")
        method, rmsd, n_aligned = align_structures(cmd, "reference", "design", pml_lines=pml)
        print(f"Alignment ({method}): RMSD = {rmsd:.3f} A over {n_aligned} atoms")

        if design_role == "gray":
            cmd.color("ipd_model_gray", "design")
            _rec(pml, "color ipd_model_gray, design")
            color_ipd_spectrum(cmd, "reference", palette_mode=palette_mode, pml_lines=pml)
        else:
            cmd.color("ipd_model_gray", "reference")
            _rec(pml, "color ipd_model_gray, reference")
            color_ipd_spectrum(cmd, "design", palette_mode=palette_mode, pml_lines=pml)
    else:
        if color_mode == "solid":
            cmd.color("ipd_pastel_lavender", "design and polymer.protein")
            _rec(pml, "color ipd_pastel_lavender, design and polymer.protein")
        elif color_mode == "chain":
            for idx, ch in enumerate(cmd.get_chains("design")):
                col = OLIGOMER_CHAIN_CYCLE[idx % len(OLIGOMER_CHAIN_CYCLE)]
                cmd.color(col, f"design and chain {ch}")
                _rec(pml, f"color {col}, design and chain {ch}")
        else:
            color_ipd_spectrum(cmd, "design", palette_mode=palette_mode, pml_lines=pml)

    if motif_sele:
        cmd.select("motif_region", f"design and ({motif_sele})")
        cmd.color("ipd_motif_teal", "motif_region")
        cmd.show("sticks", "motif_region and not name C+O+N")
        cmd.util.cnc("motif_region")
        _rec(
            pml,
            f"select motif_region, design and ({motif_sele})\n"
            "color ipd_motif_teal, motif_region\n"
            "show sticks, motif_region and not name C+O+N\n"
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
    reference_binder: Optional[str] = None,
    hotspots: Optional[str] = None,
    target_repr: str = "surface",
    target_color: str = "ipd_target_sand",
    binder_color: str = "ipd_pastel_lavender",
    show_interface_sticks: bool = False,
    zoom_interface: bool = False,
    cylindrical_helices: bool = False,
    width: int = 2000,
    height: int = 1600,
    dpi: int = 300,
    use_ray: bool = True,
) -> Tuple[str, str, str]:
    """Render a target-binder complex in RFdiffusion 1 Fig 6 / RFD-beta style."""
    pml: List[str] = ["# Baker Lab / IPD Style: Target-Binder Complex"]
    apply_ipd_theme(cmd, cylindrical_helices=cylindrical_helices, pml_lines=pml)

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

    # Target representation
    if target_repr in ("surface", "both"):
        cmd.show("surface", target_sel)
        cmd.set("surface_color", target_color, target_sel)
        _rec(pml, f"show surface, {target_sel}\nset surface_color, {target_color}, {target_sel}")
        if target_repr == "both":
            cmd.set("transparency", 0.35, target_sel)
            cmd.show("cartoon", target_sel)
            cmd.color(target_color, target_sel)
            _rec(pml, f"set transparency, 0.35, {target_sel}\nshow cartoon, {target_sel}\ncolor {target_color}, {target_sel}")
    else:
        cmd.show("cartoon", target_sel)
        cmd.color(target_color, target_sel)
        _rec(pml, f"show cartoon, {target_sel}\ncolor {target_color}, {target_sel}")

    # Hotspot coloring on target
    if hotspots:
        hs_sel = f"({target_sel}) and ({hotspots})"
        cmd.color("ipd_hotspot_orange", hs_sel)
        cmd.set("surface_color", "ipd_hotspot_orange", hs_sel)
        _rec(pml, f"color ipd_hotspot_orange, {hs_sel}\nset surface_color, ipd_hotspot_orange, {hs_sel}")

    # Binder representation
    cmd.show("cartoon", binder_sel)
    _rec(pml, f"show cartoon, {binder_sel}")
    if binder_color == "spectrum":
        color_ipd_spectrum(cmd, binder_sel, palette_mode="rfd1", pml_lines=pml)
    else:
        cmd.color(binder_color, binder_sel)
        _rec(pml, f"color {binder_color}, {binder_sel}")

    # Optional reference binder overlay (e.g., crystal/AF2 structure)
    if reference_binder:
        verify_and_load(cmd, reference_binder, "ref_binder", pml_lines=pml)
        ensure_cartoon_trace(cmd, "ref_binder", pml_lines=pml)
        cmd.show("cartoon", "ref_binder and polymer.protein")
        method, rmsd, n_aligned = align_structures(cmd, "ref_binder", binder_sel, pml_lines=pml)
        print(f"Binder Alignment ({method}): RMSD = {rmsd:.3f} A over {n_aligned} atoms")
        cmd.color("ipd_model_gray", "ref_binder")
        _rec(pml, "show cartoon, ref_binder and polymer.protein\ncolor ipd_model_gray, ref_binder")

    # Optional interface sticks & H-bond dashes
    if show_interface_sticks or zoom_interface:
        cmd.select("iface_binder", f"byres (({binder_sel}) within 4.0 of ({target_sel}))")
        cmd.select("iface_target", f"byres (({target_sel}) within 4.0 of ({binder_sel}))")
        cmd.show("sticks", "(iface_binder or iface_target) and not name C+O+N")
        cmd.util.cnc("iface_binder or iface_target")
        cmd.distance("iface_hbonds", "iface_binder", "iface_target", cutoff=3.5, mode=2)
        cmd.set("dash_color", "white")
        cmd.hide("labels", "iface_hbonds")
        _rec(
            pml,
            f"select iface_binder, byres (({binder_sel}) within 4.0 of ({target_sel}))\n"
            f"select iface_target, byres (({target_sel}) within 4.0 of ({binder_sel}))\n"
            "show sticks, (iface_binder or iface_target) and not name C+O+N\n"
            "util.cnc iface_binder or iface_target\n"
            "distance iface_hbonds, iface_binder, iface_target, cutoff=3.5, mode=2\n"
            "set dash_color, white\nhide labels, iface_hbonds",
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
    reference_asu: Optional[str] = None,
    motif_sele: Optional[str] = None,
    metal_sele: Optional[str] = None,
    em_map: Optional[str] = None,
    em_contour: float = 1.5,
    view: str = "single",
    cylindrical_helices: bool = False,
    width: int = 2000,
    height: int = 2000,
    dpi: int = 300,
    use_ray: bool = True,
) -> List[Tuple[str, str, str]]:
    """Render symmetric oligomers (C_n / D_n / cages) with optional EM density envelope."""
    pml: List[str] = ["# Baker Lab / IPD Style: Symmetric Oligomer"]
    apply_ipd_theme(cmd, cylindrical_helices=cylindrical_helices, pml_lines=pml)

    verify_and_load(cmd, structure, "oligomer", pml_lines=pml)
    ensure_cartoon_trace(cmd, "oligomer", pml_lines=pml)

    cmd.hide("everything", "all")
    cmd.show("cartoon", "oligomer and polymer.protein")
    _rec(pml, "hide everything, all\nshow cartoon, oligomer and polymer.protein")

    chains = cmd.get_chains("oligomer")
    print(f"Oligomer chains ({len(chains)}): {', '.join(chains)}")
    for idx, ch in enumerate(chains):
        col = OLIGOMER_CHAIN_CYCLE[idx % len(OLIGOMER_CHAIN_CYCLE)]
        cmd.color(col, f"oligomer and chain {ch}")
        _rec(pml, f"color {col}, oligomer and chain {ch}")

    if reference_asu:
        verify_and_load(cmd, reference_asu, "ref_asu", pml_lines=pml)
        ensure_cartoon_trace(cmd, "ref_asu", pml_lines=pml)
        first_chain = chains[0]
        method, rmsd, n_aligned = align_structures(
            cmd, "ref_asu", f"oligomer and chain {first_chain}", pml_lines=pml
        )
        print(f"ASU Alignment ({method}): RMSD = {rmsd:.3f} A over {n_aligned} atoms")
        cmd.show("cartoon", "ref_asu and polymer.protein")
        cmd.color("ipd_model_gray", "ref_asu")
        _rec(pml, "show cartoon, ref_asu and polymer.protein\ncolor ipd_model_gray, ref_asu")

    if motif_sele:
        cmd.select("sym_motif", f"oligomer and ({motif_sele})")
        cmd.color("ipd_motif_teal", "sym_motif")
        cmd.show("sticks", "sym_motif and not name C+O+N")
        cmd.util.cnc("sym_motif")
        _rec(
            pml,
            f"select sym_motif, oligomer and ({motif_sele})\n"
            "color ipd_motif_teal, sym_motif\n"
            "show sticks, sym_motif and not name C+O+N\n"
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
    reference: Optional[str] = None,
    catalytic_sele: Optional[str] = None,
    ligand_sele: str = "organic",
    metal_sele: str = "resn MG+ZN+FE+MN+CU+NI+CO+CA",
    scaffold_transparency: float = 0.55,
    zoom_buffer: float = 6.0,
    cylindrical_helices: bool = False,
    width: int = 2000,
    height: int = 1600,
    dpi: int = 300,
    use_ray: bool = True,
) -> Tuple[str, str, str]:
    """Render an RFdiffusion 2 / 3 all-atom enzyme active site, ligand, or DNA pocket."""
    pml: List[str] = ["# Baker Lab / IPD Style: All-Atom Active Site & Ligand Pocket"]
    apply_ipd_theme(cmd, cylindrical_helices=cylindrical_helices, pml_lines=pml)

    verify_and_load(cmd, structure, "enzyme", pml_lines=pml)
    ensure_cartoon_trace(cmd, "enzyme", pml_lines=pml)

    cmd.hide("everything", "all")
    cmd.show("cartoon", "enzyme and polymer.protein")
    color_ipd_spectrum(cmd, "enzyme", palette_mode="rfd2", pml_lines=pml)
    cmd.set("cartoon_transparency", scaffold_transparency, "enzyme and polymer.protein")
    _rec(
        pml,
        "hide everything, all\n"
        "show cartoon, enzyme and polymer.protein\n"
        f"set cartoon_transparency, {scaffold_transparency}, enzyme and polymer.protein",
    )

    # Nucleic acids if present (RFD3 DNA-binding designs)
    if cmd.count_atoms("enzyme and polymer.nucleic") > 0:
        cmd.show("cartoon", "enzyme and polymer.nucleic")
        cmd.show("sticks", "enzyme and polymer.nucleic")
        cmd.color("ipd_pastel_iceblue", "enzyme and polymer.nucleic")
        cmd.util.cnc("enzyme and polymer.nucleic")
        _rec(
            pml,
            "show cartoon, enzyme and polymer.nucleic\n"
            "show sticks, enzyme and polymer.nucleic\n"
            "color ipd_pastel_iceblue, enzyme and polymer.nucleic\n"
            "util.cnc enzyme and polymer.nucleic",
        )

    if reference:
        verify_and_load(cmd, reference, "ref_pred", pml_lines=pml)
        ensure_cartoon_trace(cmd, "ref_pred", pml_lines=pml)
        method, rmsd, n_aligned = align_structures(cmd, "ref_pred", "enzyme", pml_lines=pml)
        print(f"Active-Site Alignment ({method}): RMSD = {rmsd:.3f} A over {n_aligned} atoms")
        cmd.show("cartoon", "ref_pred and polymer.protein")
        cmd.color("ipd_model_gray", "ref_pred")
        cmd.set("cartoon_transparency", min(0.75, scaffold_transparency + 0.15), "ref_pred")
        _rec(
            pml,
            "show cartoon, ref_pred and polymer.protein\n"
            "color ipd_model_gray, ref_pred\n"
            f"set cartoon_transparency, {min(0.75, scaffold_transparency + 0.15)}, ref_pred",
        )

    focus_parts: List[str] = []

    if catalytic_sele and cmd.count_atoms(f"enzyme and ({catalytic_sele})") > 0:
        cmd.select("catalytic_res", f"enzyme and ({catalytic_sele})")
        cmd.show("sticks", "catalytic_res and not name C+O")
        cmd.hide("sticks", "catalytic_res and hydro")
        # Non-motif backbone/CB connector in slate gray; functional sidechain in signature IPD teal
        cmd.color("ipd_slate_gray", "catalytic_res and name CA+CB+N+C+O")
        cmd.color("ipd_motif_teal", "catalytic_res and not name CA+CB+N+C+O")
        cmd.util.cnc("catalytic_res")
        focus_parts.append("catalytic_res")
        _rec(
            pml,
            f"select catalytic_res, enzyme and ({catalytic_sele})\n"
            "show sticks, catalytic_res and not name C+O\n"
            "hide sticks, catalytic_res and hydro\n"
            "color ipd_slate_gray, catalytic_res and name CA+CB+N+C+O\n"
            "color ipd_motif_teal, catalytic_res and not name CA+CB+N+C+O\n"
            "util.cnc catalytic_res",
        )

    if ligand_sele and cmd.count_atoms(f"enzyme and ({ligand_sele})") > 0:
        cmd.select("active_ligand", f"enzyme and ({ligand_sele})")
        cmd.show("sticks", "active_ligand")
        cmd.hide("sticks", "active_ligand and hydro")
        cmd.color("ipd_ligand_carbon", "active_ligand")
        cmd.util.cnc("active_ligand")
        focus_parts.append("active_ligand")
        _rec(
            pml,
            f"select active_ligand, enzyme and ({ligand_sele})\n"
            "show sticks, active_ligand\n"
            "hide sticks, active_ligand and hydro\n"
            "color ipd_ligand_carbon, active_ligand\n"
            "util.cnc active_ligand",
        )

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
