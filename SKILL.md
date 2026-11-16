---
name: pymol-publication-styles
description: >
  Use when rendering publication-quality protein, binder, antibody CDR,
  ligand pocket, oligomer, cryo-EM, or diffusion trajectory structure figures
  in PyMOL across ten classic and AIDD styles (baker_rfd, goodsell, cylindrical,
  chimerax_soft, spotlight, alphafold_plddt, antibody_cdr, hydrophobic_surface,
  pocket_cavity, diffusion_ensemble), with auto-crop, transparent PNG,
  global+inset composites, in-pocket ligand RMSD, trajectory strips, and
  multi-style showcase grids.
---

# PyMOL Publication Styles

Render biomolecular and AIDD structures in **10 publication-grade PyMOL styles**
across **8 automated figure workflows**, compatible with Antigravity, Claude Code,
and OpenAI Codex CLI.

## Available Styles (`--style`)

| `--style` | Aesthetic Inspiration | Best Used For |
|---|---|---|
| `baker_rfd` *(default)* | Baker Lab / IPD RFdiffusion 1–3 (*Nature* 2023, *Science* 2024, *Nat Methods* 2025, *bioRxiv* 2025) | De novo binders, monomers, symmetric oligomers, RFD2/RFD3 all-atom active sites (avoids RFD4 style) |
| `goodsell` | David Goodsell / RCSB *Molecule of the Month* | Space-filling full-atom complexes, macromolecular assemblies, textbook watercolor illustrations |
| `cylindrical` | *Nature* / *Cell* cylindrical-helix architectural figures | Membrane proteins, GPCRs, ion channels, multi-helix bundles, topology overviews |
| `chimerax_soft` | ChimeraX `soft` ambient-occlusion lighting | Cryo-EM density maps, outline-free matte ceramic surfaces, epitope complexes |
| `spotlight` | Monochrome ghost scaffold + jewel-tone spotlight | Enzyme active sites, drug-binding pockets, disease mutation highlights |
| `alphafold_plddt` | Canonical AlphaFold / ColabFold confidence palette | Structure prediction confidence (pLDDT $\ge 90, 70, 50, <50$) |
| `antibody_cdr` | RFantibody / AbDiffuser / DiffAb CDR & epitope style | Antibody/VHH frameworks, color-coded CDR-H1/H2/H3 & L1/L2/L3 loops, 4.5 Å epitope footprints |
| `hydrophobic_surface` | MaSIF / BindCraft physicochemical complementarity | Eisenberg hydrophobicity target surface + hydrophobic binder anchor sidechains |
| `pocket_cavity` | DiffSBDD / TargetDiff / AF3 / Boltz ligand pocket style | Local cutaway pocket surface + dual-color pose overlay + in-pocket ligand RMSD |
| `diffusion_ensemble` | RFdiffusion / AlphaFlow trajectory & ensemble ghosting | Multi-state ghosted trajectories or B-factor/RMSF `putty` flexibility cartoons |

**Never** use PyMOL's default glossy primary colors (`green`, `red`, `magenta`, `rainbow`) or RFdiffusion 4's harsh palette.

## Prerequisites & Execution

Let `<SKILL_DIR>` be the directory containing this `SKILL.md` file (e.g., `~/.gemini/config/skills/pymol-publication-styles`, `~/.claude/skills/pymol-publication-styles`, or `~/.codex/skills/pymol-publication-styles`).

1. **Local PyMOL or `uv`**:
   - If local `python3` has `pymol` installed, run `python3 <SKILL_DIR>/scripts/render_publication.py ...`.
   - Otherwise, run with `uv run <SKILL_DIR>/scripts/render_publication.py ...` (PEP 723 installs `pymol-open-source-whl` and `pillow`; `PYOPENGL_PLATFORM=osmesa` is set automatically on Linux).
2. **License Notice**: If `.licenses/pymol_LICENSE.txt` does not exist in the working directory, remind the user to check the PyMOL license at `https://www.pymol.org/`.

## Universal Figure-Automation Flags

