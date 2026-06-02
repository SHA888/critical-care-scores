// Safe arithmetic evaluator — a tokenizer + recursive-descent parser. NO eval,
// NO Function constructor, no property access. Mirrors engine/ccscores/formula.py
// so both engines agree on every golden vector.

export class EngineError extends Error {}

export function roundHalfUp(x: number): number {
  // floor(x + 0.5) === JS Math.round for finite x; matches the Python engine.
  return Math.floor(x + 0.5);
}

const FUNCS: Record<string, { fn: (...a: number[]) => number; arity: number | null }> = {
  ln: { fn: Math.log, arity: 1 },
  exp: { fn: Math.exp, arity: 1 },
  log10: { fn: Math.log10, arity: 1 },
  sqrt: { fn: Math.sqrt, arity: 1 },
  floor: { fn: Math.floor, arity: 1 },
  ceil: { fn: Math.ceil, arity: 1 },
  abs: { fn: Math.abs, arity: 1 },
  round: { fn: roundHalfUp, arity: 1 },
  min: { fn: Math.min, arity: null },
  max: { fn: Math.max, arity: null },
  clamp: { fn: (x, lo, hi) => Math.max(lo, Math.min(hi, x)), arity: 3 },
};

type Tok =
  | { t: "num"; v: number }
  | { t: "id"; v: string }
  | { t: "op"; v: string }
  | { t: "lparen" }
  | { t: "rparen" }
  | { t: "comma" };

function tokenize(src: string): Tok[] {
  const toks: Tok[] = [];
  let i = 0;
  while (i < src.length) {
    const c = src[i];
    if (c === " " || c === "\t" || c === "\n") {
      i++;
      continue;
    }
    if (c >= "0" && c <= "9") {
      let j = i;
      while (j < src.length && /[0-9.eE+\-]/.test(src[j])) {
        // allow exponent sign only right after e/E
        if ((src[j] === "+" || src[j] === "-") && !(src[j - 1] === "e" || src[j - 1] === "E")) break;
        j++;
      }
      const num = Number(src.slice(i, j));
      if (Number.isNaN(num)) throw new EngineError(`invalid number near '${src.slice(i, j)}'`);
      toks.push({ t: "num", v: num });
      i = j;
      continue;
    }
    if (/[a-zA-Z_]/.test(c)) {
      let j = i;
      while (j < src.length && /[a-zA-Z0-9_]/.test(src[j])) j++;
      toks.push({ t: "id", v: src.slice(i, j) });
      i = j;
      continue;
    }
    if ("+-*/%^".includes(c)) {
      toks.push({ t: "op", v: c });
      i++;
      continue;
    }
    if (c === "(") {
      toks.push({ t: "lparen" });
      i++;
      continue;
    }
    if (c === ")") {
      toks.push({ t: "rparen" });
      i++;
      continue;
    }
    if (c === ",") {
      toks.push({ t: "comma" });
      i++;
      continue;
    }
    throw new EngineError(`unexpected character '${c}' in formula`);
  }
  return toks;
}

export function evaluate(expr: string, variables: Record<string, unknown>): number {
  const toks = tokenize(expr);
  let pos = 0;

  const peek = () => toks[pos];
  const next = () => toks[pos++];
  const isOp = (...ops: string[]) => {
    const tk = toks[pos];
    return tk?.t === "op" && ops.includes(tk.v);
  };

  function coerce(name: string): number {
    const v = variables[name];
    if (typeof v === "boolean") return v ? 1 : 0;
    if (typeof v === "number") return v;
    if (v === undefined) throw new EngineError(`formula references unknown variable '${name}'`);
    throw new EngineError(`formula variable '${name}' is not numeric`);
  }

  function parseExpr(): number {
    let left = parseTerm();
    while (isOp("+", "-")) {
      const op = (next() as { t: "op"; v: string }).v;
      const right = parseTerm();
      left = op === "+" ? left + right : left - right;
    }
    return left;
  }

  function parseTerm(): number {
    let left = parsePower();
    while (isOp("*", "/", "%")) {
      const op = (next() as { t: "op"; v: string }).v;
      const right = parsePower();
      left = op === "*" ? left * right : op === "/" ? left / right : left % right;
    }
    return left;
  }

  function parsePower(): number {
    const base = parseUnary();
    if (isOp("^")) {
      next();
      return Math.pow(base, parsePower()); // right-associative
    }
    return base;
  }

  function parseUnary(): number {
    if (isOp("+", "-")) {
      const op = (next() as { t: "op"; v: string }).v;
      const val = parseUnary();
      return op === "-" ? -val : val;
    }
    return parsePrimary();
  }

  function parsePrimary(): number {
    const tk = peek();
    if (!tk) throw new EngineError("unexpected end of formula");
    if (tk.t === "num") {
      next();
      return tk.v;
    }
    if (tk.t === "lparen") {
      next();
      const v = parseExpr();
      if (next()?.t !== "rparen") throw new EngineError("missing ')' in formula");
      return v;
    }
    if (tk.t === "id") {
      next();
      if (peek()?.t === "lparen") {
        const spec = FUNCS[tk.v];
        if (!spec) throw new EngineError(`call to disallowed function '${tk.v}'`);
        next(); // (
        const args: number[] = [];
        if (peek()?.t !== "rparen") {
          args.push(parseExpr());
          while (peek()?.t === "comma") {
            next();
            args.push(parseExpr());
          }
        }
        if (next()?.t !== "rparen") throw new EngineError("missing ')' in function call");
        if (spec.arity !== null && args.length !== spec.arity)
          throw new EngineError(`function '${tk.v}' expects ${spec.arity} args, got ${args.length}`);
        return spec.fn(...args);
      }
      return coerce(tk.v);
    }
    throw new EngineError(`unexpected token in formula`);
  }

  const result = parseExpr();
  if (pos !== toks.length) throw new EngineError("trailing tokens in formula");
  return result;
}
