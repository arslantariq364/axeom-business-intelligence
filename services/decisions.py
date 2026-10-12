"""
Durable persistence for owner operational decisions.
Saved in SQLite table 'owner_decisions' across restarts and recomputations.
"""

import datetime
from services.db import get_db

def get_all_decisions():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM owner_decisions")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {r['action_id']: r for r in rows}

def get_decision(action_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM owner_decisions WHERE action_id = ?", (action_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return dict(row)
    return {
        "action_id": action_id,
        "decision_type": "generic",
        "status": "pending",
        "owner_notes": "",
        "updated_at": ""
    }

def save_decision(action_id, decision_type, status, owner_notes=""):
    now_iso = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO owner_decisions (action_id, decision_type, status, owner_notes, updated_at)
    VALUES (?, ?, ?, ?, ?)
    ON CONFLICT(action_id) DO UPDATE SET
        decision_type = excluded.decision_type,
        status = excluded.status,
        owner_notes = excluded.owner_notes,
        updated_at = excluded.updated_at
    """, (action_id, decision_type, status, owner_notes, now_iso))
    conn.commit()
    conn.close()
    return {
        "action_id": action_id,
        "decision_type": decision_type,
        "status": status,
        "owner_notes": owner_notes,
        "updated_at": now_iso
    }
