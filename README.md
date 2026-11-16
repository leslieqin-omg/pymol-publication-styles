# baker-pymol-style

An agent skill and Python/PyMOL rendering toolkit that reproduces the classic **David Baker Lab / Institute for Protein Design (IPD)** figure aesthetic from **RFdiffusion 1** (*Nature* 2023), **RFdiffusion All-Atom** (*Science* 2024), **RFdiffusion 2** (*Nature Methods* 2025/2026), and **RFdiffusion 3** (*bioRxiv* 2025).

## Features

- **Exact IPD RGB Palette**: Pixel-sampled pastel topology gradients (`#FCD4AC` → `#FCACB4` → `#9494C4` → `#5064AC`), signature motif/catalytic teal (`#4CB8AC`), target sand (`#FCDCA8`) + hotspot orange (`#F08828`), and charcoal all-atom ligands (`#48484C`).
- **Matte Cel-Shaded Ray-Tracing**: Crisp thin outlines (`ray_trace_mode=1`, `ray_trace_gain=0.10`), zero plastic specular glare (`spec_reflect=0.0`), soft high-ambient lighting (`ambient=0.50`), and ambient occlusion (`ambient_occlusion_mode=1`).
- **Four Ready-to-Use Modes**:
  1. `monomer` — De novo monomers, functional motif scaffolding, and design-vs-AF2/crystal overlays with automatic `align`/`cealign` RMSD reporting.
  2. `binder` — Target surface + orange epitope hotspots + pastel de novo binder + optional interface H-bonds and crystal overlay.
  3. `oligomer` — Symmetric assemblies (`Cn`, `Dn`, cages) with automatic subunit color cycling, top/side 90° views, and cryo-EM/nsEM map envelopes.
  4. `active_site` — RFdiffusion 2/3 all-atom enzyme theozymes, small-molecule ligands, metal cofactors, and DNA pockets with semi-transparent scaffolds.
- **Triple Output**: Every run writes `<prefix>.png`, `<prefix>.pse` (interactive PyMOL session), and `<prefix>.pml` (standalone PyMOL command script).

## Installation

Place this repository under `~/.gemini/config/skills/baker-pymol-style/` (or your workspace `.agents/skills/baker-pymol-style/`).

Works with either:
- Local open-source PyMOL (`python3 scripts/render_baker.py ...`), or
- `uv run scripts/render_baker.py ...` (auto-installs `pymol-open-source-whl` via PEP 723).

## Quick Examples

```bash
# Monomer / TIM barrel
python3 scripts/render_baker.py monomer \
  --structure design.cif \
  --out-prefix output/monomer

# Target-binder complex with hotspots
python3 scripts/render_baker.py binder \
  --complex complex.cif \
  --target-chain C --binder-chain K \
  --hotspots "resi 417+453+455+486+489+493" \
  --out-prefix output/binder

# Enzyme active site (RFD2/RFD3 style)
python3 scripts/render_baker.py active_site \
  --structure enzyme.cif \
  --catalytic-sele "resi 1057+1184+1185+1186" \
  --ligand-sele "resn LLK" \
  --out-prefix output/active_site
```
