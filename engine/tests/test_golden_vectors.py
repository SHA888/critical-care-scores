"""Golden-vector conformance: the Python engine must reproduce every test
vector declared in scores/*.json. These vectors are the executable acceptance
criteria and the contract the TypeScript engine must also satisfy.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ccscores import compute, load_definition

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCORES_DIR = REPO_ROOT / "scores"


def _cases():
    cases = []
    for path in sorted(SCORES_DIR.glob("*.json")):
        definition = json.loads(path.read_text(encoding="utf-8"))
        for i, vector in enumerate(definition.get("tests", [])):
            name = vector.get("name", f"vector-{i}")
            cases.append(pytest.param(path, vector, id=f"{definition['id']}::{name}"))
    return cases


def test_scores_dir_present():
    assert SCORES_DIR.is_dir(), "scores/ directory missing"
    assert list(SCORES_DIR.glob("*.json")), "no score definitions found"


@pytest.mark.parametrize("path,vector", _cases())
def test_golden_vector(path, vector):
    definition = load_definition(path)
    result = compute(definition, vector["inputs"])
    assert result.score == vector["expected_score"], (
        f"{path.name}: score {result.score} != expected {vector['expected_score']}"
    )
    if "expected_band" in vector:
        assert result.band == vector["expected_band"], (
            f"{path.name}: band {result.band!r} != expected {vector['expected_band']!r}"
        )
