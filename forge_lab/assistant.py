from __future__ import annotations

from dataclasses import dataclass, replace
from decimal import Decimal

from .model import Design
from .simulation import CantileverBeamSolver, SimulationRun


@dataclass(frozen=True)
class Recommendation:
    baseline: SimulationRun
    proposed: SimulationRun | None
    candidates_evaluated: int
    rationale: str


class EngineeringAssistant:
    """Searches bounded, manufacturable design variants using an approved solver."""

    def __init__(self, solver: CantileverBeamSolver | None = None) -> None:
        self.solver = solver or CantileverBeamSolver()

    def improve(self, design: Design) -> Recommendation:
        baseline = self.solver.simulate(design)
        bounds = design.constraints
        increment = Decimal(str(bounds.manufacturing_increment_m))
        widths = self._steps(bounds.minimum_width_m, bounds.maximum_width_m, increment)
        heights = self._steps(bounds.minimum_height_m, bounds.maximum_height_m, increment)
        feasible: list[SimulationRun] = []
        evaluated = 0
        for width in widths:
            for height in heights:
                candidate = replace(design, part=replace(design.part, width_m=width, height_m=height))
                run = self.solver.simulate(candidate)
                evaluated += 1
                if run.result.passes:
                    feasible.append(run)
        if not feasible:
            return Recommendation(
                baseline=baseline,
                proposed=None,
                candidates_evaluated=evaluated,
                rationale="No geometry in the approved manufacturing envelope satisfies both constraints.",
            )
        best = min(feasible, key=lambda run: (run.result.mass_kg, -run.result.factor_of_safety))
        rationale = (
            f"Selected the lowest-mass passing candidate from {evaluated} manufacturable variants; "
            f"it has {best.result.factor_of_safety:.2f} factor of safety and "
            f"{best.result.tip_deflection_m * 1000:.3f} mm tip deflection."
        )
        return Recommendation(baseline, best, evaluated, rationale)

    @staticmethod
    def _steps(lower: float, upper: float, increment: Decimal) -> list[float]:
        current = Decimal(str(lower))
        ceiling = Decimal(str(upper))
        values = []
        while current <= ceiling:
            values.append(float(current))
            current += increment
        return values
