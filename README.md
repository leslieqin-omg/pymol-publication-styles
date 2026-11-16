# pymol-publication-styles

An agent skill and Python/PyMOL rendering toolkit supporting **six classic publication-quality biomolecular visualization styles**:

1. **`baker_rfd`** *(default)* — **Baker Lab / Institute for Protein Design (IPD) RFdiffusion 1–3** aesthetic (*Nature* 2023, *Science* 2024, *Nature Methods* 2025/2026, *bioRxiv* 2025): matte cel-shaded outlines, pastel topology gradients (`#FCD4AC` → `#FCACB4` → `#9494C4` → `#5064AC`), signature motif teal (`#4CB8AC`), target sand (`#FCDCA8`) + hotspot orange (`#F08828`), and charcoal all-atom ligands.
2. **`goodsell`** — **David Goodsell / RCSB *Molecule of the Month*** watercolor full-atom space-filling sphere illustration (`ray_trace_mode=3`, high ambient flat lighting, muted watercolor chains).
3. **`cylindrical`** — ***Nature* / *Cell* Minimalist Cylindrical-Helix** architectural style (`cartoon_cylindrical_helices=1`, flat sheets, slim loops, deep navy + coral + teal palette).
4. **`chimerax_soft`** — **ChimeraX Soft-Shadow / Matte Ceramic AO** cryo-EM aesthetic (outline-free `ray_trace_mode=0`, strong ambient occlusion & soft shadows).
5. **`spotlight`** — **Monochrome Ghost + Jewel-Tone Spotlight** (semi-transparent cool porcelain scaffold + opaque crimson/cyan/amber ball-and-stick focal sites).
6. **`alphafold_plddt`** — **Canonical AlphaFold / ColabFold pLDDT Confidence** coloring (auto-normalizes `0..1` and `0..100` B-factors).

Every run outputs three files at `--out-prefix`:
- `<prefix>.png` — High-resolution ray-traced image
- `<prefix>.pse` — Interactive PyMOL session
- `<prefix>.pml` — Standalone human-readable PyMOL script

## Installation

Place this repository under `~/.gemini/config/skills/pymol-publication-styles/` (or `.agents/skills/pymol-publication-styles/`).

Works with either local open-source PyMOL (`python3 scripts/render_publication.py ...`) or `uv run scripts/render_publication.py ...` (auto-installs `pymol-open-source-whl` via PEP 723).

## Examples

```bash
# 1. Baker Lab RFdiffusion 1-3 binder complex
python3 scripts/render_publication.py binder \
  --style baker_rfd \
  --complex complex.cif \
  --target-chain C --binder-chain K \
  --hotspots "resi 417+453+455+486+489+493" \
  --out-prefix output/binder_baker

# 2. Goodsell Molecule of the Month watercolor spheres
python3 scripts/render_publication.py oligomer \
  --style goodsell \
  --structure assembly.cif \
  --out-prefix output/oligomer_goodsell

# 3. Minimalist cylindrical-helix barrel
python3 scripts/render_publication.py monomer \
  --style cylindrical \
  --structure barrel.cif \
  --out-prefix output/barrel_cylindrical

# 4. ChimeraX soft ceramic AO surface
python3 scripts/render_publication.py binder \
  --style chimerax_soft \
  --complex complex.cif \
  --target-chain C --binder-chain K \
  --out-prefix output/binder_chimerax

# 5. Monochrome ghost + jewel spotlight active site
python3 scripts/render_publication.py active_site \
  --style spotlight \
  --structure enzyme.cif \
  --catalytic-sele "resi 1057+1184+1185+1186" \
  --ligand-sele "resn LLK" \
  --out-prefix output/active_site_spotlight
```
