"""
Storage backend — uses Supabase when credentials are present, SQLite otherwise.
SQLite works for local use. Supabase is required for hosted persistent storage.
"""
import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(__file__), "scrapes.db")


def _supabase():
    try:
        import streamlit as st
        from supabase import create_client
        url = st.secrets.get("SUPABASE_URL", "")
        key = st.secrets.get("SUPABASE_KEY", "")
        if url and key:
            return create_client(url, key)
    except Exception:
        pass
    return None


def _sqlite():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS scrapes (
            id         TEXT PRIMARY KEY,
            query      TEXT,
            params     TEXT,
            results    TEXT,
            session_id TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    return conn


# ── Write ────────────────────────────────────────────────────────────────────

def save_scrape(query, params, results, session_id="unknown"):
    scrape_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    sb = _supabase()
    if sb:
        sb.table("scrapes").insert({
            "id": scrape_id,
            "query": query,
            "params": params,
            "results": results,
            "session_id": session_id,
            "created_at": now,
        }).execute()
    else:
        conn = _sqlite()
        conn.execute(
            "INSERT INTO scrapes VALUES (?,?,?,?,?,?)",
            (scrape_id, query, json.dumps(params), json.dumps(results), session_id, now),
        )
        conn.commit()
        conn.close()


# ── Read ─────────────────────────────────────────────────────────────────────

def list_scrapes():
    """Return all scrapes newest-first. Each row includes parsed results."""
    sb = _supabase()
    if sb:
        resp = sb.table("scrapes").select("*").order("created_at", desc=True).execute()
        return [_normalize_sb(r) for r in resp.data]
    else:
        conn = _sqlite()
        rows = conn.execute(
            "SELECT id,query,params,results,session_id,created_at FROM scrapes ORDER BY created_at DESC"
        ).fetchall()
        conn.close()
        return [_normalize_sqlite(r) for r in rows]


def get_scrape(scrape_id):
    sb = _supabase()
    if sb:
        resp = sb.table("scrapes").select("*").eq("id", scrape_id).execute()
        return _normalize_sb(resp.data[0]) if resp.data else None
    else:
        conn = _sqlite()
        row = conn.execute(
            "SELECT id,query,params,results,session_id,created_at FROM scrapes WHERE id=?",
            (scrape_id,),
        ).fetchone()
        conn.close()
        return _normalize_sqlite(row) if row else None


# ── Normalizers ───────────────────────────────────────────────────────────────

def _normalize_sb(r):
    results = r.get("results") or []
    if isinstance(results, str):
        results = json.loads(results)
    return {
        "id": r["id"],
        "query": r["query"],
        "params": r.get("params") or {},
        "results": results,
        "session_id": r.get("session_id", ""),
        "created_at": r.get("created_at", ""),
        "post_count": len(results),
    }


def _normalize_sqlite(row):
    results = json.loads(row[3]) if row[3] else []
    return {
        "id": row[0],
        "query": row[1],
        "params": json.loads(row[2]) if row[2] else {},
        "results": results,
        "session_id": row[4] or "",
        "created_at": row[5] or "",
        "post_count": len(results),
    }
