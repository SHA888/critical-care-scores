import { useMemo, useState } from "react";
import { SCORES, scoresBySection } from "./data";
import { compute, EngineError } from "./engine/engine";
import type { InputSpec, Result, ScoreDefinition } from "./engine/types";
import { sectionName } from "./sections";
import { citedCodes, getReference, type Reference } from "./references";

const STATUS_LABEL: Record<string, string> = {
  current: "Current",
  superseded: "Superseded",
  contested: "Contested",
};

export function App() {
  const [activeId, setActiveId] = useState<string>(SCORES[0]?.id ?? "");
  const active = SCORES.find((s) => s.id === activeId);

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          <span className="logo" aria-hidden>＋</span>
          <div>
            <h1>Critical Care Scores</h1>
            <p className="tagline">Verified ICU score calculators — computed in your browser</p>
          </div>
        </div>
      </header>

      <div className="disclaimer" role="note">
        <strong>For clinical decision support only.</strong> These calculators reproduce published
        scores from cited sources. They do not replace clinical judgement — verify every result
        against the primary publication before any bedside use. No data you enter leaves your device.
      </div>

      <div className="layout">
        <ScorePicker activeId={activeId} onSelect={setActiveId} />
        <main className="panel">
          {active ? <Calculator key={active.id} def={active} /> : <p>No score selected.</p>}
        </main>
      </div>

      <footer className="footer">
        {SCORES.length} calculable score(s) · each citation- and golden-vector-verified ·{" "}
        <a href="https://github.com/SHA888/critical-care-scores">source &amp; references</a>
      </footer>
    </div>
  );
}

