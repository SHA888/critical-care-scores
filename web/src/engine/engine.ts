// Calculation engine — faithful port of engine/ccscores/engine.py. The Python
// engine is the reference; this must reproduce every golden vector.

import { EngineError, evaluate, roundHalfUp } from "./formula";
import type { Band, Bin, InputSpec, Mapping, Result, ScoreDefinition } from "./types";

export { EngineError };

function toNumber(value: unknown, label: string): number {
  if (typeof value === "boolean") throw new EngineError(`'${label}' expects a number, got boolean`);
  if (typeof value === "number") return value;
  throw new EngineError(`'${label}' expects a number, got ${JSON.stringify(value)}`);
}

function validateValue(spec: InputSpec, value: unknown): unknown {
  const label = spec.label ?? spec.id;
  if (spec.type === "boolean") {
    if (typeof value === "boolean") return value;
    if (value === 0 || value === 1) return Boolean(value);
    throw new EngineError(`'${label}' expects a boolean`);
  }
  if (spec.type === "enum") {
    for (const opt of spec.options ?? []) if (opt.value === value) return value;
    throw new EngineError(`'${label}' value ${JSON.stringify(value)} not in allowed options`);
  }
  const num = toNumber(value, label);
  if (spec.type === "integer" && !Number.isInteger(num))
    throw new EngineError(`'${label}' expects an integer`);
  if (spec.min !== undefined && num < spec.min)
    throw new EngineError(`'${label}' value ${num} below minimum ${spec.min}`);
  if (spec.max !== undefined && num > spec.max)
    throw new EngineError(`'${label}' value ${num} above maximum ${spec.max}`);
  return num;
}

function binPoints(mapping: Extract<Mapping, { type: "bins" }>, value: number): number {
  for (const b of mapping.bins) {
    if (matchBin(b, value)) return b.points;
  }
  return mapping.default_points ?? 0;
}

function matchBin(b: Bin, v: number): boolean {
  switch (b.op) {
    case ">=":
      return v >= (b.value as number);
    case ">":
      return v > (b.value as number);
    case "<=":
      return v <= (b.value as number);
    case "<":
      return v < (b.value as number);
    case "==":
      return v === (b.value as number);
    case "between": {
      const [lo, hi] = b.value as [number, number];
      return lo <= v && v <= hi;
    }
  }
}

function inputPoints(spec: InputSpec, value: unknown): number {
  if (spec.type === "boolean") {
    const mp = (spec.mapping as Extract<Mapping, { type: "boolean" }>) ?? { type: "boolean" };
    return value ? mp.true_points ?? 1 : mp.false_points ?? 0;
  }
  if (spec.type === "enum") {
    for (const opt of spec.options ?? []) if (opt.value === value) return opt.points ?? 0;
    return 0;
  }
  if (spec.mapping?.type === "bins") return binPoints(spec.mapping, value as number);
  return 0;
}

function applyRounding(score: number, mode: string | undefined): number {
  if (mode === "nearest") return roundHalfUp(score);
  if (mode === "floor") return Math.floor(score);
  if (mode === "ceil") return Math.ceil(score);
  return score;
}

function selectBand(bands: Band[], score: number): Band | null {
  for (const band of bands) {
    const lo = band.min;
    const hi = band.max;
    if ((lo === undefined || score >= lo) && (hi === undefined || score <= hi)) return band;
  }
  return null;
}

export function compute(definition: ScoreDefinition, inputs: Record<string, unknown>): Result {
  const specs = new Map(definition.inputs.map((i) => [i.id, i]));
  for (const key of Object.keys(inputs)) {
    if (!specs.has(key)) throw new EngineError(`unknown input: ${key}`);
  }

  const values: Record<string, unknown> = {};
  for (const [id, spec] of specs) {
    if (!(id in inputs)) {
      if (spec.required ?? true) throw new EngineError(`missing required input '${id}'`);
      continue;
    }
    values[id] = validateValue(spec, inputs[id]);
  }

  const aggregate = definition.scoring.aggregate;
  const breakdown: Result["breakdown"] = [];
  let total: number;

  if (aggregate.type === "sum") {
    total = 0;
    for (const [id, spec] of specs) {
      if (!(id in values)) continue;
      const pts = inputPoints(spec, values[id]);
      total += pts;
      breakdown.push({ id, value: values[id], points: pts });
    }
  } else {
    const missing = [...specs.keys()].filter((id) => !(id in values));
    if (missing.length) throw new EngineError(`formula needs all inputs; missing: ${missing.join(", ")}`);
    total = evaluate(aggregate.expr, values);
    for (const id of specs.keys()) breakdown.push({ id, value: values[id] });
  }

  total = applyRounding(total, aggregate.rounding);
  const band = selectBand(definition.output.bands, total);
  return { score: total, band: band ? band.label : null, bandDetail: band, breakdown };
}
