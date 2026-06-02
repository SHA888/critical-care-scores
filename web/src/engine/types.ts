// Types mirroring schema/score.schema.json. The generated scores.json conforms
// to these; the contract gate (tools/verify_definitions.py) enforces the schema.

export type InputType = "integer" | "number" | "boolean" | "enum";

export interface EnumOption {
  label: string;
  value: string | number | boolean;
  points?: number;
}

export interface Bin {
  op: ">=" | ">" | "<=" | "<" | "==" | "between";
  value: number | [number, number];
  points: number;
}

export type Mapping =
  | { type: "bins"; bins: Bin[]; default_points?: number }
  | { type: "boolean"; true_points?: number; false_points?: number };

export interface InputSpec {
  id: string;
  label: string;
  type: InputType;
  unit?: string;
  min?: number;
  max?: number;
  required?: boolean;
  help?: string;
  options?: EnumOption[];
  mapping?: Mapping;
}

export interface Band {
  min?: number;
  max?: number;
  label: string;
  interpretation?: string;
  mortality?: string;
  color?: "green" | "yellow" | "orange" | "red" | "gray";
  ref?: string;
}

export type Aggregate =
  | { type: "sum"; rounding?: Rounding }
  | { type: "formula"; expr: string; rounding?: Rounding };

export type Rounding = "none" | "nearest" | "floor" | "ceil";

export interface GoldenVector {
  name?: string;
  inputs: Record<string, unknown>;
  expected_score: number;
  expected_band?: string;
}

export interface ScoreDefinition {
  id: string;
  name: string;
  full_name?: string;
  section: number;
  version?: string;
  status: "current" | "superseded" | "contested";
  references: string[];
  purpose?: string;
  disclaimer: string;
  provenance?: { source_doi?: string; encoded?: string; encoder?: string; notes?: string };
  inputs: InputSpec[];
  scoring: { aggregate: Aggregate };
  output: { unit?: string; bands: Band[] };
  tests: GoldenVector[];
}

export interface Result {
  score: number;
  band: string | null;
  bandDetail: Band | null;
  breakdown: Array<{ id: string; value: unknown; points?: number }>;
}
