from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from hashlib import sha256
import json

from .model import Design

SOLVER_ID = "cantilever-euler-bernoulli/v1"
ASSUMPTIONS = (
    "Homogeneous isotropic linear-elastic material",
    "Rigid fixed support",
    "Small-deflection Euler-Bernoulli beam theory",
    "Static point force at the free end",
)


@dataclass(frozen=True)
class SimulationResult:
    maximum_bending_stress_pa: float
    tip_deflection_m: float
    factor_of_safety: float
    volume_m3: float
    mass_kg: float
    passes_stress: bool
    passes_deflection: bool

    @property
    def passes(self) -> bool:
        return self.passes_stress and self.passes_deflection


@dataclass(frozen=True)
class SimulationRun:
    run_id: str
    created_at: str
    solver_id: str
    assumptions: tuple[str, ...]
    design: dict
    result: SimulationResult

    def to_dict(self) -> dict:
        payload = asdict(self)
        payload["result"]["passes"] = self.result.passes
        return payload


class CantileverBeamSolver:
    """Analytic rectangular-cantilever solver, with an auditable run record."""

    def simulate(self, design: Design) -> SimulationRun:
        design.validate()
        length = design.part.length_m
        width = design.part.width_m
        height = design.part.height_m
        force = design.load_case.end_force_n
        modulus = design.material.youngs_modulus_pa

        inertia_m4 = width * height**3 / 12
        max_stress = force * length * (height / 2) / inertia_m4
        tip_deflection = force * length**3 / (3 * modulus * inertia_m4)
        factor_of_safety = design.material.yield_strength_pa / max_stress
        volume = length * width * height
        result = SimulationResult(
            maximum_bending_stress_pa=max_stress,
            tip_deflection_m=tip_deflection,
            factor_of_safety=factor_of_safety,
            volume_m3=volume,
            mass_kg=volume * design.material.density_kg_m3,
            passes_stress=factor_of_safety >= design.constraints.minimum_factor_of_safety,
            passes_deflection=tip_deflection <= design.constraints.maximum_tip_deflection_m,
        )
        created_at = datetime.now(UTC).isoformat()
        signature_payload = {
            "solver_id": SOLVER_ID,
            "design": design.to_dict(),
            "result": asdict(result),
        }
        encoded = json.dumps(signature_payload, sort_keys=True, separators=(",", ":")).encode()
        return SimulationRun(
            run_id=sha256(encoded).hexdigest()[:16],
            created_at=created_at,
            solver_id=SOLVER_ID,
            assumptions=ASSUMPTIONS,
            design=design.to_dict(),
            result=result,
        )
