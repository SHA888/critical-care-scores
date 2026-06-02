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


DOI_UA = "critical-care-scores-verify/1.0 (+https://github.com/SHA888/critical-care-scores)"


def check_doi_resolves(doi: str, timeout: int = 15, retries: int = 2) -> str | None:
    """Resolve a bare DOI via the DOI Handle System content-negotiation API.

    Uses https://doi.org/api/handles/<doi> instead of a HEAD on the redirect
    target: the handle API is built for programmatic resolution and returns a
    JSON `responseCode` (1 = resolves, 100 = handle not found), so it doesn't
    trip the anti-bot 403s that publishers (JAMA, ATS, …) return to HEAD probes.

    A non-resolving handle (responseCode != 1) is a definitive failure (no retry).
    Transient network/timeout errors are retried so a momentary API blip can't
    falsely fail the gate. Returns None if the DOI resolves, else a reason string.
    """
    import json
    import time
    import urllib.error
    import urllib.parse
    import urllib.request

    api = "https://doi.org/api/handles/" + urllib.parse.quote(doi, safe="/")
    req = urllib.request.Request(api, headers={"User-Agent": DOI_UA, "Accept": "application/json"})
    last_net_err = ""
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.load(resp)
        except urllib.error.HTTPError as e:  # 404 still carries a JSON body with responseCode
            try:
                data = json.load(e)
            except Exception:
                last_net_err = f"HTTP {e.code}"
                time.sleep(1.0 * (attempt + 1))
                continue
        except Exception as e:  # noqa: BLE001 - network/timeout/DNS: transient, retry
            last_net_err = str(e)
            time.sleep(1.0 * (attempt + 1))
            continue

        rc = data.get("responseCode")
        if rc == 1:
            return None
        reason = {100: "handle not found", 200: "values not found", 2: "resolution error"}.get(rc, "")
        return f"responseCode {rc}{' (' + reason + ')' if reason else ''}"

    return f"network error after {retries + 1} attempts ({last_net_err})"


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
        # Capture the bare DOI after doi.org/ and resolve via the Handle System API.
        dois = re.findall(r"https?://doi\.org/(\S+)", md)
        for doi in sorted({d.rstrip(".,;)]") for d in dois}):
            reason = check_doi_resolves(doi)
            if reason:
                errors.append(f"DOI not resolving: {doi} ({reason})")

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