Every subcommand supports:
- `--transparent`: Render transparent PNG (`ray_opaque_background=0`) for drag-and-drop BioRender / Illustrator / PPT layouts.
- `--auto-crop` (`--crop-padding 24`): Trim excess empty alpha or white margin around the structure.
- `--with-inset` (available on `binder`, `active_site`, `antibody`, `ligand_pocket`): Renders `<prefix>_global.png`, `<prefix>_inset.png`, and a side-by-side framed composite `<prefix>_composite.png`.
- **Triple Output Contract**: Single-view renders always emit `<prefix>.png`, `<prefix>.pse` (interactive PyMOL session), and `<prefix>.pml` (standalone PyMOL script).

## Subcommands (`scripts/render_publication.py`)

### 1. Monomer, Overlay, & Ensemble (`monomer`)
```bash
python3 <SKILL_DIR>/scripts/render_publication.py monomer \
  --style baker_rfd \
  --structure design.cif \
  [--reference af2.cif] [--motif-sele "resi 20-35"] \
  --out-prefix output/monomer
```

### 2. Target–Binder Complex & Hydrophobic Complementarity (`binder`)
```bash
python3 <SKILL_DIR>/scripts/render_publication.py binder \
  --style hydrophobic_surface \
  --complex complex.cif --target-chain C --binder-chain K \
  --with-inset --transparent --auto-crop \
  --out-prefix output/binder_hydro
```

### 3. Symmetric Oligomers & Cryo-EM Maps (`oligomer`)
```bash
python3 <SKILL_DIR>/scripts/render_publication.py oligomer \
  --style baker_rfd --structure c4_assembly.cif \
  --motif-sele "resn HIS and resi 52" --view both \
  --out-prefix output/oligomer
```

### 4. Enzyme Active Site & DNA Pocket (`active_site`)
```bash
python3 <SKILL_DIR>/scripts/render_publication.py active_site \
  --style baker_rfd --structure enzyme.cif \
  --catalytic-sele "resi 1057+1184+1185+1186" --ligand-sele "resn LLK" \
  --with-inset --out-prefix output/active_site
```

### 5. Antibody CDR Loops + 4.5 Å Epitope Footprint (`antibody`)
```bash
python3 <SKILL_DIR>/scripts/render_publication.py antibody \
  --complex ab_ag.cif --antigen-chain A --heavy-chain H --light-chain L \
  --cdr-h1 27-38 --cdr-h2 56-66 --cdr-h3 105-117 \
  --cdr-l1 27-39 --cdr-l2 55-60 --cdr-l3 105-115 \
  --with-inset --auto-crop --out-prefix output/antibody
```

### 6. Local Ligand Pocket Cutaway + In-Pocket Ligand RMSD (`ligand_pocket`)
```bash
python3 <SKILL_DIR>/scripts/render_publication.py ligand_pocket \
  --structure crystal.cif --reference cofold_pred.cif \
  --ligand-sele "resn LLK" --pocket-radius 6.0 \
  --with-inset --auto-crop --out-prefix output/pocket_rmsd
```
Prints exact **In-Pocket Ligand Heavy-Atom RMSD (Å)** to stdout after aligning the pockets.

### 7. Diffusion / MD Trajectory Progression Strip (`trajectory_strip`)
```bash
python3 <SKILL_DIR>/scripts/render_publication.py trajectory_strip \
  --structure traj_multistate.pdb --n-frames 4 \
  --style baker_rfd --out-prefix output/traj_strip
```
Locks the camera on the final frame and stitches $t=0 \to 1$ horizontally. Also accepts `--structures f0.pdb,f1.pdb,...`.

### 8. Multi-Style Comparison Grid (`showcase`)
```bash
python3 <SKILL_DIR>/scripts/render_publication.py showcase \
  --structure design.cif --scene monomer \
  [--all-styles] --out-prefix output/style_grid
```

See [references/PALETTE_AND_RECIPES.md](references/PALETTE_AND_RECIPES.md) for all 10 palettes and PyMOL rendering settings.
