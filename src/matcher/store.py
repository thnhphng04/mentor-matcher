"""Pluggable persistence for enrichment tags.

If ``SUPABASE_URL`` and ``SUPABASE_KEY`` are set, enriched tags are stored in a
Supabase (Postgres) table so in-app enrichment survives redeploys. Otherwise the
caller falls back to a local JSON file. Table schema is in ``supabase_schema.sql``:

    enrichment_tags(kind text, id text, tags jsonb, updated_at timestamptz,
                    primary key (kind, id))
"""
from __future__ import annotations

import os
from typing import Dict, Optional

TABLE = "enrichment_tags"
DATASET_TABLE = "dataset_rows"
_PAGE = 1000  # PostgREST default max rows per request


def configured() -> bool:
    return bool(os.environ.get("SUPABASE_URL") and os.environ.get("SUPABASE_KEY"))


def _client():
    if not configured():
        return None
    try:
        from supabase import create_client
        return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
    except Exception:
        return None


def remote_load(kind: str) -> Optional[Dict[str, dict]]:
    """Return {id: tags} from Supabase, or None if Supabase isn't in use."""
    sb = _client()
    if sb is None:
        return None
    out: Dict[str, dict] = {}
    start = 0
    while True:
        rows = (sb.table(TABLE).select("id,tags").eq("kind", kind)
                .range(start, start + _PAGE - 1).execute()).data or []
        for r in rows:
            out[r["id"]] = r["tags"]
        if len(rows) < _PAGE:
            break
        start += _PAGE
    return out


def remote_save(kind: str, data: Dict[str, dict]) -> bool:
    """Upsert {id: tags} into Supabase. Returns False if Supabase isn't in use."""
    sb = _client()
    if sb is None:
        return False
    payload = [{"kind": kind, "id": cid, "tags": rec} for cid, rec in data.items()]
    for i in range(0, len(payload), 500):
        sb.table(TABLE).upsert(payload[i:i + 500], on_conflict="kind,id").execute()
    return True


def backend_name() -> str:
    return "Supabase" if configured() else "local disk"


# --------------------------------------------------------------------------
# Raw dataset rows (the original CSV data) — so uploads persist in Supabase.
# --------------------------------------------------------------------------
def dataset_load(kind: str) -> Optional[list]:
    """Return the raw rows (list of dicts) for ``kind`` from Supabase, or None
    if Supabase isn't in use / the table is empty / unavailable."""
    sb = _client()
    if sb is None:
        return None
    try:
        out = []
        start = 0
        while True:
            rows = (sb.table(DATASET_TABLE).select("data").eq("kind", kind)
                    .range(start, start + _PAGE - 1).execute()).data or []
            out.extend(r["data"] for r in rows)
            if len(rows) < _PAGE:
                break
            start += _PAGE
        return out or None
    except Exception:
        return None


def dataset_replace(kind: str, rows: list) -> bool:
    """Replace all ``kind`` rows in Supabase with ``rows`` (each a dict with an
    'ID' key). Empty ``rows`` just clears them. Returns False if not in use."""
    sb = _client()
    if sb is None:
        return False
    try:
        sb.table(DATASET_TABLE).delete().eq("kind", kind).execute()
        payload = [{"kind": kind, "id": str(r.get("ID")), "data": r} for r in rows]
        for i in range(0, len(payload), 500):
            sb.table(DATASET_TABLE).insert(payload[i:i + 500]).execute()
        return True
    except Exception:
        return False
