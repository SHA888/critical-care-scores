# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

A living reference of ICU scoring systems with automated discovery and verification tools. The project maintains domain-organized documentation (SCORES.md) with a machine-readable contract enforced by CI (verify_scores.py). All Python tools are stdlib-only and runnable via `uv`.

## Architecture

**The Loop** (see README.md diagram):
1. `tools/discover_scores.py` — finds candidate DOIs from Crossref/PubMed by keyword, stores in SQLite
2. Human triage — annotates candidates as `current` / `superseded` / `contested` / `unverified` into SCORES.md
3. `tools/verify_scores.py` — CI gate; validates the status/citation contract
4. Keywords auto-extract from SCORES.md to keep discovery seed in sync

**Key principle**: Discovery proposes, verification disposes. Discovery never sets status; verification never fetches.

## Files

| File | Role |
|------|------|
| `SCORES.md` | Domain-organized reference: 24 sections, ~172 ICU scoring systems. Each row has `Status` + `Key ref` columns. |
| `TODO.md` | Verification protocol, Definition of Done, work breakdown by priority tier, milestones to v1.0.0. |
| `tools/discover_scores.py` v0.1 | Literature harvester: query keywords → DOI dedup → living SQLite DB upsert. Ports: Crossref (public), PubMed (public), MCP (stub). |
| `tools/verify_scores.py` | CI gate: validates status/citation contract + ratchet on unverified count. Enforces 6 rules (see Contract below). |

## The Contract (enforced by verify_scores.py)

A row passes validation if ALL hold:

1. `Status` is one of: `current` | `superseded` | `contested` | `unverified`
2. If `Status ≠ unverified` → `Key ref` must be non-empty (not `—` or `-`)
3. If `Status == unverified` → `Key ref` must be `—` (empty)
4. Every `R#` code referenced exists in the **References** section
5. `unverified` count is monotonic (ratchet): can only lower, never raise
6. (**--check-dois flag**) Every DOI in References resolves to HTTP < 400

Build fails on breach. See TODO.md §2 for CI wiring.

## Common Tasks

### Discovery: find new papers to triage

```bash
# See what keywords will be auto-extracted (no network)
uv run tools/discover_scores.py keywords

# Harvest recent DOIs (populates discover.db)
uv run tools/discover_scores.py discover --since 2023 --sources crossref,pubmed --limit 10 --mailto your@email.org

# Report candidates in a given triage state (or newly surfaced)
uv run tools/discover_scores.py report --triage candidate
uv run tools/discover_scores.py report --new-only
```

**Output**: SQLite store (discover.db) with provenance, run metadata, and relevance hints (keyword + signal match).

### Verification: enforce the contract

```bash
# Local check (no network)
uv run tools/verify_scores.py SCORES.md --max-unverified 161

# Deep check: also validate DOI resolution (slower, use before tagging)
uv run tools/verify_scores.py SCORES.md --max-unverified 0 --check-dois
```

**Exit code** 0 = pass; 1 = contract breach (prints violations to stderr).

### Update workflow

1. **Human**: Run discovery, triage candidates into SCORES.md, set `Status` + `Key ref`
2. **CI gate**: `uv run tools/verify_scores.py SCORES.md --max-unverified <new_count>`
3. **Ratchet**: decrement `--max-unverified` in `.github/workflows/verify-scores.yml` on each merge
4. **Milestone**: when `unverified == 0` with `--check-dois` green → tag `1.0.0`

## Development Notes

### Tools design

- **Stdlib-only** (Python ≥3.11, PEP 723 headers). No lockfile needed; `uv run` is the only dependency.
- **Ports & Adapters**: `SourceAdapter` protocol allows Crossref, PubMed, or MCP sources to be swapped. Currently MCP seam documented but unwired.
- **Store**: WAL-enabled SQLite for safe concurrent access and provenance.
- **Parsing**: verify_scores.py uses regex over markdown tables; detect via "Key ref" + "Status" headers.

### Common gotchas

- `discover_scores.py keywords` must read SCORES.md directly; adjust `--keywords-from` flag if filename changes.
- verify_scores.py ignores the Status legend table (filtered by "Key ref" in header).
- unverified count is enforced at merge time; a PR can only lower it.
- DOI resolution (--check-dois) is slow; use only pre-tag or in scheduled jobs.

### Testing & validation

No formal test suite yet. Validate by:
- Local `verify_scores.py` against modified SCORES.md (catches contract breaches)
- Manual `discover` → inspect discover.db (sanity check dedupe + provenance)
- Pre-tag full run with --check-dois (validates DOI resolution)

## References

- **README.md**: Project vision, file organization, quickstart
- **SCORES.md**: Reference itself + status legend + verified deltas
- **TODO.md**: Verification protocol, Definition of Done, work breakdown to v1.0.0
