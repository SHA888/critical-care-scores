#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""verify_definitions.py — contract gate for calculable score definitions.

Sibling to verify_scores.py: where that tool enforces the *citation* contract on
SCORES.md, this tool enforces the *calculation* contract on scores/*.json. A
definition passes iff ALL hold:

  1. Required keys present; status in {current, superseded, contested}
     (never 'unverified' — unverified scores are not calculable).
  2. Every R# in `references` (and in any band `ref`) resolves to an entry in the
     SCORES.md References section  [reuses verify_scores.parse()].
  3. `id` equals the filename stem; inputs/bands/tests non-empty.
  4. At least one golden vector (`tests`), and the reference engine reproduces
     every vector's expected_score (and expected_band when given).
  5. (optional, if `jsonschema` is importable) full JSON Schema validation
     against schema/score.schema.json.

Exit 0 = pass; 1 = breach (violations printed to stderr). Stdlib-only by default;
JSON Schema validation is opt-in and degrades gracefully when the lib is absent.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "engine"))

from verify_scores import RCODE, parse  # noqa: E402  (reuse citation parser)
from ccscores import EngineError, compute, load_definition  # noqa: E402

VALID_STATUS = {"current", "superseded", "contested"}


def load_reference_codes(scores_md: Path) -> set[str]:
    _, ref_codes = parse(scores_md.read_text(encoding="utf-8"))
    return ref_codes


def check_definition(path: Path, ref_codes: set[str]) -> list[str]:
    errs: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{path.name}: invalid JSON ({exc})"]

    # Rule 3: id matches filename stem
    if data.get("id") != path.stem:
        errs.append(f"{path.name}: id {data.get('id')!r} != filename stem {path.stem!r}")

    # Rule 1: status
    status = data.get("status")
    if status not in VALID_STATUS:
        errs.append(f"{path.name}: status {status!r} not in {sorted(VALID_STATUS)}")

    # Rule 2: references resolve
    refs = data.get("references") or []
    if not refs:
        errs.append(f"{path.name}: 'references' must be non-empty")
    cited = set(refs)
    for band in data.get("output", {}).get("bands", []):
        if band.get("ref"):
            cited.add(band["ref"])
    for code in sorted(cited):
        if not RCODE.fullmatch(code):
            errs.append(f"{path.name}: malformed reference code {code!r}")
        elif code not in ref_codes:
            errs.append(f"{path.name}: reference {code} not found in SCORES.md References")

    # Rule 3: structural non-empties
    if not data.get("inputs"):
        errs.append(f"{path.name}: 'inputs' must be non-empty")
    if not data.get("output", {}).get("bands"):
        errs.append(f"{path.name}: 'output.bands' must be non-empty")
    if not data.get("disclaimer"):
        errs.append(f"{path.name}: 'disclaimer' is required")

    # Rule 4: golden vectors exist and the engine reproduces them
    tests = data.get("tests") or []
    if not tests:
        errs.append(f"{path.name}: at least one golden vector ('tests') is required")
    band_labels = {b.get("label") for b in data.get("output", {}).get("bands", [])}
    for i, vector in enumerate(tests):
        tag = vector.get("name", f"vector-{i}")
        try:
            result = compute(data, vector["inputs"])
        except EngineError as exc:
            errs.append(f"{path.name}::{tag}: engine error: {exc}")
            continue
        if result.score != vector.get("expected_score"):
            errs.append(
                f"{path.name}::{tag}: engine score {result.score} != expected "
                f"{vector.get('expected_score')}"
            )
        exp_band = vector.get("expected_band")
        if exp_band is not None:
            if exp_band not in band_labels:
                errs.append(f"{path.name}::{tag}: expected_band {exp_band!r} not a declared band")
            if result.band != exp_band:
                errs.append(f"{path.name}::{tag}: engine band {result.band!r} != expected {exp_band!r}")

    return errs


def jsonschema_check(paths: list[Path], schema_path: Path) -> list[str]:
    try:
        import jsonschema  # type: ignore
    except ImportError:
        print("note: 'jsonschema' not installed; skipping full schema validation "
              "(structural checks still enforced).", file=sys.stderr)
        return []
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    errs: list[str] = []
    for path in paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        for e in sorted(validator.iter_errors(data), key=lambda e: e.path):
            loc = "/".join(str(p) for p in e.path) or "<root>"
            errs.append(f"{path.name}: schema: {loc}: {e.message}")
    return errs


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate calculable score definitions.")
    ap.add_argument("scores_dir", nargs="?", default=str(ROOT / "scores"),
                    help="directory of *.json definitions (default: scores/)")
    ap.add_argument("--scores-md", default=str(ROOT / "SCORES.md"),
                    help="path to SCORES.md for reference resolution")
    ap.add_argument("--schema", default=str(ROOT / "schema" / "score.schema.json"),
                    help="JSON Schema for optional full validation")
    args = ap.parse_args()

    scores_dir = Path(args.scores_dir)
    paths = sorted(scores_dir.glob("*.json"))
    if not paths:
        print(f"error: no definitions found in {scores_dir}", file=sys.stderr)
        return 1

    ref_codes = load_reference_codes(Path(args.scores_md))

    violations: list[str] = []
    for path in paths:
        violations.extend(check_definition(path, ref_codes))
    violations.extend(jsonschema_check(paths, Path(args.schema)))

    if violations:
        print(f"FAIL: {len(violations)} violation(s) across {len(paths)} definition(s):",
              file=sys.stderr)
        for v in violations:
            print(f"  - {v}", file=sys.stderr)
        return 1

    n_vectors = sum(len(json.loads(p.read_text())["tests"]) for p in paths)
    print(f"OK: {len(paths)} definition(s) valid; {n_vectors} golden vector(s) reproduced.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
