from __future__ import annotations

import argparse
import json
from pathlib import Path

from .assistant import EngineeringAssistant
from .model import Design
from .simulation import CantileverBeamSolver


def _load_design(path: str) -> Design:
    with open(path, encoding="utf-8") as source:
        return Design.from_dict(json.load(source))


def _write_run(payload: dict, run_id: str) -> Path:
    directory = Path("runs")
    directory.mkdir(exist_ok=True)
    path = directory / f"{run_id}.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def _summary(run: dict) -> str:
    result = run["result"]
    return (
        f"run={run['run_id']} pass={result['passes']} "
        f"stress={result['maximum_bending_stress_pa'] / 1e6:.2f} MPa "
        f"deflection={result['tip_deflection_m'] * 1000:.3f} mm "
        f"FoS={result['factor_of_safety']:.2f} mass={result['mass_kg']:.3f} kg"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="FORGE digital engineering lab")
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("simulate", "improve"):
        subparser = commands.add_parser(command)
        subparser.add_argument("design", help="Path to a design JSON document")
    args = parser.parse_args(argv)
    design = _load_design(args.design)
    if args.command == "simulate":
        run = CantileverBeamSolver().simulate(design)
        payload = run.to_dict()
        output = _write_run(payload, run.run_id)
        print(_summary(payload))
        print(f"provenance={output}")
        return 0
    recommendation = EngineeringAssistant().improve(design)
    baseline = recommendation.baseline.to_dict()
    print("baseline " + _summary(baseline))
    if recommendation.proposed is None:
        print(recommendation.rationale)
        return 2
    proposed = recommendation.proposed.to_dict()
    output = _write_run(proposed, proposed["run_id"])
    print("proposed " + _summary(proposed))
    print(recommendation.rationale)
    print(f"provenance={output}")
    return 0
