# HEPHAESTUS — Digital Engineering Laboratory

HEPHAESTUS starts with a deliberately small, auditable engineering loop:

1. describe a parametric part and its material, load, and constraints;
2. run a deterministic structural simulation;
3. retain inputs, assumptions, results, and a content fingerprint as provenance;
4. ask the engineering assistant to search manufacturable variants and explain its recommendation.

The first supported part is a rectangular cantilever beam under a point load at its free end. It uses Euler–Bernoulli beam theory and SI units. This is a foundation for a broader system—not a replacement for finite-element analysis or physical validation.

## Quick start

Requires Python 3.11+ and no third-party packages.

```powershell
python -m forge_lab simulate examples/bracket.json
python -m forge_lab improve examples/bracket.json
python -m unittest discover -s tests -v
```

`simulate` writes a traceable result to `runs/`. `improve` searches the configured manufacturing increments for the lightest design that satisfies stress and deflection constraints.

## Input model

See `examples/bracket.json`. Dimensions are metres, forces are newtons, moduli are pascals, and densities are kg/m³. The analysis assumes a homogeneous, linear-elastic material, a rigid fixed end, small deflection, and a single static end load.

## Next increments

- Add geometry import and meshed finite-element solvers behind the same run contract.
- Add more load cases, fatigue/thermal analysis, materials and process constraints.
- Persist runs in a database and expose a reviewable API/UI.
- Let an LLM-driven planning layer select validated analysis tools while preserving deterministic execution and approval gates.

## Week 1 desktop foundation

The desktop application is organised as a local-first Windows architecture:

```text
desktop/   Electron shell + React/TypeScript workspace + Three.js viewport
backend/   FastAPI project service and CadQuery geometry boundary
forge_lab/ Deterministic engineering domain and current analytic solver
```

The Electron renderer only calls the local FastAPI service. Project documents and analysis runs are human-readable JSON files under the user's `Documents/HEPHAESTUS Projects` folder when launched from Electron.

### Development setup

The current machine needs a Python environment with FastAPI and frontend packages:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r backend\requirements.txt
cd desktop
npm install
npm run dev
```

CadQuery and OpenCASCADE (OCP) are integrated in the project `.venv` (Python 3.12). Geometry production uses B-Rep parametric modeling, kernel-level tessellation for Three.js, and export to industry-standard ISO 10303 STEP and STL meshes.

## 3D CAD & Viewport Controls

- **Orbit Controls:** Left-click + drag to rotate 3D camera with inertia damping.
- **Pan & Zoom:** Right-click + drag to pan, mouse scroll wheel to zoom.
- **CAD Silhouette Edges:** Crisp wireframe feature highlighting on top of shaded PBR geometry.
- **Exporting CAD:** Direct STEP and STL export from the API (`/api/projects/{id}/export/step` and `stl`) or desktop toolbar.