function ScorePicker({ activeId, onSelect }: { activeId: string; onSelect: (id: string) => void }) {
  const grouped = useMemo(() => scoresBySection(), []);
  const sections = [...grouped.keys()].sort((a, b) => a - b);
  return (
    <nav className="sidebar" aria-label="Score picker">
      {sections.map((sec) => (
        <div key={sec} className="sidebar-group">
          <h2 className="sidebar-heading">{sectionName(sec)}</h2>
          <ul>
            {grouped.get(sec)!.map((s) => (
              <li key={s.id}>
                <button
                  className={s.id === activeId ? "score-link active" : "score-link"}
                  onClick={() => onSelect(s.id)}
                >
                  {s.name}
                </button>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </nav>
  );
}

function Calculator({ def }: { def: ScoreDefinition }) {
  const [values, setValues] = useState<Record<string, unknown>>(() => initialValues(def));

  const { result, error } = useMemo<{ result: Result | null; error: string | null }>(() => {
    try {
      const filled = Object.fromEntries(
        Object.entries(values).filter(([, v]) => v !== "" && v !== undefined),
      );
      // Only compute once every required input is present.
      const missing = def.inputs.some(
        (i) => (i.required ?? true) && (filled[i.id] === undefined),
      );
      if (missing) return { result: null, error: null };
      return { result: compute(def, filled), error: null };
    } catch (e) {
      return { result: null, error: e instanceof EngineError ? e.message : String(e) };
    }
  }, [def, values]);

  const setValue = (id: string, v: unknown) => setValues((prev) => ({ ...prev, [id]: v }));

  return (
    <article className="calculator">
      <div className="calc-head">
        <h2>
          {def.name}
          <span className={`badge badge-${def.status}`}>{STATUS_LABEL[def.status]}</span>
        </h2>
        {def.full_name && <p className="full-name">{def.full_name}</p>}
        {def.purpose && <p className="purpose">{def.purpose}</p>}
      </div>

      <form className="inputs" onSubmit={(e) => e.preventDefault()}>
        {def.inputs.map((spec) => (
          <Field key={spec.id} spec={spec} value={values[spec.id]} onChange={(v) => setValue(spec.id, v)} />
        ))}
      </form>

      {error && <div className="result error" role="alert">{error}</div>}
      {result && <ResultCard def={def} result={result} />}
      {!result && !error && <p className="hint">Enter all values to calculate.</p>}

      <section className="provenance">
        <p className="score-disclaimer">{def.disclaimer}</p>
        <ReferenceList def={def} />
        {def.provenance?.encoded && <p className="encoded">Definition encoded {def.provenance.encoded}.</p>}
      </section>
    </article>
  );
}

function ReferenceList({ def }: { def: ScoreDefinition }) {
  const codes = citedCodes(def.references, def.output.bands.map((b) => b.ref));
  return (
    <div className="references">
      <h3>References</h3>
      <ol>
        {codes.map((code) => {
          const ref = getReference(code);
          return (
            <li key={code} id={`ref-${code}`}>
              <span className="refcode">{code}</span>{" "}
              {ref ? <Citation reference={ref} /> : <em>citation not found in SCORES.md</em>}
            </li>
          );
        })}
      </ol>
    </div>
  );
}

// Renders citation text with its URL turned into a clickable link in place.
function Citation({ reference }: { reference: Reference }) {
  if (!reference.url) return <>{reference.text}</>;
  const [before, ...rest] = reference.text.split(reference.url);
  const after = rest.join(reference.url);
  return (
    <>
      {before}
      <a href={reference.url} target="_blank" rel="noopener noreferrer">
        {reference.url}
      </a>
      {after}
    </>
  );
}

function Field({
  spec,
  value,
  onChange,
}: {
  spec: InputSpec;
  value: unknown;
  onChange: (v: unknown) => void;
}) {
  const id = `f-${spec.id}`;
  return (
    <div className="field">
      <label htmlFor={id}>
        {spec.label}
        {spec.unit && <span className="unit"> ({spec.unit})</span>}
      </label>
      {spec.type === "boolean" ? (
        <input
          id={id}
          type="checkbox"
          checked={Boolean(value)}
          onChange={(e) => onChange(e.target.checked)}
        />
      ) : spec.type === "enum" ? (
        <select
          id={id}
          value={value === undefined ? "" : optionIndex(spec, value)}
          onChange={(e) => onChange(e.target.value === "" ? undefined : spec.options![Number(e.target.value)].value)}
        >
          <option value="">—</option>
          {spec.options!.map((opt, idx) => (
            <option key={idx} value={idx}>
              {opt.label}
            </option>
          ))}
        </select>
      ) : (
        <input
          id={id}
          type="number"
          inputMode="decimal"
          step={spec.type === "integer" ? 1 : "any"}
          min={spec.min}
          max={spec.max}
          value={value === undefined ? "" : String(value)}
          onChange={(e) => onChange(e.target.value === "" ? undefined : Number(e.target.value))}
        />
      )}
      {spec.help && <p className="help">{spec.help}</p>}
    </div>
  );
}

function ResultCard({ def, result }: { def: ScoreDefinition; result: Result }) {
  const color = result.bandDetail?.color ?? "gray";
  return (
    <div className={`result band-${color}`} role="status" aria-live="polite">
      <div className="result-score">
        <span className="score-num">{result.score}</span>
        <span className="score-unit">{def.output.unit ?? "points"}</span>
      </div>
      <div className="result-band">
        <strong>{result.band ?? "—"}</strong>
        {result.bandDetail?.interpretation && <p>{result.bandDetail.interpretation}</p>}
        {result.bandDetail?.mortality && <p className="mortality">{result.bandDetail.mortality}</p>}
        {result.bandDetail?.ref && (
          <p className="band-source">
            Source: <a href={`#ref-${result.bandDetail.ref}`}>{result.bandDetail.ref}</a>
          </p>
        )}
      </div>
    </div>
  );
}

function optionIndex(spec: InputSpec, value: unknown): string {
  const idx = (spec.options ?? []).findIndex((o) => o.value === value);
  return idx >= 0 ? String(idx) : "";
}

function initialValues(def: ScoreDefinition): Record<string, unknown> {
  const v: Record<string, unknown> = {};
  for (const spec of def.inputs) {
    if (spec.type === "boolean") v[spec.id] = false;
  }
  return v;
}
