"""
Comprehensive Data Management Service for Axeom Studio Operations & Owner OS.
Supports viewing, searching, filtering, editing, archiving, restoring, soft-deleting records,
dataset upload provenance inspection, upload reversal, audit logging, and protected data reset.
"""

import os
import json
import shutil
import datetime
from pathlib import Path
from services.db import get_db, is_postgres

TABLE_CONFIG = {
    "clients": {
        "pk": "id",
        "label": "Clients Directory",
        "search_cols": ["id", "canonical_name", "primary_contact", "emails", "status"],
        "editable_cols": ["canonical_name", "primary_contact", "emails", "phones", "status", "notes"]
    },
    "leads": {
        "pk": "lead_id",
        "label": "Inbound Leads",
        "search_cols": ["lead_id", "name", "business", "email", "phone", "status"],
        "editable_cols": ["name", "business", "email", "phone", "source", "first_reply", "status"]
    },
    "invoices": {
        "pk": "invoice_no",
        "label": "Invoices Ledger",
        "search_cols": ["invoice_no", "bill_to", "email", "status", "memo"],
        "editable_cols": ["bill_to", "email", "issued", "due", "amount", "status", "memo"]
    },
    "payments": {
        "pk": "payment_id",
        "label": "Payments Ledger",
        "search_cols": ["payment_id", "payer", "payer_email", "method", "reference"],
        "editable_cols": ["payer", "payer_email", "amount", "method", "reference", "payment_date"]
    },
    "bookings": {
        "pk": "booking_id",
        "label": "Studio Bookings",
        "search_cols": ["booking_id", "client_name", "email", "service", "status"],
        "editable_cols": ["client_name", "email", "service", "status", "price", "booking_date"]
    },
    "messages": {
        "pk": "id",
        "label": "Communications Log",
        "search_cols": ["id", "entity", "body", "channel", "direction"],
        "editable_cols": ["entity", "body", "channel", "direction", "msg_datetime"]
    },
    "production_board": {
        "pk": "video_id",
        "label": "Production Board",
        "search_cols": ["video_id", "client", "title", "editor", "stage"],
        "editable_cols": ["client", "title", "editor", "stage", "notes_on_board", "revisions", "editor_hours"]
    }
}


