"""Definition loader + calculation engine."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

from .errors import EngineError
from .formula import evaluate, round_half_up


@dataclass
class Result:
    score: float
    band: str | None
    band_detail: dict[str, Any] | None
    breakdown: list[dict[str, Any]] = field(default_factory=list)


def load_definition(path: str | Path) -> dict[str, Any]:
    """Load and minimally sanity-check a score definition JSON file.

    Schema validation proper lives in tools/verify_definitions.py; this only
    guards against the handful of shapes the engine would crash on.
    """
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    for key in ("id", "inputs", "scoring", "output"):
        if key not in data:
            raise EngineError(f"definition missing required key '{key}' ({path})")
    return data


def _to_number(value: Any, label: str) -> float:
    if isinstance(value, bool):
        raise EngineError(f"'{label}' expects a number, got boolean")
    if isinstance(value, (int, float)):
        return float(value)
    raise EngineError(f"'{label}' expects a number, got {value!r}")


def _validate_value(spec: Mapping[str, Any], value: Any) -> Any:
    """Coerce/validate one input value against its spec; return the canonical value."""
    typ = spec["type"]
    label = spec.get("label", spec["id"])
    if typ == "boolean":
        if isinstance(value, bool):
            return value
        if value in (0, 1):
            return bool(value)
        raise EngineError(f"'{label}' expects a boolean, got {value!r}")
    if typ == "enum":
        options = spec.get("options", [])
        for opt in options:
            if opt["value"] == value:
                return value
        allowed = ", ".join(repr(o["value"]) for o in options)
        raise EngineError(f"'{label}' value {value!r} not in allowed options ({allowed})")
    # integer / number
    num = _to_number(value, label)
    if typ == "integer" and float(num).is_integer() is False:
        raise EngineError(f"'{label}' expects an integer, got {value!r}")
    lo, hi = spec.get("min"), spec.get("max")
    if lo is not None and num < lo:
        raise EngineError(f"'{label}' value {num} below minimum {lo}")
    if hi is not None and num > hi:
        raise EngineError(f"'{label}' value {num} above maximum {hi}")
    return num


def _bin_points(mapping: Mapping[str, Any], value: float) -> float:
    for b in mapping["bins"]:
        op, ref = b["op"], b["value"]
        hit = (
            (op == ">=" and value >= ref)
            or (op == ">" and value > ref)
            or (op == "<=" and value <= ref)
            or (op == "<" and value < ref)
            or (op == "==" and value == ref)
            or (op == "between" and isinstance(ref, (list, tuple)) and ref[0] <= value <= ref[1])
        )
        if hit:
            return float(b["points"])
    return float(mapping.get("default_points", 0))


def _input_points(spec: Mapping[str, Any], value: Any) -> float:
    typ = spec["type"]
    if typ == "boolean":
        mp = spec.get("mapping") or {"type": "boolean"}
        return float(mp.get("true_points", 1) if value else mp.get("false_points", 0))
    if typ == "enum":
        for opt in spec.get("options", []):
            if opt["value"] == value:
                return float(opt.get("points", 0))
        return 0.0
    mapping = spec.get("mapping")
    if mapping and mapping.get("type") == "bins":
        return _bin_points(mapping, float(value))
    return 0.0  # numeric input with no mapping contributes nothing under 'sum'


def _round(score: float, mode: str) -> float:
    import math

    if mode == "nearest":
        return round_half_up(score)
    if mode == "floor":
        return float(math.floor(score))
    if mode == "ceil":
        return float(math.ceil(score))
    return score


def _select_band(bands: list[Mapping[str, Any]], score: float) -> Mapping[str, Any] | None:
    for band in bands:
        lo, hi = band.get("min"), band.get("max")
        if (lo is None or score >= lo) and (hi is None or score <= hi):
            return band
    return None


def compute(definition: Mapping[str, Any], inputs: Mapping[str, Any]) -> Result:
    """Compute the score for `inputs` against `definition`."""
    specs = {i["id"]: i for i in definition["inputs"]}
    unknown = set(inputs) - set(specs)
    if unknown:
        raise EngineError(f"unknown input(s): {', '.join(sorted(unknown))}")

    values: dict[str, Any] = {}
    for iid, spec in specs.items():
        if iid not in inputs:
            if spec.get("required", True):
                raise EngineError(f"missing required input '{iid}'")
            continue
        values[iid] = _validate_value(spec, inputs[iid])

    aggregate = definition["scoring"]["aggregate"]
    breakdown: list[dict[str, Any]] = []

    if aggregate["type"] == "sum":
        total = 0.0
        for iid, spec in specs.items():
            if iid not in values:
                continue
            pts = _input_points(spec, values[iid])
            total += pts
            breakdown.append({"id": iid, "value": values[iid], "points": pts})
    elif aggregate["type"] == "formula":
        missing = [iid for iid in specs if iid not in values]
        if missing:
            raise EngineError(f"formula needs all inputs; missing: {', '.join(missing)}")
        total = evaluate(aggregate["expr"], values)
        breakdown = [{"id": iid, "value": values[iid]} for iid in specs]
    else:  # pragma: no cover - schema-guarded
        raise EngineError(f"unknown aggregate type {aggregate['type']!r}")

    total = _round(total, aggregate.get("rounding", "none"))
    band = _select_band(definition["output"]["bands"], total)
    return Result(
        score=total,
        band=band["label"] if band else None,
        band_detail=dict(band) if band else None,
        breakdown=breakdown,
    )
