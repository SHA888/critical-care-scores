#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []   # stdlib only (sqlite3, urllib, json). See note on msgspec below.
# ///
"""
discover_scores.py — literature DISCOVERY harvester for a living reference DB.

Sibling to verify_scores.py. Division of labour:
    verify_scores.py  -> VALIDATION (is a row's status backed by a citation? gate.)
    discover_scores.py -> DISCOVERY (what new DOIs match our work? feed the pipeline.)

It never decides currency. It finds candidate papers (new validations, new scores,
guideline updates), deduplicates them by DOI across sources, and upserts into a
SQLite store that grows and freshens on every run -> a *living* database.

Architecture (ports & adapters):
    Record                 -- the domain object parsed at the boundary
    Store                  -- SQLite persistence (upsert, provenance, run log)
    SourceAdapter(Protocol)-- the port: .name + .search(query, since, limit)
    CrossrefAdapter        -- concrete, public api.crossref.org (no key)
    PubMedAdapter          -- concrete, public NCBI E-utilities (optional key)
    McpSourceAdapter       -- documented seam: wire any MCP server you run locally

Keywords are auto-extracted from SCORES.md so the discovery seed
tracks the same corpus the verification pipeline is annotating.

Usage:
    uv run discover_scores.py keywords --keywords-from SCORES.md
    uv run discover_scores.py discover --since 2023 --sources crossref,pubmed --limit 8
    uv run discover_scores.py report --triage candidate --since-run latest
    uv run discover_scores.py report --new-only

Discovery, not validation. Triage is for a human (or the verify pass) to action.
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Iterable, Protocol, runtime_checkable

UA = "discover_scores/0.1 (living-ref-db; mailto:{mailto})"
NOW = lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")  # noqa: E731

# Signal tokens that hint a paper is *useful to our work* (not a currency verdict).
RELEVANCE_SIGNALS = (
    "validation", "validate", "external validation", "recalibration", "calibration",
    "definition", "consensus", "guideline", "derivation", "prognostic", "auroc",
    "discrimination", "update", "comparison", "diagnostic accuracy", "score",
)

# ----------------------------------------------------------------------------- domain
@dataclass(slots=True)
class Record:
    uid: str                 # doi (normalized) if present, else "source:native_id"
    doi: str | None
    title: str
    year: int | None
    container: str           # journal / venue
    source: str              # crossref | pubmed | mcp:<name>
    surfaced_by: str         # the keyword tag that found it
    url: str
    relevance_hint: str = ""
    raw: dict = field(default_factory=dict)


def norm_doi(doi: str | None) -> str | None:
    if not doi:
        return None
    d = doi.strip().lower()
    d = re.sub(r"^https?://(dx\.)?doi\.org/", "", d)
    return d or None


def relevance_hint(title: str, keyword: str) -> str:
    t = title.lower()
    hits = [s for s in RELEVANCE_SIGNALS if s in t]
    if hits:
        return f"kw:{keyword}; signal:{','.join(sorted(set(hits))[:4])}"
    return ""


# ----------------------------------------------------------------------------- store
class Store:
    def __init__(self, path: str):
        self.db = sqlite3.connect(path)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.executescript(
            """
            CREATE TABLE IF NOT EXISTS records(
                uid TEXT PRIMARY KEY,
                doi TEXT,
                title TEXT,
                year INTEGER,
                container TEXT,
                source TEXT,
                surfaced_by TEXT,
                url TEXT,
                relevance_hint TEXT,
                triage TEXT NOT NULL DEFAULT 'new',   -- new|candidate|relevant|irrelevant|linked
                first_seen TEXT NOT NULL,
                last_seen TEXT NOT NULL,
                times_seen INTEGER NOT NULL DEFAULT 1,
                raw TEXT
            );
            CREATE TABLE IF NOT EXISTS runs(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                started TEXT, finished TEXT, sources TEXT,
                keywords INTEGER, inserted INTEGER, updated INTEGER
            );
            CREATE INDEX IF NOT EXISTS ix_triage ON records(triage);
            CREATE INDEX IF NOT EXISTS ix_first ON records(first_seen);
            """
        )
        self.db.commit()

    def upsert(self, r: Record) -> str:
        """Returns 'inserted' or 'updated'. Idempotent; merges cross-source by DOI."""
        now = NOW()
        cur = self.db.execute("SELECT triage FROM records WHERE uid=?", (r.uid,))
        existing = cur.fetchone()
        triage = "candidate" if r.relevance_hint else "new"
        if existing is None:
            self.db.execute(
                """INSERT INTO records(uid,doi,title,year,container,source,surfaced_by,
                   url,relevance_hint,triage,first_seen,last_seen,times_seen,raw)
                   VALUES(?,?,?,?,?,?,?,?,?,?,?,?,1,?)""",
                (r.uid, r.doi, r.title, r.year, r.container, r.source, r.surfaced_by,
                 r.url, r.relevance_hint, triage, now, now, json.dumps(r.raw)),
            )
            self.db.commit()
            return "inserted"
        # living-DB freshness: bump last_seen + times_seen; never downgrade human triage
        self.db.execute(
            """UPDATE records SET last_seen=?, times_seen=times_seen+1,
               relevance_hint=COALESCE(NULLIF(?,''), relevance_hint)
               WHERE uid=?""",
            (now, r.relevance_hint, r.uid),
        )
        self.db.commit()
        return "updated"

    def log_run(self, sources, n_kw, ins, upd, started):
        self.db.execute(
            "INSERT INTO runs(started,finished,sources,keywords,inserted,updated) VALUES(?,?,?,?,?,?)",
            (started, NOW(), ",".join(sources), n_kw, ins, upd),
        )
        self.db.commit()

    def report(self, triage: str | None, new_only: bool, limit: int) -> list[sqlite3.Row]:
        self.db.row_factory = sqlite3.Row
        q = "SELECT * FROM records"
        clauses, params = [], []
        if triage:
            clauses.append("triage=?"); params.append(triage)
        if new_only:
            clauses.append("times_seen=1")
        if clauses:
            q += " WHERE " + " AND ".join(clauses)
        q += " ORDER BY first_seen DESC, year DESC LIMIT ?"
        params.append(limit)
        return list(self.db.execute(q, params))


# ----------------------------------------------------------------------------- ports
@runtime_checkable
class SourceAdapter(Protocol):
    name: str
    def search(self, query: str, tag: str, since: int | None, limit: int) -> Iterable[Record]: ...


def _http_json(url: str, mailto: str, retries: int = 2) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA.format(mailto=mailto)})
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception:  # noqa: BLE001
            if attempt == retries:
                raise
            time.sleep(1.5 * (attempt + 1))
    return {}


# --------------------------------------------------------------------- crossref adapter
class CrossrefAdapter:
    name = "crossref"
    def __init__(self, mailto: str):
        self.mailto = mailto

    def search(self, query, tag, since, limit):
        params = {
            "query.bibliographic": query,
            "rows": str(limit),
            "select": "DOI,title,issued,container-title,URL",
            "sort": "issued", "order": "desc",
        }
        if since:
            params["filter"] = f"from-pub-date:{since}-01-01"
        url = "https://api.crossref.org/works?" + urllib.parse.urlencode(params)
        data = _http_json(url, self.mailto)
        for it in data.get("message", {}).get("items", []):
            doi = norm_doi(it.get("DOI"))
            title = (it.get("title") or ["(untitled)"])[0]
            year = None
            parts = (it.get("issued", {}) or {}).get("date-parts", [[None]])
            if parts and parts[0] and parts[0][0]:
                year = int(parts[0][0])
            container = (it.get("container-title") or [""])[0]
            yield Record(
                uid=doi or f"crossref:{it.get('DOI','?')}",
                doi=doi, title=title, year=year, container=container,
                source="crossref", surfaced_by=tag,
                url=it.get("URL", f"https://doi.org/{doi}" if doi else ""),
                relevance_hint=relevance_hint(title, tag), raw=it,
            )
            time.sleep(0.2)  # polite


# ---------------------------------------------------------------------- pubmed adapter
class PubMedAdapter:
    name = "pubmed"
    def __init__(self, mailto: str, api_key: str | None = None):
        self.mailto = mailto
        self.api_key = api_key
        self.delay = 0.11 if api_key else 0.34  # ~10/s with key, ~3/s without

    def _eutils(self, endpoint: str, params: dict) -> dict:
        params = {**params, "retmode": "json", "tool": "discover_scores", "email": self.mailto}
        if self.api_key:
            params["api_key"] = self.api_key
        url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/{endpoint}?" + urllib.parse.urlencode(params)
        return _http_json(url, self.mailto)

    def search(self, query, tag, since, limit):
        term = query
        es = {"db": "pubmed", "term": term, "retmax": str(limit), "sort": "date"}
        if since:
            es.update(mindate=str(since), maxdate=str(datetime.now().year), datetype="pdat")
        ids = self._eutils("esearch.fcgi", es).get("esearchresult", {}).get("idlist", [])
        time.sleep(self.delay)
        if not ids:
            return
        summ = self._eutils("esummary.fcgi", {"db": "pubmed", "id": ",".join(ids)})
        result = summ.get("result", {})
        for pmid in result.get("uids", []):
            it = result.get(pmid, {})
            doi = None
            for aid in it.get("articleids", []):
                if aid.get("idtype") == "doi":
                    doi = norm_doi(aid.get("value"))
            title = it.get("title", "(untitled)")
            year = None
            m = re.search(r"\b(19|20)\d{2}\b", it.get("pubdate", ""))
            if m:
                year = int(m.group())
            yield Record(
                uid=doi or f"pubmed:{pmid}",
                doi=doi, title=title, year=year, container=it.get("fulljournalname", ""),
                source="pubmed", surfaced_by=tag,
                url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                relevance_hint=relevance_hint(title, tag), raw={"pmid": pmid, **it},
            )
        time.sleep(self.delay)


# ------------------------------------------------------------------------- MCP seam
class McpSourceAdapter:
    """Extension seam for ANY MCP server you run locally (bioRxiv, Scite, Scholar
    Gateway, Clinical Trials, ...). The MCP connectors visible inside a Claude chat
    are *session* tools and cannot be called from a standalone script; to use one
    here, run its MCP server via an MCP client and translate results into Record.

    Implement search() to satisfy the SourceAdapter port. Example skeleton:

        class BioRxivMcp(McpSourceAdapter):
            name = "mcp:biorxiv"
            def search(self, query, tag, since, limit):
                hits = self.client.call("search_preprints", {"query": query, ...})
                for h in hits:
                    yield Record(uid=norm_doi(h["doi"]) or f"{self.name}:{h['id']}",
                                 doi=norm_doi(h.get("doi")), title=h["title"],
                                 year=h.get("year"), container="bioRxiv",
                                 source=self.name, surfaced_by=tag, url=h["url"],
                                 relevance_hint=relevance_hint(h["title"], tag), raw=h)
    """
    name = "mcp:unconfigured"
    def search(self, query, tag, since, limit):  # pragma: no cover - seam
        raise NotImplementedError(
            "Wire an MCP client here. See McpSourceAdapter docstring. "
            "Crossref + PubMed already cover keyworded DOI discovery out of the box."
        )


# --------------------------------------------------------------- keyword extraction
SKIP_CELL0 = {"score", "instrument", "token", "current", "superseded", "contested", "unverified"}

def extract_keywords(md_path: str) -> list[tuple[str, str]]:
    """Returns (tag, query) pairs from the reference doc's score tables.
    tag   = abbreviation (for provenance), query = full name or disambiguated abbrev.
    """
    out: dict[str, str] = {}
    for line in open(md_path, encoding="utf-8").read().splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        c0 = cells[0]
        if c0.lower() in SKIP_CELL0 or set(c0) <= set("-: "):
            continue
        if "Key ref" in cells or "Purpose" in cells or "Note" in cells:
            continue  # header row
        # tag: first variant, first token-ish (strip roman/numeric ranges)
        tag = re.split(r"[/(]", c0)[0].strip()
        tag = re.sub(r"\s+(I+|[0-9]).*$", "", tag).strip() or c0
        full = cells[1]
        if full in {"—", "-", ""} or full.startswith("(") or full.lower().startswith("see "):
            query = f"{tag} critical care"
        else:
            query = re.split(r"\s*\(", full)[0].strip()
            if len(query) < 8:                       # short full names collide; disambiguate
                query = f"{query} critical care"
        out.setdefault(tag, query)
    return sorted(out.items())


# ------------------------------------------------------------------------- orchestrate
def build_adapters(names: list[str], mailto: str, api_key: str | None) -> list[SourceAdapter]:
    reg = {"crossref": lambda: CrossrefAdapter(mailto),
           "pubmed": lambda: PubMedAdapter(mailto, api_key)}
    adapters = []
    for n in names:
        if n not in reg:
            print(f"  ! unknown source '{n}' (have: {', '.join(reg)}; MCP via McpSourceAdapter)", file=sys.stderr)
            continue
        adapters.append(reg[n]())
    return adapters


def run_discovery(adapters, store: Store, keywords, since, limit, dry_run=False):
    started = NOW()
    ins = upd = 0
    for tag, query in keywords:
        for ad in adapters:
            try:
                for rec in ad.search(query, tag, since, limit):
                    if dry_run:
                        print(f"  [{ad.name}] {tag:14} {rec.year} {rec.doi or rec.uid}  {rec.title[:70]}")
                        continue
                    res = store.upsert(rec)
                    ins += res == "inserted"
                    upd += res == "updated"
            except Exception as e:  # noqa: BLE001
                print(f"  ! {ad.name} failed on '{tag}': {e}", file=sys.stderr)
    if not dry_run:
        store.log_run([a.name for a in adapters], len(keywords), ins, upd, started)
    return ins, upd


# ------------------------------------------------------------------------------- cli
def main() -> int:
    ap = argparse.ArgumentParser(description="Discovery harvester for a living reference DB.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--keywords-from", default="SCORES.md")
    common.add_argument("--db", default="living_refs.db")
    common.add_argument("--mailto", default="researcher@example.org",
                        help="used for Crossref polite pool + NCBI etiquette")

    pk = sub.add_parser("keywords", parents=[common], help="show extracted keywords (no network)")

    pd = sub.add_parser("discover", parents=[common], help="harvest DOIs into the living DB")
    pd.add_argument("--sources", default="crossref,pubmed")
    pd.add_argument("--since", type=int, default=2023)
    pd.add_argument("--limit", type=int, default=8, help="max hits per keyword per source")
    pd.add_argument("--ncbi-api-key", default=None)
    pd.add_argument("--dry-run", action="store_true")

    pr = sub.add_parser("report", parents=[common], help="view the living DB")
    pr.add_argument("--triage", default=None, choices=["new", "candidate", "relevant", "irrelevant", "linked"])
    pr.add_argument("--new-only", action="store_true", help="only first-time-seen records")
    pr.add_argument("--limit", type=int, default=40)

    args = ap.parse_args()
    kws = extract_keywords(args.keywords_from)

    if args.cmd == "keywords":
        print(f"{len(kws)} keyword(s) from {args.keywords_from}:")
        for tag, q in kws:
            print(f"  {tag:16} -> query: {q}")
        return 0

    store = Store(args.db)

    if args.cmd == "discover":
        adapters = build_adapters(args.sources.split(","), args.mailto, args.ncbi_api_key)
        if not adapters:
            print("no usable sources", file=sys.stderr); return 1
        print(f"discovering: {len(kws)} keywords x {len(adapters)} source(s), since {args.since}, "
              f"<= {args.limit}/kw/source -> {args.db}")
        ins, upd = run_discovery(adapters, store, kws, args.since, args.limit, args.dry_run)
        if not args.dry_run:
            print(f"done: +{ins} new, {upd} refreshed. (discovery only — triage is yours.)")
        return 0

    if args.cmd == "report":
        rows = store.report(args.triage, args.new_only, args.limit)
        print(f"{len(rows)} record(s){' [new]' if args.new_only else ''}"
              f"{' triage='+args.triage if args.triage else ''}:")
        for r in rows:
            flag = "*" if r["relevance_hint"] else " "
            print(f" {flag}[{r['triage']:9}] {r['year'] or '????'} {r['doi'] or r['uid']}")
            print(f"     {r['title'][:88]}")
            if r["relevance_hint"]:
                print(f"     ↳ {r['relevance_hint']}  (seen x{r['times_seen']}, src {r['source']})")
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