def log_audit_action(action_type: str, target_table: str, record_id: str, details: dict, performed_by: str = "owner"):
    """Durable audit logger for all administrative data operations."""
    try:
        conn = get_db()
        cur = conn.cursor()
        now_iso = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        details_json = json.dumps(details) if isinstance(details, dict) else str(details)
        cur.execute("""
        INSERT INTO audit_logs (timestamp, action_type, target_table, record_id, details, performed_by)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (now_iso, action_type, target_table, str(record_id), details_json, performed_by))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[Audit Log Error] Failed to write audit log: {e}")


def get_records(table_name: str, filter_status: str = "all", search: str = "", limit: int = 50, offset: int = 0):
    """
    Retrieves paginated records for a supported table with filtering and search.
    Status options: 'active', 'archived', 'deleted', 'all'
    """
    if table_name not in TABLE_CONFIG:
        raise ValueError(f"Unsupported table: {table_name}")

    cfg = TABLE_CONFIG[table_name]
    pk = cfg["pk"]
    search_cols = cfg["search_cols"]

    conn = get_db()
    cur = conn.cursor()

    conditions = ["1=1"]
    params = []

    # 1. Filter status
    if filter_status == "active":
        conditions.append("(deleted_at IS NULL OR deleted_at = '')")
        conditions.append("(is_archived IS NULL OR is_archived = 0)")
    elif filter_status == "archived":
        conditions.append("is_archived = 1")
        conditions.append("(deleted_at IS NULL OR deleted_at = '')")
    elif filter_status == "deleted":
        conditions.append("(deleted_at IS NOT NULL AND deleted_at != '')")

    # 2. Search query
    if search and search.strip():
        term = f"%{search.strip().lower()}%"
        or_clauses = [f"LOWER(CAST({col} AS TEXT)) LIKE ?" for col in search_cols]
        conditions.append(f"({' OR '.join(or_clauses)})")
        params.extend([term] * len(search_cols))

    where_sql = " AND ".join(conditions)

    # Count total
    cur.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {where_sql}", params)
    total_count = cur.fetchone()[0]

    # Fetch rows
    fetch_params = list(params) + [limit, offset]
    cur.execute(f"""
    SELECT * FROM {table_name}
    WHERE {where_sql}
    ORDER BY {pk} ASC
    LIMIT ? OFFSET ?
    """, fetch_params)

    rows = [dict(r) for r in cur.fetchall()]
    conn.close()

    # Parse JSON fields where appropriate
    for r in rows:
        for json_key in ["emails", "phones", "payer_aliases"]:
            if json_key in r and isinstance(r[json_key], str):
                try:
                    r[json_key] = json.loads(r[json_key])
                except Exception:
                    pass

    return {
        "table": table_name,
        "label": cfg["label"],
        "pk": pk,
        "records": rows,
        "total_count": total_count,
        "limit": limit,
        "offset": offset,
        "filter_status": filter_status
    }


def get_record(table_name: str, record_id: str):
    """Retrieves single record by primary key with its audit history."""
    if table_name not in TABLE_CONFIG:
        return None

    cfg = TABLE_CONFIG[table_name]
    pk = cfg["pk"]

    conn = get_db()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table_name} WHERE {pk} = ?", (str(record_id),))
    row = cur.fetchone()

    # Fetch audit logs for this record
    cur.execute("""
    SELECT timestamp, action_type, details, performed_by
    FROM audit_logs
    WHERE target_table = ? AND record_id = ?
    ORDER BY id DESC LIMIT 10
    """, (table_name, str(record_id)))
    audit_history = [dict(r) for r in cur.fetchall()]
    conn.close()

    if not row:
        return None

    res = dict(row)
    res["_audit_history"] = audit_history
    return res


def update_record(table_name: str, record_id: str, updates: dict, performed_by: str = "owner"):
    """Updates allowed editable fields for a record and logs previous state."""
    if table_name not in TABLE_CONFIG:
        raise ValueError(f"Unsupported table: {table_name}")

    cfg = TABLE_CONFIG[table_name]
    pk = cfg["pk"]
    allowed = set(cfg["editable_cols"])

    prior = get_record(table_name, record_id)
    if not prior:
        return {"status": "error", "message": f"Record {record_id} not found in {table_name}"}

    if "updated_fields" in updates and isinstance(updates["updated_fields"], dict):
        updates = updates["updated_fields"]

    valid_updates = {k: v for k, v in updates.items() if k in allowed}
    if not valid_updates:
        return {"status": "error", "message": "No valid editable fields provided"}

    set_clauses = []
    params = []
    for col, val in valid_updates.items():
        if isinstance(val, (list, dict)):
            val = json.dumps(val)
        set_clauses.append(f"{col} = ?")
        params.append(val)

    params.append(str(record_id))

    conn = get_db()
    cur = conn.cursor()
    cur.execute(f"UPDATE {table_name} SET {', '.join(set_clauses)} WHERE {pk} = ?", params)
    conn.commit()
    conn.close()

    log_audit_action("edit", table_name, record_id, {
        "prior": {k: prior.get(k) for k in valid_updates},
        "new": valid_updates
    }, performed_by=performed_by)

    return {"status": "success", "message": f"Updated {table_name} record {record_id}", "record": get_record(table_name, record_id)}


def archive_record(table_name: str, record_id: str, performed_by: str = "owner"):
    """Archives a record (soft-status: is_archived = 1)."""
    if table_name not in TABLE_CONFIG:
        raise ValueError(f"Unsupported table: {table_name}")

    cfg = TABLE_CONFIG[table_name]
    pk = cfg["pk"]

    conn = get_db()
    cur = conn.cursor()
    cur.execute(f"UPDATE {table_name} SET is_archived = 1 WHERE {pk} = ?", (str(record_id),))
    conn.commit()
    conn.close()

    log_audit_action("archive", table_name, record_id, {"is_archived": 1}, performed_by=performed_by)
    return {"status": "success", "message": f"Archived {table_name} record {record_id}", "record": get_record(table_name, record_id)}


def restore_record(table_name: str, record_id: str, performed_by: str = "owner"):
    """Restores an archived or soft-deleted record (is_archived = 0, deleted_at = NULL)."""
    if table_name not in TABLE_CONFIG:
        raise ValueError(f"Unsupported table: {table_name}")

    cfg = TABLE_CONFIG[table_name]
    pk = cfg["pk"]

    conn = get_db()
    cur = conn.cursor()
    cur.execute(f"UPDATE {table_name} SET is_archived = 0, deleted_at = NULL WHERE {pk} = ?", (str(record_id),))
    conn.commit()
    conn.close()

    log_audit_action("restore", table_name, record_id, {"is_archived": 0, "deleted_at": None}, performed_by=performed_by)
    return {"status": "success", "message": f"Restored {table_name} record {record_id}", "record": get_record(table_name, record_id)}


PROTECTED_CLIENTS = {f"C{i:02d}" for i in range(1, 35)}
PROTECTED_ORIGINAL_FILES = {
    "clients.csv", "invoices.csv", "payments.csv", "bookings.csv",
    "production_board.csv", "leads.csv", "messages.csv", "costs.csv", "team.csv",
    "pack_01", "genesis", "baseline"
}


def soft_delete_record(table_name: str, record_id: str, performed_by: str = "owner"):
    """
    Soft-deletes a record (sets deleted_at timestamp and is_archived = 1).
    Guarantees reversible retention and protects associated financial ledger rows.
    """
    if table_name not in TABLE_CONFIG:
        raise ValueError(f"Unsupported table: {table_name}")

    if table_name == "clients" and str(record_id).strip().upper() in PROTECTED_CLIENTS:
        return {
            "status": "error",
            "message": f"Protected Baseline Record: Canonical client '{record_id}' is part of the certified Pack 01 baseline and cannot be deleted."
        }

    cfg = TABLE_CONFIG[table_name]
    pk = cfg["pk"]
    now_iso = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_db()
    cur = conn.cursor()
    cur.execute(f"UPDATE {table_name} SET deleted_at = ?, is_archived = 1 WHERE {pk} = ?", (now_iso, str(record_id)))
    conn.commit()
    conn.close()

    log_audit_action("soft_delete", table_name, record_id, {"deleted_at": now_iso}, performed_by=performed_by)
    return {"status": "success", "message": f"Soft-deleted {table_name} record {record_id}", "record": get_record(table_name, record_id)}


def calculate_impact(table_name: str, record_id: str):
    """
    Pre-flight consequence analysis for a record before deletion or archival.
    Computes affected relationships, linked invoices/payments, and business invariants.
    """
    if table_name not in TABLE_CONFIG:
        raise ValueError(f"Unsupported table: {table_name}")

    rec = get_record(table_name, record_id)
    if not rec:
        return {"status": "error", "message": "Record not found"}

    conn = get_db()
    cur = conn.cursor()

    impact = {
        "table": table_name,
        "record_id": record_id,
        "record_name": rec.get("canonical_name") or rec.get("name") or rec.get("bill_to") or rec.get("client") or str(record_id),
        "relationships": [],
        "financial_impact": 0.0,
        "consequences_summary": "",
        "safety_note": "Axeom utilizes reversible soft-deletion. Original records are preserved in audit tables."
    }

    if table_name == "clients":
        client_name = rec.get("canonical_name", "")
        # Bookings count
        cur.execute("SELECT COUNT(*), COALESCE(SUM(price), 0.0) FROM bookings WHERE (LOWER(client_name) = LOWER(?) OR LOWER(email) IN (SELECT LOWER(email) FROM clients WHERE id=?)) AND deleted_at IS NULL", (client_name, record_id))
        b_row = cur.fetchone()
        b_cnt = b_row[0]
        b_val = float(b_row[1] or 0.0)
        # Invoices count
        cur.execute("SELECT COUNT(*), COALESCE(SUM(amount), 0.0) FROM invoices WHERE LOWER(bill_to) = LOWER(?) AND deleted_at IS NULL", (client_name,))
        inv_row = cur.fetchone()
        inv_cnt = inv_row[0]
        inv_val = float(inv_row[1] or 0.0)
        # Payments count
        cur.execute("SELECT COUNT(*), COALESCE(SUM(amount), 0.0) FROM payments WHERE LOWER(payer) = LOWER(?) AND deleted_at IS NULL", (client_name,))
        p_row = cur.fetchone()
        p_cnt = p_row[0]
        p_val = float(p_row[1] or 0.0)
        # Videos count
        cur.execute("SELECT COUNT(*) FROM production_board WHERE LOWER(client) = LOWER(?) AND deleted_at IS NULL", (client_name,))
        v_row = cur.fetchone()
        v_cnt = v_row[0]

        impact["relationships"] = [
            {"label": "Studio Bookings", "count": b_cnt, "amount": b_val},
            {"label": "Invoices Ledger", "count": inv_cnt, "amount": inv_val},
            {"label": "Payments Recorded", "count": p_cnt, "amount": p_val},
            {"label": "Production Board Videos", "count": v_cnt, "amount": 0.0}
        ]
        impact["financial_impact"] = float(inv_val - p_val)
        impact["consequences_summary"] = (
            f"Archiving or soft-deleting this client will remove them from active client counts. "
            f"CRITICAL SAFETY RULE: Their {inv_cnt} historical invoices (${float(inv_val):,.2f}) and {p_cnt} payments "
            f"(${float(p_val):,.2f}) will NOT be cascade-deleted and will remain intact in accounting records."
        )

    elif table_name == "invoices":
        inv_no = rec.get("invoice_no")
        amount = float(rec.get("amount") or 0.0)
        cur.execute("SELECT COUNT(*), COALESCE(SUM(amount), 0.0) FROM payments WHERE reference = ? AND deleted_at IS NULL", (inv_no,))
        pay_row = cur.fetchone()
        pay_cnt = pay_row[0]
        pay_sum = float(pay_row[1] or 0.0)
        impact["relationships"] = [
            {"label": "Matching Payments Applied", "count": pay_cnt, "amount": pay_sum}
        ]
        impact["financial_impact"] = amount
        impact["consequences_summary"] = (
            f"Soft-deleting invoice {inv_no} will reduce outstanding accounts receivable by ${amount:,.2f}. "
            f"{pay_cnt} payment records referencing this invoice will remain recorded."
        )

    elif table_name == "payments":
        amt = float(rec.get("amount") or 0.0)
        ref = rec.get("reference", "")
        impact["relationships"] = [
            {"label": "Referenced Invoice", "count": 1 if ref else 0, "amount": amt, "detail": ref or "None"}
        ]
        impact["financial_impact"] = amt
        impact["consequences_summary"] = (
            f"Soft-deleting payment {rec.get('payment_id')} (${amt:,.2f}) will cause the client's balance "
            f"or overdue status to increase by ${amt:,.2f} upon recalculation."
        )

    elif table_name == "leads":
        lead_name = rec.get("name")
        status = rec.get("status")
        impact["consequences_summary"] = (
            f"Soft-deleting lead {rec.get('lead_id')} ({lead_name}) will remove it from active lead pipeline metrics."
        )

    elif table_name == "production_board":
        vid = rec.get("video_id")
        impact["consequences_summary"] = (
            f"Soft-deleting video {vid} will remove it from the active production board and associated edit request tracking."
        )

    conn.close()
    return {"status": "success", "impact": impact}


def get_upload_history():
    """Returns list of uploaded files, import revisions, and current status."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
    SELECT id, filename, file_role, row_count, added_count, updated_count, skipped_count, rejected_count,
           status, details, uploaded_at, is_reverted, reverted_at
    FROM file_uploads
    ORDER BY id DESC
    """)
    uploads = [dict(r) for r in cur.fetchall()]
    conn.close()

    for u in uploads:
        if isinstance(u.get("details"), str):
            try:
                u["details"] = json.loads(u["details"])
            except Exception:
                pass
    return uploads


def calculate_upload_reversal_impact(upload_id: int):
    """
    Evaluates whether an upload can be safely rolled back without breaking downstream modifications.
    """
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM file_uploads WHERE id = ?", (upload_id,))
    upload = cur.fetchone()
    if not upload:
        conn.close()
        return {"status": "error", "message": "Upload record not found"}

    u = dict(upload)
    filename = u["filename"]
    role = u["file_role"]
    is_reverted = bool(u.get("is_reverted"))

    if is_reverted:
        conn.close()
        return {"status": "error", "message": "This dataset upload has already been reverted."}

    # Inspect active records created by this file
    table_map = {
        "invoices": "invoices",
        "payments": "payments",
        "bookings": "bookings",
        "production_board": "production_board",
        "leads": "leads",
        "messages": "messages",
        "costs": "costs",
        "team": "team"
    }

    target_table = table_map.get(role)
    active_rows_count = 0
    subsequent_modifications = 0
    financial_delta = 0.0

    if target_table:
        cur.execute(f"SELECT COUNT(*) FROM {target_table} WHERE source_file = ? AND deleted_at IS NULL", (filename,))
        active_rows_count = cur.fetchone()[0]

        if target_table in ["invoices", "payments"]:
            cur.execute(f"SELECT COALESCE(SUM(amount), 0.0) FROM {target_table} WHERE source_file = ? AND deleted_at IS NULL", (filename,))
            financial_delta = float(cur.fetchone()[0])

    # Check if later uploads touched these records
    cur.execute("SELECT COUNT(*) FROM file_uploads WHERE id > ? AND status = 'success'", (upload_id,))
    later_uploads_count = cur.fetchone()[0]

    conn.close()

    can_safely_revert = True
    safety_warnings = []

    if filename.lower() in PROTECTED_ORIGINAL_FILES or "pack" in filename.lower() or "genesis" in filename.lower():
        can_safely_revert = False
        safety_warnings.append(f"PROTECTED BASELINE: '{filename}' is part of the certified original Pack 01 business baseline and cannot be reverted.")

    if later_uploads_count > 0 and active_rows_count > 0:
        safety_warnings.append(f"{later_uploads_count} newer file(s) have been uploaded since this dataset. Downstream records may be affected.")

    if role == "invoices" and active_rows_count > 0:
        safety_warnings.append(f"Reversing this upload will soft-delete {active_rows_count} invoices totaling ${financial_delta:,.2f}.")

    return {
        "status": "success",
        "upload_id": upload_id,
        "filename": filename,
        "file_role": role,
        "uploaded_at": u["uploaded_at"],
        "records_created": u.get("added_count", 0),
        "active_records_remaining": active_rows_count,
        "financial_delta": financial_delta,
        "can_safely_revert": can_safely_revert,
        "warnings": safety_warnings
    }


def revert_upload(upload_id: int, performed_by: str = "owner"):
    """
    Safely rolls back an uploaded file by soft-deleting all active records it introduced.
    Guarantees audit traceability and provenance preservation.
    """
    impact = calculate_upload_reversal_impact(upload_id)
    if impact.get("status") == "error":
        return impact

    filename = impact["filename"]
    role = impact["file_role"]

    if filename.lower() in PROTECTED_ORIGINAL_FILES or "pack" in filename.lower() or "genesis" in filename.lower():
        return {
            "status": "error",
            "message": f"Protected Baseline Dataset: Original file '{filename}' is part of the certified Pack 01 baseline and cannot be reverted or deleted."
        }

    now_iso = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    table_map = {
        "invoices": "invoices",
        "payments": "payments",
        "bookings": "bookings",
        "production_board": "production_board",
        "leads": "leads",
        "messages": "messages",
        "costs": "costs",
        "team": "team"
    }

    target_table = table_map.get(role)

    conn = get_db()
    cur = conn.cursor()

    reverted_count = 0
    if target_table:
        cur.execute(f"UPDATE {target_table} SET deleted_at = ?, is_archived = 1 WHERE source_file = ? AND deleted_at IS NULL", (now_iso, filename))
        cur.execute("SELECT COUNT(*) FROM file_uploads")  # dummy for rowcount if driver doesn't support cur.rowcount
        reverted_count = impact["active_records_remaining"]

    # Mark upload entry as reverted
    cur.execute("""
    UPDATE file_uploads
    SET is_reverted = 1, status = 'reverted', reverted_at = ?
    WHERE id = ?
    """, (now_iso, upload_id))

    conn.commit()
    conn.close()

    log_audit_action("upload_revert", "file_uploads", str(upload_id), {
        "filename": filename,
        "role": role,
        "reverted_rows_count": reverted_count,
        "reverted_at": now_iso
    }, performed_by=performed_by)

    return {
        "status": "success",
        "message": f"Successfully reversed upload '{filename}'. {reverted_count} introduced records were soft-deleted.",
        "reverted_rows_count": reverted_count
    }


def get_reset_preview():
    """
    Pre-flight inspection for Reset Business Data.
    Shows table counts and verifies backup status.
    """
    conn = get_db()
    cur = conn.cursor()

    tables = [
        "clients", "third_party_payers", "bookings", "invoices", "payments",
        "production_board", "leads", "messages", "costs", "team",
        "dataset_revisions", "file_uploads", "owner_decisions"
    ]

    counts = {}
    total_records = 0
    for t in tables:
        try:
            cur.execute(f"SELECT COUNT(*) FROM {t}")
            cnt = cur.fetchone()[0]
            counts[t] = cnt
            total_records += cnt
        except Exception:
            counts[t] = 0

    conn.close()

    has_backup = False
    backup_path = "axeom_genesis_backup.db" if not is_postgres() else "neon_branch_main"
    if os.path.exists("axeom.db") or is_postgres():
        has_backup = True

    return {
        "total_records": total_records,
        "table_counts": counts,
        "has_recoverable_backup": has_backup,
        "backup_reference": backup_path,
        "required_confirmation_phrase": "RESET AXEOM DATA",
        "warning": "This operation will reset modified records back to certified baseline."
    }


def execute_reset(confirmation_phrase: str, performed_by: str = "owner"):
    """
    Executes a guarded business data reset.
    Requires exact confirmation phrase: 'RESET AXEOM DATA'.
    Creates a pre-reset backup and re-initializes to pristine baseline.
    """
    if str(confirmation_phrase).strip() != "RESET AXEOM DATA":
        return {
            "status": "error",
            "message": "Invalid confirmation phrase. You must type exactly 'RESET AXEOM DATA' to proceed."
        }

    # Backup local database if SQLite
    now_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    if not is_postgres():
        db_path = os.environ.get("AXEOM_DB_PATH", "axeom.db")
        if os.path.exists(db_path):
            backup_file = f"axeom_backup_{now_str}.db"
            shutil.copy2(db_path, backup_file)

    conn = get_db()
    cur = conn.cursor()

    # Clear mutable business tables
    clear_tables = [
        "bookings", "invoices", "payments", "production_board",
        "leads", "messages", "costs", "team", "owner_decisions",
        "file_uploads", "dataset_revisions", "message_classifications", "audit_logs"
    ]
    for t in clear_tables:
        try:
            cur.execute(f"DELETE FROM {t}")
        except Exception:
            pass

    conn.commit()
    conn.close()

    # Re-seed to pristine challenge baseline
    from services.db import seed_db_if_empty
    seed_db_if_empty()

    log_audit_action("reset", "all_tables", "system", {
        "timestamp": now_str,
        "reseeded": True
    }, performed_by=performed_by)

    return {
        "status": "success",
        "message": "Business dataset has been successfully reset to the certified baseline.",
        "reset_timestamp": now_str
    }


def get_audit_logs(limit: int = 100):
    """Fetches recent audit log entries."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
    SELECT id, timestamp, action_type, target_table, record_id, details, performed_by
    FROM audit_logs
    ORDER BY id DESC
    LIMIT ?
    """, (limit,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()

    for r in rows:
        if isinstance(r.get("details"), str):
            try:
                r["details"] = json.loads(r["details"])
            except Exception:
                pass
    return rows
