from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Part:
    length_m: float
    width_m: float
    height_m: float

    def validate(self) -> None:
        if min(self.length_m, self.width_m, self.height_m) <= 0:
            raise ValueError("Part dimensions must all be positive.")


@dataclass(frozen=True)
class Material:
    name: str
    youngs_modulus_pa: float
    yield_strength_pa: float
    density_kg_m3: float

    def validate(self) -> None:
        if not self.name.strip():
            raise ValueError("Material name is required.")
        if min(self.youngs_modulus_pa, self.yield_strength_pa, self.density_kg_m3) <= 0:
            raise ValueError("Material properties must all be positive.")


@dataclass(frozen=True)
class LoadCase:
    name: str
    end_force_n: float

    def validate(self) -> None:
        if not self.name.strip():
            raise ValueError("Load-case name is required.")
        if self.end_force_n <= 0:
            raise ValueError("End force must be positive.")


@dataclass(frozen=True)
class Constraints:
    minimum_factor_of_safety: float
    maximum_tip_deflection_m: float
    minimum_width_m: float
    maximum_width_m: float
    minimum_height_m: float
    maximum_height_m: float
    manufacturing_increment_m: float

    def validate(self) -> None:
        if min(self.minimum_factor_of_safety, self.maximum_tip_deflection_m, self.manufacturing_increment_m) <= 0:
            raise ValueError("Safety factor, deflection limit, and increment must be positive.")
        if self.minimum_width_m <= 0 or self.minimum_height_m <= 0:
            raise ValueError("Minimum dimensions must be positive.")
        if self.minimum_width_m > self.maximum_width_m or self.minimum_height_m > self.maximum_height_m:
            raise ValueError("Minimum dimensions cannot exceed maximum dimensions.")


@dataclass(frozen=True)
class Design:
    design_id: str
    part: Part
    material: Material
    load_case: LoadCase
    constraints: Constraints

    @classmethod
    def from_dict(cls, data: dict) -> "Design":
        try:
            design = cls(
                design_id=data["design_id"],
                part=Part(**data["part"]),
                material=Material(**data["material"]),
                load_case=LoadCase(**data["load_case"]),
                constraints=Constraints(**data["constraints"]),
            )
        except (KeyError, TypeError) as exc:
            raise ValueError(f"Invalid design document: {exc}") from exc
        design.validate()
        return design

    def validate(self) -> None:
        if not self.design_id.strip():
            raise ValueError("Design ID is required.")
        self.part.validate()
        self.material.validate()
        self.load_case.validate()
        self.constraints.validate()

    def to_dict(self) -> dict:
        return asdict(self)
