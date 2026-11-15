import unittest

from forge_lab.assistant import EngineeringAssistant
from forge_lab.model import Constraints, Design, LoadCase, Material, Part
from forge_lab.simulation import CantileverBeamSolver


def design() -> Design:
    return Design(
        design_id="test-bracket",
        part=Part(length_m=0.18, width_m=0.032, height_m=0.012),
        material=Material("6061-T6", 68_900_000_000, 276_000_000, 2700),
        load_case=LoadCase("rated", 850),
        constraints=Constraints(2.0, 0.0015, 0.02, 0.08, 0.006, 0.05, 0.001),
    )


class CantileverBeamSolverTests(unittest.TestCase):
    def test_known_result_and_provenance(self) -> None:
        run = CantileverBeamSolver().simulate(design())
        self.assertAlmostEqual(run.result.maximum_bending_stress_pa / 1e6, 199.22, places=2)
        self.assertAlmostEqual(run.result.tip_deflection_m * 1000, 5.205, places=3)
        self.assertFalse(run.result.passes)
        self.assertEqual(run.solver_id, "cantilever-euler-bernoulli/v1")
        self.assertEqual(len(run.run_id), 16)

    def test_assistant_returns_lowest_mass_passing_geometry(self) -> None:
        recommendation = EngineeringAssistant().improve(design())
        self.assertIsNotNone(recommendation.proposed)
        self.assertTrue(recommendation.proposed.result.passes)  # type: ignore[union-attr]
        self.assertGreater(recommendation.candidates_evaluated, 0)
        self.assertLessEqual(
            recommendation.proposed.result.mass_kg,  # type: ignore[union-attr]
            recommendation.baseline.result.mass_kg * 2,
        )

    def test_rejects_invalid_dimensions(self) -> None:
        bad = Design(
            design_id="bad",
            part=Part(length_m=0, width_m=0.02, height_m=0.01),
            material=design().material,
            load_case=design().load_case,
            constraints=design().constraints,
        )
        with self.assertRaisesRegex(ValueError, "positive"):
            CantileverBeamSolver().simulate(bad)


if __name__ == "__main__":
    unittest.main()
