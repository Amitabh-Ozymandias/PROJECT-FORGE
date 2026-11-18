from __future__ import annotations

from importlib.util import find_spec
from pathlib import Path
from typing import Any

from forge_lab.model import Design

from .schemas import GeometryPreview


class CadQueryGeometryService:
    """Geometry boundary connecting CadQuery CAD generation to Three.js mesh previews."""

    @property
    def cadquery_available(self) -> bool:
        return find_spec("cadquery") is not None

    def build_solid(self, design: Design) -> Any:
        """Generates a CadQuery solid model from parametric design specifications."""
        import cadquery as cq

        # Work in millimeters for standard CAD mechanical conventions
        w_mm = design.part.width_m * 1000.0
        l_mm = design.part.length_m * 1000.0
        h_mm = design.part.height_m * 1000.0

        model = cq.Workplane("XY").box(w_mm, l_mm, h_mm)
        return model

    def preview(self, design: Design) -> GeometryPreview:
        width = design.part.width_m
        length = design.part.length_m
        height = design.part.height_m

        if self.cadquery_available:
            try:
                model = self.build_solid(design)
                shape = model.val()
                # Tessellate OpenCASCADE solid: linear deflection 0.1 mm, angular 0.1 rad
                raw_verts, raw_tris = shape.tessellate(0.1, 0.1)

                # Convert millimetres back to metres for Three.js viewport coordinates
                vertices = [[v.x / 1000.0, v.y / 1000.0, v.z / 1000.0] for v in raw_verts]
                triangles = [idx for tri in raw_tris for idx in tri]
                return GeometryPreview(
                    generator="cadquery",
                    vertices=vertices,
                    triangles=triangles,
                    dimensions_m={"width": width, "length": length, "height": height},
                )
            except Exception:
                pass

        # Fallback parametric mesh if CadQuery is not available
        x, y, z = width / 2, length / 2, height / 2
        vertices = [
            [-x, -y, -z], [x, -y, -z], [x, y, -z], [-x, y, -z],
            [-x, -y, z], [x, -y, z], [x, y, z], [-x, y, z],
        ]
        triangles = [
            0, 2, 1, 0, 3, 2, 4, 5, 6, 4, 6, 7,
            0, 1, 5, 0, 5, 4, 1, 2, 6, 1, 6, 5,
            2, 3, 7, 2, 7, 6, 3, 0, 4, 3, 4, 7,
        ]
        return GeometryPreview(
            generator="parametric-preview",
            vertices=vertices,
            triangles=triangles,
            dimensions_m={"width": width, "length": length, "height": height},
        )

    def export_step(self, design: Design, output_path: Path) -> Path:
        """Export solid model to STEP format using CadQuery."""
        if not self.cadquery_available:
            raise RuntimeError("CadQuery is required to export STEP files.")
        import cadquery as cq
        model = self.build_solid(design)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cq.exporters.export(model, str(output_path), cq.exporters.ExportTypes.STEP)
        return output_path

    def export_stl(self, design: Design, output_path: Path) -> Path:
        """Export solid model to STL format using CadQuery."""
        if not self.cadquery_available:
            raise RuntimeError("CadQuery is required to export STL files.")
        import cadquery as cq
        model = self.build_solid(design)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cq.exporters.export(model, str(output_path), cq.exporters.ExportTypes.STL)
        return output_path

