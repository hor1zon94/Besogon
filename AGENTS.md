# Besogon project instructions

The user's canonical repository is https://github.com/hor1zon94/Besogon.
Keep project source, approved art documentation, modeling references, and the future Godot project here. The user downloads this repository and checks the result. Commit and push completed changes under the user's standing instruction to maintain the project here; do not leave finished project work only in a temporary chat output directory.

## Layout

- `prototype/besogon.html`: existing standalone Canvas 2D combat prototype.
- `docs/`: game design, prototype requirements, approved visual direction, and original approved images.
- `references/models/`: standalone modeling reference pack, PNG sheets, dimensions, gallery, and Godot export requirements.
- `godot/`: reserved location for the future actual Godot project. Currently it contains a status README, not a runnable Godot project.
- `tools/`: reproducible checks and release packaging tools.

## Current scope and status

- The visual direction was approved on 2026-11-09. See `docs/APPROVED_VISUAL.md`.
- The user has not explicitly approved the HTML prototype or instructed a full Godot port yet. Do not describe an empty folder or documentation as a completed Godot game.
- Core prototype scope: five combat rooms, manual sickle/hammer combo, dash, enemies, portals, restart. No boss, narrative reveal, or meta-progression in the HTML prototype.
- Boss, devil, and hell modeling sheets are proposed later-stage designs, not separately approved visual designs. Keep this status visible.
- Model integration parameters are in `references/models/02_GODOT_EXPORT.md`; PNGs are visual references, not engineering drawings.

## Verification and delivery

- For HTML changes, run `node tools/verify_html.cjs`. These are simulation and mocked Canvas API checks; they do not prove browser rendering or game feel.
- Run `python tools/package_references.py --check` after changing model pack files, and check relative links when moving documents.
- Keep original PNGs in ordinary Git so source ZIP downloads include real images. No LFS pointers are configured in this initial repository.
- Put generated release ZIPs in GitHub Releases instead of duplicating them in Git history. `python tools/package_references.py` rebuilds the two reference archives under ignored `build/release/`.
- Never commit credentials, Godot's generated `.godot/` cache, temporary execution files, or machine-local paths in project documentation.
- Update the root README with what can actually be run and any material verification limits.
