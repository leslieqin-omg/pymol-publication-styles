---
name: pymol-publication-styles
description: >
  Use when rendering publication-quality protein, binder, oligomer, cryo-EM,
  or enzyme active-site structure figures in PyMOL across six classic styles:
  Baker Lab / IPD RFdiffusion 1-3 pastel cel-shaded style (baker_rfd), David
  Goodsell Molecule of the Month watercolor sphere style (goodsell), Nature/Cell
  cylindrical-helix architecture style (cylindrical), ChimeraX soft-shadow
  ambient-occlusion cryo-EM style (chimerax_soft), monochrome ghost scaffold
  with jewel-tone focal spotlight (spotlight), and canonical AlphaFold pLDDT
  confidence coloring (alphafold_plddt).
---

# PyMOL Publication Styles

Render biomolecular structures in six recognizable, publication-grade PyMOL
aesthetics without writing repetitive lighting or color setup code:

| `--style` | Aesthetic Inspiration | Best Used For |
|---|---|---|
| `baker_rfd` *(default)* | Baker Lab / IPD RFdiffusion 1–3 (*Nature* 2023, *Science* 2024, *Nat Methods* 2025, *bioRxiv* 2025) | De novo binders, monomers, symmetric oligomers, RFD2/RFD3 all-atom active sites (avoids RFD4 style) |
| `goodsell` | David Goodsell / RCSB *Molecule of the Month* | Space-filling full-atom complexes, macromolecular assemblies, textbook-style watercolor illustrations |
| `cylindrical` | *Nature* / *Cell* cylindrical-helix architectural figures | Membrane proteins, GPCRs, ion channels, multi-helix bundles, topology overviews |
| `chimerax_soft` | ChimeraX `soft` ambient-occlusion lighting | Cryo-EM density maps, outline-free matte ceramic surfaces, epitope complexes |
| `spotlight` | Monochrome ghost scaffold + jewel-tone spotlight | Enzyme active sites, drug-binding pockets, disease mutation highlights |
| `alphafold_plddt` | Canonical AlphaFold / ColabFold confidence palette | Structure prediction confidence (pLDDT $\ge 90, 70, 50, <50$) with matte outlined cartoons |

**Never** use PyMOL's default glossy primary colors (`green`, `red`, `magenta`, `rainbow`) or RFdiffusion 4's harsh palette.

## Prerequisites & Execution

1. **Local PyMOL or `uv`**:
   - If local `python3` has `pymol` installed, run `python3 scripts/render_publication.py ...`.
   - Otherwise, run with `uv run scripts/render_publication.py ...` (PEP 723 auto-installs `pymol-open-source-whl`; `PYOPENGL_PLATFORM=osmesa` is enabled on Linux headless hosts).
2. **License Notice**: If `.licenses/pymol_LICENSE.txt` does not exist in the working directory, remind the user to check the PyMOL license at `https://www.pymol.org/`.

## Core Rules

- **Triple Output Contract**: Every render writes `<out-prefix>.png` (ray-traced high-res), `<out-prefix>.pse` (interactive PyMOL session), and `<out-prefix>.pml` (standalone PyMOL script).
- **Pre-Flight Check**: Verify the input `.pdb` / `.cif` exists locally before executing; never use `cmd.fetch()`.
- **Cα-Trace & pLDDT Normalization**: Cα-only diffusion outputs automatically get `cartoon_trace = 1`; `0..1` B-factor pLDDT files automatically scale to `0..100`.
- **Mandatory Cleanup**: Custom scripts importing `publication_style` must call `cmd.quit()` inside a `finally:` block.

## Quick Start (`scripts/render_publication.py`)

Pass `--style <style>` to any of the four structural subcommands (`monomer`, `binder`, `oligomer`, `active_site`):

### 1. Baker Lab / RFdiffusion 1–3 Binder Complex (`baker_rfd`)
```bash
python3 ~/.gemini/config/skills/pymol-publication-styles/scripts/render_publication.py binder \
  --style baker_rfd \
  --complex complex.cif \
  --target-chain C --binder-chain K \
  --hotspots "resi 417+453+455+486+489+493" \
  --out-prefix output/binder_baker
```

### 2. Goodsell Watercolor Space-Filling Style (`goodsell`)
```bash
python3 ~/.gemini/config/skills/pymol-publication-styles/scripts/render_publication.py oligomer \
  --style goodsell \
  --structure assembly.cif \
  --out-prefix output/assembly_goodsell
```

### 3. Cylindrical-Helix Minimalist Architecture (`cylindrical`)
```bash
python3 ~/.gemini/config/skills/pymol-publication-styles/scripts/render_publication.py monomer \
  --style cylindrical \
  --structure barrel.cif \
  --out-prefix output/barrel_cylindrical
```

### 4. ChimeraX Soft-Shadow Ceramic Cryo-EM Surface (`chimerax_soft`)
```bash
python3 ~/.gemini/config/skills/pymol-publication-styles/scripts/render_publication.py binder \
  --style chimerax_soft \
  --complex complex.cif \
  --target-chain C --binder-chain K \
  --target-repr surface \
  --out-prefix output/binder_chimerax
```

### 5. Monochrome Ghost + Jewel-Tone Spotlight (`spotlight`)
```bash
python3 ~/.gemini/config/skills/pymol-publication-styles/scripts/render_publication.py active_site \
  --style spotlight \
  --structure enzyme.cif \
  --catalytic-sele "resi 1057+1184+1185+1186" \
  --ligand-sele "resn LLK" \
  --out-prefix output/active_site_spotlight
```

### 6. AlphaFold pLDDT Confidence Style (`alphafold_plddt`)
```bash
python3 ~/.gemini/config/skills/pymol-publication-styles/scripts/render_publication.py monomer \
  --style alphafold_plddt \
  --structure af2_model.cif \
  --out-prefix output/model_plddt
```

## Custom Python Scripts

Import `publication_style` from `~/.gemini/config/skills/pymol-publication-styles/scripts/publication_style.py`:

```python
import sys
sys.path.insert(0, "/Users/leslie/.gemini/config/skills/pymol-publication-styles/scripts")
import pymol
pymol.pymol_argv = ["pymol", "-cq"]
pymol.finish_launching()
from pymol import cmd
import publication_style

try:
    pml = []
    publication_style.apply_theme(cmd, style="chimerax_soft", pml_lines=pml)
    publication_style.verify_and_load(cmd, "design.cif", "design", pml_lines=pml)
    cmd.show("cartoon", "design")
    publication_style.color_style_spectrum(cmd, "design", style="chimerax_soft", pml_lines=pml)
    cmd.orient("design")
    publication_style.render_outputs(cmd, "output/custom", pml_lines=pml)
finally:
    cmd.quit()
```

See [references/PALETTE_AND_RECIPES.md](references/PALETTE_AND_RECIPES.md) for exact RGB/Hex tables and detailed settings for all six styles.
