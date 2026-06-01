#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []   # stdlib only by design; --check-dois uses urllib
# ///
"""
verify_scores.py — CI gate for critical-care-scores.md

Enforces the machine-readable contract declared in the document's Status legend.
A principle without a failing build is a wish; this is the mechanism.

Contract:
  1. Status is one of: current | superseded | contested | unverified
  2. status != unverified  =>  Key ref is non-empty (not '-' / '—')
  3. status == unverified   =>  Key ref == '—'
  4. Every R# code used in a row exists in the References section
  5. unverified count is a ratchet: must be <= --max-unverified (baseline)
  6. (optional, --check-dois) every DOI in References resolves to HTTP < 400

Only tables whose header contains 'Key ref' are treated as score tables,
so the Status-legend table is excluded automatically.

Usage:
  uv run verify_scores.py critical-care-scores.md --max-unverified 161
  uv run verify_scores.py critical-care-scores.md --max-unverified 140 --check-dois
Exit code 0 = pass, 1 = contract violation.
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass

VALID_STATUS = {"current", "superseded", "contested", "unverified"}
EMPTY_REF = {"—", "-", ""}
RCODE = re.compile(r"\bR\d+\b")


@dataclass
class Row:
    line_no: int
    status: str
    keyref: str


def split_cells(line: str) -> list[str]:
    # strip leading/trailing pipe, split, trim
    return [c.strip() for c in line.strip().strip("|").split("|")]


def parse(md: str) -> tuple[list[Row], set[str]]:
    lines = md.splitlines()
    rows: list[Row] = []
    ref_codes: set[str] = set()
    in_refs = False
    header: list[str] | None = None
    status_idx = keyref_idx = -1

    for i, line in enumerate(lines, start=1):
        if line.startswith("## References") or line.startswith("# References"):
            in_refs = True
        if in_refs:
            m = re.match(r"\s*[-*]\s*\*\*(R\d+)\*\*", line)
            if m:
                ref_codes.add(m.group(1))
            continue

        if not line.lstrip().startswith("|"):
            header = None
            continue

        cells = split_cells(line)
        # detect header row of a score table
        if "Key ref" in cells and "Status" in cells:
            header = cells
            status_idx = cells.index("Status")
            keyref_idx = cells.index("Key ref")
            continue
        if header is None:
            continue
        # skip the markdown separator row |---|---|
        if set("".join(cells)) <= set("-: "):
            continue
        if max(status_idx, keyref_idx) >= len(cells):
            continue
        status = cells[status_idx]
        keyref = cells[keyref_idx]
        rows.append(Row(i, status, keyref))
        for code in RCODE.findall(keyref):
            ref_codes.discard("__sentinel__")  # noop to keep mypy calm
    return rows, ref_codes


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--max-unverified", type=int, required=True,
                    help="ratchet ceiling; build fails if unverified exceeds this")
    ap.add_argument("--check-dois", action="store_true")
    args = ap.parse_args()

    md = open(args.path, encoding="utf-8").read()
    rows, ref_codes = parse(md)

    errors: list[str] = []
    unverified = 0
    used_codes: set[str] = set()

    for r in rows:
        if r.status not in VALID_STATUS:
            errors.append(f"L{r.line_no}: invalid status '{r.status}'")
            continue
        if r.status == "unverified":
            unverified += 1
            if r.keyref not in EMPTY_REF:
                errors.append(f"L{r.line_no}: unverified row must have empty ref, got '{r.keyref}'")
        else:
            if r.keyref in EMPTY_REF:
                errors.append(f"L{r.line_no}: status '{r.status}' requires a Key ref")
            for code in RCODE.findall(r.keyref):
                used_codes.add(code)

    missing = used_codes - ref_codes
    if missing:
        errors.append(f"Key ref codes used but absent from References: {sorted(missing)}")

    if unverified > args.max_unverified:
        errors.append(
            f"ratchet breach: {unverified} unverified rows > ceiling {args.max_unverified} "
            "(a PR may only lower this number)")

    if args.check_dois:
        import urllib.request
        dois = re.findall(r"https?://doi\.org/\S+", md)
        for url in sorted(set(dois)):
            try:
                req = urllib.request.Request(url, method="HEAD")
                with urllib.request.urlopen(req, timeout=15) as resp:
                    if resp.status >= 400:
                        errors.append(f"DOI not resolving ({resp.status}): {url}")
            except Exception as e:  # noqa: BLE001
                errors.append(f"DOI check failed: {url} ({e})")

    verified = len(rows) - unverified
    print(f"score rows: {len(rows)} | verified: {verified} | unverified: {unverified} "
          f"| ceiling: {args.max_unverified}")
    if errors:
        print("\nCONTRACT VIOLATIONS:")
        for e in errors:
            print(f"  ✗ {e}")
        return 1
    print("contract OK ✓")
    return 0


if __name__ == "__main__":
    sys.exit(main())
