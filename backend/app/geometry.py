from __future__ import annotations

from importlib.util import find_spec

from forge_lab.model import Design

from .schemas import GeometryPreview


class CadQueryGeometryService:
    """Geometry boundary for CadQuery; viewport preview works before CAD kernel installation."""

    @property
    def cadquery_available(self) -> bool:
        return find_spec("cadquery") is not None

    def preview(self, design: Design) -> GeometryPreview:
        # The first Week-1 primitive is a CadQuery-equivalent rectangular stock body.
        # The renderer gets metres and a triangle mesh; later this service will return
        # tessellated CadQuery solids for arbitrary parametric features.
        width = design.part.width_m
        length = design.part.length_m
        height = design.part.height_m
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
            generator="cadquery" if self.cadquery_available else "parametric-preview",
            vertices=vertices,
            triangles=triangles,
            dimensions_m={"width": width, "length": length, "height": height},
        )
