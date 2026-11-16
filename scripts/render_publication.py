# /// script
# requires-python = ">=3.10, <3.14"
# dependencies = [
#     "pymol-open-source-whl",
# ]
# ///
"""
CLI entrypoint for rendering publication-quality PyMOL figures across 6 styles:
  baker_rfd, goodsell, cylindrical, chimerax_soft, spotlight, alphafold_plddt

Run with local Python (if PyMOL is installed) or via `uv run`:
  python3 render_publication.py <mode> [--style <style>] [options]
  uv run render_publication.py <mode> [--style <style>] [options]
"""

from __future__ import annotations

import argparse
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from publication_style import VALID_STYLES  # noqa: E402


def _launch_pymol():
    if sys.platform.startswith("linux") and "PYOPENGL_PLATFORM" not in os.environ:
        os.environ["PYOPENGL_PLATFORM"] = "osmesa"

    import pymol  # type: ignore

    pymol.pymol_argv = ["pymol", "-cq"]
    pymol.finish_launching()
    from pymol import cmd  # type: ignore

    return cmd


def _add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--style",
        choices=list(VALID_STYLES),
        default="baker_rfd",
        help="Publication visual style preset (default: baker_rfd)",
    )
    parser.add_argument("--out-prefix", required=True, help="Output prefix for .png, .pse, and .pml")
    parser.add_argument("--width", type=int, default=2000, help="Image width in pixels (default: 2000)")
    parser.add_argument("--height", type=int, default=1600, help="Image height in pixels (default: 1600)")
    parser.add_argument("--dpi", type=int, default=300, help="Image DPI metadata (default: 300)")
    parser.add_argument(
        "--cylindrical-helices",
        action="store_true",
        default=None,
        help="Force cylindrical alpha-helices on (cartoon_cylindrical_helices=1)",
    )
    parser.add_argument(
        "--no-ray",
        action="store_true",
        help="Skip ray-tracing for quick previews",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Render protein structures in 6 classic publication-grade PyMOL styles."
    )
    sub = parser.add_subparsers(dest="mode", required=True)

    # 1. Monomer / Overlay / Motif
    p_mono = sub.add_parser("monomer", help="Monomer, motif scaffolding, or AF2/crystal overlay")
    p_mono.add_argument("--structure", required=True, help="Path to structure (.pdb / .cif)")
    p_mono.add_argument("--reference", help="Optional AF2/AF3/crystal structure to superimpose")
    p_mono.add_argument("--motif-sele", help="Optional PyMOL selection for functional motif / focal site")
    p_mono.add_argument(
        "--color-mode",
        choices=["spectrum", "solid", "chain"],
        default="spectrum",
        help="Coloring mode when no reference is given (default: spectrum)",
    )
    p_mono.add_argument(
        "--design-role",
        choices=["gray", "colored"],
        default="gray",
        help="When --reference is given: 'gray' (RFD1 style) or 'colored' (RFD2 style)",
    )
    p_mono.add_argument(
        "--palette",
        choices=["rfd1", "rfd2"],
        default="rfd1",
        help="Pastel gradient stop set for baker_rfd style (default: rfd1)",
    )
    _add_common_args(p_mono)

    # 2. Binder / Target Complex
    p_bind = sub.add_parser("binder", help="Target-binder complex with optional hotspots & interface zoom")
    p_bind.add_argument("--complex", required=True, help="Path to complex structure (.pdb / .cif)")
    p_bind.add_argument("--target-chain", required=True, help="Chain ID of target protein")
    p_bind.add_argument("--binder-chain", required=True, help="Chain ID of binder protein")
    p_bind.add_argument("--reference-binder", help="Optional crystal/AF2 binder structure to overlay in gray")
    p_bind.add_argument("--hotspots", help="PyMOL selection on target chain (e.g. 'resi 45+48+52')")
    p_bind.add_argument(
        "--target-repr",
        choices=["surface", "cartoon", "both"],
        default="surface",
        help="Target representation (default: surface)",
    )
    p_bind.add_argument("--target-color", default=None, help="Override target color name")
    p_bind.add_argument("--binder-color", default=None, help="Override binder color name or 'spectrum'")
    p_bind.add_argument("--show-interface-sticks", action="store_true", help="Show interface sticks and H-bonds")
    p_bind.add_argument("--zoom-interface", action="store_true", help="Zoom into the binding interface")
    _add_common_args(p_bind)

    # 3. Symmetric Oligomer
    p_olig = sub.add_parser("oligomer", help="Symmetric oligomers (Cn / Dn / cages) and optional EM map")
    p_olig.add_argument("--structure", required=True, help="Path to oligomer structure (.pdb / .cif)")
    p_olig.add_argument("--reference-asu", help="Optional AF2 asymmetric unit to overlay on chain 1")
    p_olig.add_argument("--motif-sele", help="Optional symmetric motif selection")
    p_olig.add_argument(
        "--metal-sele",
        default="resn NI+ZN+FE+MG+CA+MN+CU+CO",
        help="Metal ion selection",
    )
    p_olig.add_argument("--em-map", help="Optional cryo-EM/nsEM density map (.mrc / .ccp4)")
    p_olig.add_argument("--em-contour", type=float, default=1.5, help="EM map contour level (default: 1.5)")
    p_olig.add_argument("--view", choices=["single", "side", "both"], default="single", help="Camera views")
    _add_common_args(p_olig)

    # 4. Active Site / All-Atom Enzyme / Ligand / DNA Pocket
    p_act = sub.add_parser("active_site", help="Enzyme active site, ligand pocket, or DNA complex")
    p_act.add_argument("--structure", required=True, help="Path to enzyme/complex structure (.pdb / .cif)")
    p_act.add_argument("--reference", help="Optional AF3/Chai-1/crystal structure overlay")
    p_act.add_argument("--catalytic-sele", help="Catalytic residues selection (e.g. 'resi 27+36+59')")
    p_act.add_argument("--ligand-sele", default="organic", help="Ligand/substrate selection (default: organic)")
    p_act.add_argument(
        "--metal-sele",
        default="resn MG+ZN+FE+MN+CU+NI+CO+CA",
        help="Metal cofactor selection",
    )
    p_act.add_argument(
        "--scaffold-transparency",
        type=float,
        default=None,
        help="Override cartoon transparency of protein scaffold",
    )
    p_act.add_argument("--zoom-buffer", type=float, default=6.0, help="Zoom buffer in Angstroms (default: 6.0)")
    _add_common_args(p_act)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    import publication_style

    cmd = _launch_pymol()
    use_ray = not args.no_ray
    try:
        if args.mode == "monomer":
            out = publication_style.render_monomer(
                cmd,
                structure=args.structure,
                out_prefix=args.out_prefix,
                style=args.style,
                reference=args.reference,
                motif_sele=args.motif_sele,
                color_mode=args.color_mode,
                design_role=args.design_role,
                palette_mode=args.palette,
                cylindrical_helices=args.cylindrical_helices,
                width=args.width,
                height=args.height,
                dpi=args.dpi,
                use_ray=use_ray,
            )
            print("Rendered:", out)
        elif args.mode == "binder":
            out = publication_style.render_binder(
                cmd,
                complex_path=args.complex,
                target_chain=args.target_chain,
                binder_chain=args.binder_chain,
                out_prefix=args.out_prefix,
                style=args.style,
                reference_binder=args.reference_binder,
                hotspots=args.hotspots,
                target_repr=args.target_repr,
                target_color=args.target_color,
                binder_color=args.binder_color,
                show_interface_sticks=args.show_interface_sticks,
                zoom_interface=args.zoom_interface,
                cylindrical_helices=args.cylindrical_helices,
                width=args.width,
                height=args.height,
                dpi=args.dpi,
                use_ray=use_ray,
            )
            print("Rendered:", out)
        elif args.mode == "oligomer":
            outs = publication_style.render_oligomer(
                cmd,
                structure=args.structure,
                out_prefix=args.out_prefix,
                style=args.style,
                reference_asu=args.reference_asu,
                motif_sele=args.motif_sele,
                metal_sele=args.metal_sele,
                em_map=args.em_map,
                em_contour=args.em_contour,
                view=args.view,
                cylindrical_helices=args.cylindrical_helices,
                width=args.width,
                height=args.height,
                dpi=args.dpi,
                use_ray=use_ray,
            )
            print("Rendered:", outs)
        elif args.mode == "active_site":
            out = publication_style.render_active_site(
                cmd,
                structure=args.structure,
                out_prefix=args.out_prefix,
                style=args.style,
                reference=args.reference,
                catalytic_sele=args.catalytic_sele,
                ligand_sele=args.ligand_sele,
                metal_sele=args.metal_sele,
                scaffold_transparency=args.scaffold_transparency,
                zoom_buffer=args.zoom_buffer,
                cylindrical_helices=args.cylindrical_helices,
                width=args.width,
                height=args.height,
                dpi=args.dpi,
                use_ray=use_ray,
            )
            print("Rendered:", out)
    finally:
        cmd.quit()


if __name__ == "__main__":
    main()
