---
name: baker-pymol-style
description: >
  Use when rendering publication-quality protein, binder, oligomer, or enzyme
  active-site structure figures in the classic Baker Lab / Institute for Protein
  Design (IPD) RFdiffusion 1-3 PyMOL visual style (matte cel-shaded outlines,
  IPD pastel palette, signature motif teal, target sand + hotspot orange, and
  all-atom active-site pockets).
---

# Baker Lab / IPD PyMOL Style (`RFdiffusion 1–3` Aesthetic)

Render protein structures in the clean, matte, cel-shaded scientific illustration
style of the **RFdiffusion 1** (*Nature* 2023), **RFdiffusion All-Atom** (*Science*
2024), **RFdiffusion 2** (*Nature Methods* 2025/2026), and **RFdiffusion 3**
(*bioRxiv* 2025) publications.

**Never** use RFdiffusion 4's aesthetic or PyMOL's default glossy primary colors
(`green`, `red`, `magenta`, `rainbow`).

## Prerequisites & Execution

1. **Check local PyMOL or `uv`**:
   - If local `python3` already has `pymol` installed (e.g. Homebrew open-source PyMOL), run `python3 scripts/render_baker.py ...`.
   - Otherwise, run with `uv run scripts/render_baker.py ...` (PEP 723 dependencies install `pymol-open-source-whl` automatically; `PYOPENGL_PLATFORM=osmesa` is set on Linux headless hosts).
2. **License Notice**: If `.licenses/pymol_LICENSE.txt` does not exist in the working directory, remind the user to check the PyMOL license at `https://www.pymol.org/` and record the notice.

## Core Rules

- **Triple Output Contract**: Every render produces three files at `--out-prefix`:
  1. `<prefix>.png` — Ray-traced high-resolution figure (`ray_trace_mode=1`, `spec_reflect=0.0`, white background).
  2. `<prefix>.pse` — PyMOL session file for interactive GUI inspection.
  3. `<prefix>.pml` — Clean, human-readable PyMOL script for manual tweaks.
- **Pre-Flight Check**: Always verify the input `.pdb` / `.cif` file exists locally before running. Never rely on `cmd.fetch()`.
- **Cα-Trace Auto-Detection**: The styling engine automatically detects Cα-only diffusion outputs and enables `cartoon_trace = 1`.
- **Mandatory Cleanup**: Custom scripts importing `baker_style` must always call `cmd.quit()` in a `finally:` block.

## Quick Start: Four Core Modes (`scripts/render_baker.py`)

### 1. Monomer, Motif Scaffolding, & AF2/Crystal Overlay (`monomer`)

```bash
python3 ~/.gemini/config/skills/baker-pymol-style/scripts/render_baker.py monomer \
  --structure design.pdb \
  --reference af2_pred.pdb \
  --motif-sele "resi 20-35" \
  --design-role gray \
  --out-prefix output/monomer_overlay
```

- `--design-role gray` (RFD1 Fig. 2/4): Design model in `ipd_model_gray`, AF2/experimental structure in 4-stop IPD pastel spectrum.
- `--design-role colored` (RFD2 Fig. 1c/3d): Design in pastel spectrum, reference/PDB match in `ipd_model_gray`.

### 2. Target–Binder Complex (`binder`)

```bash
python3 ~/.gemini/config/skills/baker-pymol-style/scripts/render_baker.py binder \
  --complex complex.pdb \
  --target-chain A \
  --binder-chain B \
  --hotspots "resi 45+48+52" \
  --show-interface-sticks \
  --out-prefix output/binder_fig
```

- Target chain renders as `ipd_target_sand` (`#FCDCA8`) smooth surface with `ipd_hotspot_orange` (`#F08828`) epitope patches.
- Binder renders in `ipd_pastel_lavender` (`#9494C4`, or `ipd_pastel_rose` / `spectrum`).
- Add `--reference-binder crystal.pdb` to overlay an experimental structure in `ipd_model_gray`, or `--zoom-interface` for a close-up H-bond view.

### 3. Symmetric Oligomers & Cryo-EM Density (`oligomer`)

```bash
python3 ~/.gemini/config/skills/baker-pymol-style/scripts/render_baker.py oligomer \
  --structure c4_assembly.pdb \
  --motif-sele "resn HIS and resi 52" \
  --view both \
  --out-prefix output/oligomer_fig
```

- Cycles subunits across `ipd_pastel_peach`, `ipd_pastel_rose`, `ipd_pastel_lavender`, `ipd_pastel_deepblue`, `ipd_pastel_slate`, and `ipd_motif_teal`.
- `--view both` renders `<prefix>_top.png` and 90°-rotated `<prefix>_side.png`.
- Supports `--em-map map.mrc --em-contour 2.0` for translucent `ipd_surface_gray` density envelopes.

### 4. Enzyme Active Site, Ligand, & DNA Pocket (`active_site`)

```bash
python3 ~/.gemini/config/skills/baker-pymol-style/scripts/render_baker.py active_site \
  --structure enzyme.pdb \
  --catalytic-sele "resi 27+36+59+61" \
  --ligand-sele "organic" \
  --scaffold-transparency 0.55 \
  --out-prefix output/active_site_fig
```

- Semi-transparent RFD2 pastel scaffold (`cartoon_transparency=0.55`).
- Catalytic side-chain carbons in signature `ipd_motif_teal` (`#4CB8AC`) with `ipd_slate_gray` (`#7A828E`) Cα/Cβ connectors; ligands in dark charcoal `ipd_ligand_carbon` (`#48484C`) with heteroatom colors.

## Custom Python Scripts

For multi-panel layouts or bespoke selections, import `baker_style` directly from `~/.gemini/config/skills/baker-pymol-style/scripts/baker_style.py`:

```python
import sys
sys.path.insert(0, "/Users/leslie/.gemini/config/skills/baker-pymol-style/scripts")
import pymol
pymol.pymol_argv = ["pymol", "-cq"]
pymol.finish_launching()
from pymol import cmd
import baker_style

try:
    pml = []
    baker_style.apply_ipd_theme(cmd, cylindrical_helices=False, pml_lines=pml)
    baker_style.verify_and_load(cmd, "design.pdb", "design", pml_lines=pml)
    cmd.show("cartoon", "design")
    baker_style.color_ipd_spectrum(cmd, "design", palette_mode="rfd1", pml_lines=pml)
    cmd.orient("design")
    baker_style.render_outputs(cmd, "output/custom", pml_lines=pml)
finally:
    cmd.quit()
```

See [references/PALETTE_AND_RECIPES.md](references/PALETTE_AND_RECIPES.md) for the complete RGB/Hex table and figure-by-figure mapping to RFdiffusion 1–3.
