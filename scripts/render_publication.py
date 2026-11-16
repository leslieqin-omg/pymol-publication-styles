# /// script
# requires-python = ">=3.10, <3.14"
# dependencies = [
#     "pymol-open-source-whl",
#     "pillow",
# ]
# ///
"""
CLI entrypoint for rendering publication-quality PyMOL figures across 10 styles:
  baker_rfd, goodsell, cylindrical, chimerax_soft, spotlight, alphafold_plddt,
  antibody_cdr, hydrophobic_surface, pocket_cavity, diffusion_ensemble

Subcommands:
  monomer | binder | oligomer | active_site | antibody | ligand_pocket | trajectory_strip | showcase
"""

from __future__ import annotations

import argparse
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from publication_style import CORE_SHOWCASE_STYLES, VALID_STYLES  # noqa: E402


def _launch_pymol():
    if sys.platform.startswith("linux") and "PYOPENGL_PLATFORM" not in os.environ:
        os.environ["PYOPENGL_PLATFORM"] = "osmesa"

    import pymol  # type: ignore

    pymol.pymol_argv = ["pymol", "-cq"]
    pymol.finish_launching()
    from pymol import cmd  # type: ignore

    return cmd


def _add_common_args(parser: argparse.ArgumentParser, default_style: str = "baker_rfd", include_style: bool = True) -> None:
    if include_style:
        parser.add_argument(
            "--style",
            choices=list(VALID_STYLES),
            default=default_style,
            help=f"Publication visual style preset (default: {default_style})",
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
    parser.add_argument("--transparent", action="store_true", help="Render PNG with transparent background")
    parser.add_argument("--auto-crop", action="store_true", help="Auto-trim whitespace/alpha margins around structure")
    parser.add_argument("--crop-padding", type=int, default=24, help="Pixel padding when --auto-crop is set (default: 24)")
    parser.add_argument("--no-ray", action="store_true", help="Skip ray-tracing for quick previews")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Render protein structures in 10 classic publication & AIDD PyMOL styles."
    )
    sub = parser.add_subparsers(dest="mode", required=True)

    # 1. Monomer / Overlay / Motif
    p_mono = sub.add_parser("monomer", help="Monomer, motif scaffolding, or AF2/crystal overlay")
    p_mono.add_argument("--structure", required=True, help="Path to structure (.pdb / .cif)")
    p_mono.add_argument("--reference", help="Optional AF2/AF3/crystal structure to superimpose")
    p_mono.add_argument("--motif-sele", help="Optional PyMOL selection for functional motif / focal site")
    p_mono.add_argument("--color-mode", choices=["spectrum", "solid", "chain"], default="spectrum")
    p_mono.add_argument("--design-role", choices=["gray", "colored"], default="gray")
    p_mono.add_argument("--palette", choices=["rfd1", "rfd2"], default="rfd1")
    _add_common_args(p_mono)

    # 2. Binder / Target Complex
    p_bind = sub.add_parser("binder", help="Target-binder complex with hotspots, hydrophobic patches & inset zoom")
    p_bind.add_argument("--complex", required=True, help="Path to complex structure (.pdb / .cif)")
    p_bind.add_argument("--target-chain", required=True, help="Chain ID of target protein")
    p_bind.add_argument("--binder-chain", required=True, help="Chain ID of binder protein")
    p_bind.add_argument("--reference-binder", help="Optional crystal/AF2 binder structure to overlay")
    p_bind.add_argument("--hotspots", help="PyMOL selection on target chain (e.g. 'resi 45+48+52')")
    p_bind.add_argument("--target-repr", choices=["surface", "cartoon", "both"], default="surface")
    p_bind.add_argument("--target-color", default=None, help="Override target color name")
    p_bind.add_argument("--binder-color", default=None, help="Override binder color name or 'spectrum'")
    p_bind.add_argument("--show-interface-sticks", action="store_true", help="Show interface sticks and H-bonds")
    p_bind.add_argument("--zoom-interface", action="store_true", help="Zoom into the binding interface")
    p_bind.add_argument("--with-inset", action="store_true", help="Generate global + inset zoom composite")
    _add_common_args(p_bind)

    # 3. Symmetric Oligomer
    p_olig = sub.add_parser("oligomer", help="Symmetric oligomers (Cn / Dn / cages) and optional EM map")
    p_olig.add_argument("--structure", required=True, help="Path to oligomer structure (.pdb / .cif)")
    p_olig.add_argument("--reference-asu", help="Optional AF2 asymmetric unit to overlay on chain 1")
    p_olig.add_argument("--motif-sele", help="Optional symmetric motif selection")
    p_olig.add_argument("--metal-sele", default="resn NI+ZN+FE+MG+CA+MN+CU+CO")
    p_olig.add_argument("--em-map", help="Optional cryo-EM/nsEM density map (.mrc / .ccp4)")
    p_olig.add_argument("--em-contour", type=float, default=1.5)
    p_olig.add_argument("--view", choices=["single", "side", "both"], default="single")
    _add_common_args(p_olig)

    # 4. Active Site / All-Atom Enzyme / Ligand / DNA Pocket
    p_act = sub.add_parser("active_site", help="Enzyme active site, ligand pocket, or DNA complex")
    p_act.add_argument("--structure", required=True, help="Path to enzyme/complex structure (.pdb / .cif)")
    p_act.add_argument("--reference", help="Optional AF3/Chai-1/crystal structure overlay")
    p_act.add_argument("--catalytic-sele", help="Catalytic residues selection (e.g. 'resi 27+36+59')")
    p_act.add_argument("--ligand-sele", default="organic", help="Ligand/substrate selection (default: organic)")
    p_act.add_argument("--metal-sele", default="resn MG+ZN+FE+MN+CU+NI+CO+CA")
    p_act.add_argument("--scaffold-transparency", type=float, default=None)
    p_act.add_argument("--zoom-buffer", type=float, default=6.0)
    p_act.add_argument("--with-inset", action="store_true", help="Generate global + inset zoom composite")
    _add_common_args(p_act)

    # 5. Antibody CDR + Epitope Footprint
    p_ab = sub.add_parser("antibody", help="Antibody/nanobody CDR loop colors + 4.5 A epitope footprint")
    p_ab.add_argument("--complex", required=True, help="Path to antibody-antigen complex (.pdb / .cif)")
    p_ab.add_argument("--antigen-chain", required=True, help="Chain ID of antigen")
    p_ab.add_argument("--heavy-chain", required=True, help="Chain ID of heavy chain / VHH")
    p_ab.add_argument("--light-chain", help="Optional chain ID of light chain")
    p_ab.add_argument("--cdr-h1", default="26-35", help="CDR-H1 residue range (default: 26-35)")
    p_ab.add_argument("--cdr-h2", default="50-65", help="CDR-H2 residue range (default: 50-65)")
    p_ab.add_argument("--cdr-h3", default="95-102", help="CDR-H3 residue range (default: 95-102)")
    p_ab.add_argument("--cdr-l1", default="24-34", help="CDR-L1 residue range (default: 24-34)")
    p_ab.add_argument("--cdr-l2", default="50-56", help="CDR-L2 residue range (default: 50-56)")
    p_ab.add_argument("--cdr-l3", default="89-97", help="CDR-L3 residue range (default: 89-97)")
    p_ab.add_argument("--footprint-cutoff", type=float, default=4.5, help="Epitope projection cutoff in A (default: 4.5)")
    p_ab.add_argument("--with-inset", action="store_true", help="Generate global + CDR interface inset composite")
    _add_common_args(p_ab, default_style="antibody_cdr")

    # 6. Local Ligand Pocket Cutaway & In-Pocket Ligand RMSD
    p_pkt = sub.add_parser("ligand_pocket", help="Local cutaway pocket cavity + in-pocket ligand RMSD")
    p_pkt.add_argument("--structure", required=True, help="Path to protein-ligand complex (.pdb / .cif)")
    p_pkt.add_argument("--reference", help="Optional reference crystal/co-fold complex to overlay and score RMSD")
    p_pkt.add_argument("--ligand-sele", default="organic", help="Ligand selection in primary structure (default: organic)")
    p_pkt.add_argument("--ref-ligand-sele", help="Optional ligand selection in reference (defaults to --ligand-sele)")
    p_pkt.add_argument("--pocket-radius", type=float, default=6.0, help="Local pocket surface radius in A (default: 6.0)")
    p_pkt.add_argument("--with-inset", action="store_true", help="Generate global + pocket inset composite")
    _add_common_args(p_pkt, default_style="pocket_cavity")

    # 7. Diffusion / MD Trajectory Strip
    p_traj = sub.add_parser("trajectory_strip", help="Horizontal time-step strip from multi-state or frame PDBs")
    p_traj.add_argument("--structure", help="Multi-state trajectory PDB/CIF")
    p_traj.add_argument("--structures", help="Comma-separated frame PDB/CIF paths")
    p_traj.add_argument("--n-frames", type=int, default=5, help="Number of frames to sample (default: 5)")
    _add_common_args(p_traj, default_style="baker_rfd")

    # 8. Multi-Style Showcase Grid
    p_show = sub.add_parser("showcase", help="Render the same view across multiple styles into a comparison grid")
    p_show.add_argument("--structure", required=True, help="Path to structure (.pdb / .cif)")
    p_show.add_argument("--scene", choices=["monomer", "binder", "oligomer", "active_site"], default="monomer", help="Scene layout to render across styles")
    p_show.add_argument("--styles", help="Comma-separated style names (default: 6 core styles)")
    p_show.add_argument("--all-styles", action="store_true", help="Include all 10 styles in the grid")
    p_show.add_argument("--target-chain", help="Target chain (for --scene binder)")
    p_show.add_argument("--binder-chain", help="Binder chain (for --scene binder)")
    p_show.add_argument("--hotspots", help="Hotspots (for --scene binder)")
    p_show.add_argument("--catalytic-sele", help="Catalytic residues (for --scene active_site)")
    p_show.add_argument("--ligand-sele", default="organic", help="Ligand selection (for --scene active_site)")
    _add_common_args(p_show, include_style=False)

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
                transparent=args.transparent,
                auto_crop=args.auto_crop,
                crop_padding=args.crop_padding,
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
                with_inset=args.with_inset,
                cylindrical_helices=args.cylindrical_helices,
                width=args.width,
                height=args.height,
                dpi=args.dpi,
                use_ray=use_ray,
                transparent=args.transparent,
                auto_crop=args.auto_crop,
                crop_padding=args.crop_padding,
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
                transparent=args.transparent,
                auto_crop=args.auto_crop,
                crop_padding=args.crop_padding,
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
                with_inset=args.with_inset,
                cylindrical_helices=args.cylindrical_helices,
                width=args.width,
                height=args.height,
                dpi=args.dpi,
                use_ray=use_ray,
                transparent=args.transparent,
                auto_crop=args.auto_crop,
                crop_padding=args.crop_padding,
            )
            print("Rendered:", out)
        elif args.mode == "antibody":
            out = publication_style.render_antibody(
                cmd,
                complex_path=args.complex,
                antigen_chain=args.antigen_chain,
                heavy_chain=args.heavy_chain,
                light_chain=args.light_chain,
                out_prefix=args.out_prefix,
                style=args.style,
                cdr_h1=args.cdr_h1,
                cdr_h2=args.cdr_h2,
                cdr_h3=args.cdr_h3,
                cdr_l1=args.cdr_l1,
                cdr_l2=args.cdr_l2,
                cdr_l3=args.cdr_l3,
                footprint_cutoff=args.footprint_cutoff,
                with_inset=args.with_inset,
                cylindrical_helices=args.cylindrical_helices,
                width=args.width,
                height=args.height,
                dpi=args.dpi,
                use_ray=use_ray,
                transparent=args.transparent,
                auto_crop=args.auto_crop,
                crop_padding=args.crop_padding,
            )
            print("Rendered:", out)
        elif args.mode == "ligand_pocket":
            out = publication_style.render_ligand_pocket(
                cmd,
                structure=args.structure,
                out_prefix=args.out_prefix,
                style=args.style,
                reference=args.reference,
                ligand_sele=args.ligand_sele,
                ref_ligand_sele=args.ref_ligand_sele,
                pocket_radius=args.pocket_radius,
                with_inset=args.with_inset,
                cylindrical_helices=args.cylindrical_helices,
                width=args.width,
                height=args.height,
                dpi=args.dpi,
                use_ray=use_ray,
                transparent=args.transparent,
                auto_crop=args.auto_crop,
                crop_padding=args.crop_padding,
            )
            print("Rendered:", out)
        elif args.mode == "trajectory_strip":
            struct_list = [s.strip() for s in args.structures.split(",") if s.strip()] if args.structures else None
            out = publication_style.render_trajectory_strip(
                cmd,
                out_prefix=args.out_prefix,
                structure=args.structure,
                structures=struct_list,
                n_frames=args.n_frames,
                style=args.style,
                cylindrical_helices=args.cylindrical_helices,
                width=args.width,
                height=args.height,
                dpi=args.dpi,
                use_ray=use_ray,
                transparent=args.transparent,
            )
            print("Rendered:", out)
        elif args.mode == "showcase":
            if args.all_styles:
                style_list = list(VALID_STYLES)
            elif args.styles:
                style_list = [s.strip() for s in args.styles.split(",") if s.strip()]
            else:
                style_list = list(CORE_SHOWCASE_STYLES)
            out = publication_style.render_showcase(
                cmd,
                structure=args.structure,
                out_prefix=args.out_prefix,
                mode=args.scene,
                styles=style_list,
                target_chain=args.target_chain,
                binder_chain=args.binder_chain,
                hotspots=args.hotspots,
                catalytic_sele=args.catalytic_sele,
                ligand_sele=args.ligand_sele,
                cell_width=min(1200, args.width),
                cell_height=min(1000, args.height),
                dpi=min(200, args.dpi),
                use_ray=use_ray,
            )
            print("Rendered:", out)
    finally:
        cmd.quit()


if __name__ == "__main__":
    main()
