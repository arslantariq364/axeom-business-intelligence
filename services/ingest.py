"""
Robust, idempotent file ingestion service for Axeom Studio.
Unified pipeline for initial data seeding and ongoing 'Add New Files' uploads.
Guarantees schema sniffing, staged transactions, deduplication, and revision tracking.
"""

import hashlib
import csv
import io
import re
import os
import json
import datetime
from pathlib import Path
from services.db import get_db, clean_float, get_current_revision

UPLOAD_DIR_ENV = os.environ.get("AXEOM_UPLOAD_DIR")
if UPLOAD_DIR_ENV:
    UPLOAD_DIR = Path(UPLOAD_DIR_ENV)
else:
    try:
        UPLOAD_DIR = Path("uploads")
        UPLOAD_DIR.mkdir(exist_ok=True)
    except OSError:
        UPLOAD_DIR = Path("/tmp/axeom_uploads")
        UPLOAD_DIR.mkdir(exist_ok=True)

MAX_UPLOAD_SIZE_BYTES = 16 * 1024 * 1024  # 16 MB limit

REQUIRED_COLUMNS = {
    "bookings": ["booking_id", "client_name"],
    "invoices": ["invoice_no", "bill_to", "amount"],
    "payments": ["payment_id", "payer", "amount"],
    "production_board": ["video_id", "client"],
    "leads": ["lead_id", "name"],
    "costs": ["item", "cost"],
    "team": ["name", "role"]
}

def decode_bytes(content_bytes):
    """Attempts UTF-8, then UTF-8-sig (BOM), then Latin-1 decoding."""
    for enc in ["utf-8", "utf-8-sig", "latin-1", "cp1252"]:
        try:
            return content_bytes.decode(enc)
        except UnicodeDecodeError:
            continue
    return content_bytes.decode("utf-8", errors="replace")

def detect_file_role(filename, text_content):
    """
    Sniffs content headers and format signatures to detect file role.
    Falls back to filename hints only if header sniffing is ambiguous.
    """
    fn_lower = filename.lower()
    first_few_lines = [line.strip() for line in text_content.strip().splitlines()[:5] if line.strip()]
    if not first_few_lines:
        return "unknown"

    # 1. Check for messages.txt pattern (starts with bracketed timestamp)
    if re.search(r"^\[\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}\]", first_few_lines[0]):
        return "messages"

    # 2. Check CSV headers
    header_raw = first_few_lines[0].lower()
    headers = [h.strip().strip('"').strip("'") for h in header_raw.split(",")]

    header_set = set(headers)

    if "invoice_no" in header_set and ("amount" in header_set or "bill_to" in header_set):
        return "invoices"
    if "payment_id" in header_set and ("amount" in header_set or "payer" in header_set):
        return "payments"
    if "booking_id" in header_set and ("client_name" in header_set or "service" in header_set):
        return "bookings"
    if "video_id" in header_set and ("client" in header_set or "title" in header_set or "editor" in header_set):
        return "production_board"
    if "lead_id" in header_set and ("name" in header_set or "business" in header_set or "source" in header_set):
        return "leads"
    if "item" in header_set and "cost" in header_set:
        return "costs"
    if "name" in header_set and "role" in header_set and "pay" in header_set:
        return "team"

    # 3. Filename heuristics fallback
    if "invoice" in fn_lower: return "invoices"
    if "payment" in fn_lower: return "payments"
    if "booking" in fn_lower: return "bookings"
    if "production" in fn_lower or "board" in fn_lower: return "production_board"
    if "lead" in fn_lower: return "leads"
    if "message" in fn_lower: return "messages"
    if "cost" in fn_lower: return "costs"
    if "team" in fn_lower: return "team"

    return "unknown"

def ingest_file_path(file_path):
    """Helper to ingest a file directly from a filesystem path."""
    p = Path(file_path)
    if not p.exists():
        return {"status": "error", "message": f"File not found: {p}"}
    with open(p, "rb") as f:
        content = f.read()
    return process_file_upload(p.name, content)

def process_file_upload(filename, content_bytes):
    """
    Main idempotent ingestion processor.
    Handles size checks, hashing, staging, deduplication, row changes, and revisions.
    """
    if len(content_bytes) > MAX_UPLOAD_SIZE_BYTES:
        return {
            "status": "error",
            "message": f"File '{filename}' exceeds maximum allowable size of 16MB.",
            "file_role": "unknown",
            "added": 0, "updated": 0, "skipped": 0, "rejected": 0, "needs_review": 0,
            "errors": ["File size limit exceeded"]
        }

    sha256 = hashlib.sha256(content_bytes).hexdigest()
    text = decode_bytes(content_bytes)
    role = detect_file_role(filename, text)
    now_iso = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Save physical audit copy if filesystem allows (serverless fallback)
    try:
        audit_filename = f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
        audit_path = UPLOAD_DIR / audit_filename
        with open(audit_path, "wb") as f:
            f.write(content_bytes)
    except OSError:
        pass

    if role == "unknown":
        return {
            "status": "error",
            "message": f"Could not determine valid schema or role for '{filename}'.",
            "file_role": "unknown",
            "added": 0, "updated": 0, "skipped": 0, "rejected": 0, "needs_review": 0,
            "errors": ["Unknown schema format"]
        }

    conn = get_db()
    cur = conn.cursor()

    # 1. Idempotency Check: Exact duplicate file hash
    cur.execute("SELECT id, filename, file_role, row_count, added_count FROM file_uploads WHERE sha256_hash = ? AND status = 'success'", (sha256,))
    existing_upload = cur.fetchone()
    if existing_upload:
        rev = get_current_revision()
        conn.close()
        return {
            "status": "duplicate_file",
            "message": f"File '{filename}' has already been processed with identical content (SHA-256 match).",
            "file_role": existing_upload["file_role"],
            "sha256": sha256,
            "added": 0,
            "updated": 0,
            "skipped": existing_upload["row_count"],
            "rejected": 0,
            "needs_review": 0,
            "revision_id": rev["revision_id"],
            "errors": []
        }

    # 2. Schema Validation (Headers & Duplicate Headers)
    if role != "messages":
        first_line = text.strip().splitlines()[0]
        raw_headers = [h.strip().strip('"').strip("'") for h in first_line.split(",")]
        
        # Check duplicate headers
        if len(raw_headers) != len(set(raw_headers)):
            conn.close()
            return {
                "status": "error",
                "message": f"Validation Error in '{filename}': Duplicate column headers found in CSV.",
                "file_role": role,
                "added": 0, "updated": 0, "skipped": 0, "rejected": 0, "needs_review": 0,
                "errors": ["Duplicate column headers detected"]
            }

        # Check required columns
        req = REQUIRED_COLUMNS.get(role, [])
        missing = [col for col in req if col not in raw_headers]
        if missing:
            conn.close()
            return {
                "status": "error",
                "message": f"Validation Error in '{filename}': Missing required columns for role '{role}': {', '.join(missing)}.",
                "file_role": role,
                "added": 0, "updated": 0, "skipped": 0, "rejected": 0, "needs_review": 0,
                "errors": [f"Missing required columns: {missing}"]
            }

    # Staged Transaction Execution
    added_count = 0
    updated_count = 0
    skipped_count = 0
    rejected_count = 0
    needs_review_count = 0
    row_errors = []
    new_messages_to_classify = []

    try:
        cur.execute("BEGIN TRANSACTION")

        if role == "invoices":
            reader = csv.DictReader(io.StringIO(text))
            for idx, r in enumerate(reader, start=2):
                inv_no = r.get("invoice_no", "").strip()
                if not inv_no:
                    rejected_count += 1
                    row_errors.append(f"Row {idx}: missing invoice_no")
                    continue
                amt = clean_float(r.get("amount", 0.0))
                bill_to = r.get("bill_to", "").strip()
                email = r.get("email", "").strip()
                issued = r.get("issued", "").strip()
                due = r.get("due", "").strip()
                status = r.get("status", "").strip()
                memo = r.get("memo", "").strip()

                cur.execute("SELECT amount, due, status, bill_to FROM invoices WHERE invoice_no = ?", (inv_no,))
                existing = cur.fetchone()
                if existing is None:
                    cur.execute("""
                    INSERT INTO invoices (invoice_no, bill_to, email, issued, due, amount, status, memo, source_file)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (inv_no, bill_to, email, issued, due, amt, status, memo, filename))
                    added_count += 1
                else:
                    if (existing["amount"] == amt and existing["due"] == due and 
                        existing["status"] == status and existing["bill_to"] == bill_to):
                        skipped_count += 1
                    else:
                        cur.execute("""
                        UPDATE invoices SET bill_to=?, email=?, issued=?, due=?, amount=?, status=?, memo=?, source_file=?
                        WHERE invoice_no=?
                        """, (bill_to, email, issued, due, amt, status, memo, filename, inv_no))
                        updated_count += 1

        elif role == "payments":
            reader = csv.DictReader(io.StringIO(text))
            for idx, r in enumerate(reader, start=2):
                pay_id = r.get("payment_id", "").strip()
                if not pay_id:
                    rejected_count += 1
                    row_errors.append(f"Row {idx}: missing payment_id")
                    continue
                amt = clean_float(r.get("amount", 0.0))
                p_date = r.get("date", "").strip()
                payer = r.get("payer", "").strip()
                payer_email = r.get("payer_email", "").strip()
                method = r.get("method", "").strip()
                ref = r.get("reference", "").strip()

                cur.execute("SELECT amount, reference, method, payment_date FROM payments WHERE payment_id = ?", (pay_id,))
                existing = cur.fetchone()
                if existing is None:
                    cur.execute("""
                    INSERT INTO payments (payment_id, payment_date, payer, payer_email, amount, method, reference, source_file)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (pay_id, p_date, payer, payer_email, amt, method, ref, filename))
                    added_count += 1
                else:
                    if (existing["amount"] == amt and existing["reference"] == ref and 
                        existing["method"] == method and existing["payment_date"] == p_date):
                        skipped_count += 1
                    else:
                        cur.execute("""
                        UPDATE payments SET payment_date=?, payer=?, payer_email=?, amount=?, method=?, reference=?, source_file=?
                        WHERE payment_id=?
                        """, (p_date, payer, payer_email, amt, method, ref, filename, pay_id))
                        updated_count += 1

        elif role == "bookings":
            reader = csv.DictReader(io.StringIO(text))
            for idx, r in enumerate(reader, start=2):
                b_id = r.get("booking_id", "").strip()
                if not b_id:
                    rejected_count += 1
                    row_errors.append(f"Row {idx}: missing booking_id")
                    continue
                price = clean_float(r.get("price", 0.0))
                b_date = r.get("date", "").strip()
                client_name = r.get("client_name", "").strip()
                email = r.get("email", "").strip()
                service = r.get("service", "").strip()
                status = r.get("status", "").strip()

                cur.execute("SELECT price, status, client_name, service FROM bookings WHERE booking_id = ?", (b_id,))
                existing = cur.fetchone()
                if existing is None:
                    cur.execute("""
                    INSERT INTO bookings (booking_id, booking_date, client_name, email, service, status, price, source_file)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (b_id, b_date, client_name, email, service, status, price, filename))
                    added_count += 1
                else:
                    if (existing["price"] == price and existing["status"] == status and 
                        existing["client_name"] == client_name and existing["service"] == service):
                        skipped_count += 1
                    else:
                        cur.execute("""
                        UPDATE bookings SET booking_date=?, client_name=?, email=?, service=?, status=?, price=?, source_file=?
                        WHERE booking_id=?
                        """, (b_date, client_name, email, service, status, price, filename, b_id))
                        updated_count += 1

        elif role == "production_board":
            reader = csv.DictReader(io.StringIO(text))
            for idx, r in enumerate(reader, start=2):
                v_id = r.get("video_id", "").strip()
                if not v_id:
                    rejected_count += 1
                    row_errors.append(f"Row {idx}: missing video_id")
                    continue
                client = r.get("client", "").strip()
                title = r.get("title", "").strip()
                editor = r.get("editor", "").strip()
                stage = r.get("stage", "").strip()
                notes = r.get("notes_on_board", "").strip()
                revs = int(r.get("revisions", 0)) if r.get("revisions") else 0
                hours = clean_float(r.get("editor_hours", 0.0))
                app_on = r.get("client_approved_on", "").strip()
                shoot_b = r.get("shoot_booking", "").strip()

                cur.execute("SELECT stage, notes_on_board, editor_hours, revisions FROM production_board WHERE video_id = ?", (v_id,))
                existing = cur.fetchone()
                if existing is None:
                    cur.execute("""
                    INSERT INTO production_board (video_id, client, title, editor, stage, notes_on_board, revisions, editor_hours, client_approved_on, shoot_booking, source_file)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (v_id, client, title, editor, stage, notes, revs, hours, app_on, shoot_b, filename))
                    added_count += 1
                else:
                    if (existing["stage"] == stage and existing["notes_on_board"] == notes and 
                        existing["editor_hours"] == hours and existing["revisions"] == revs):
                        skipped_count += 1
                    else:
                        cur.execute("""
                        UPDATE production_board SET client=?, title=?, editor=?, stage=?, notes_on_board=?, revisions=?, editor_hours=?, client_approved_on=?, shoot_booking=?, source_file=?
                        WHERE video_id=?
                        """, (client, title, editor, stage, notes, revs, hours, app_on, shoot_b, filename, v_id))
                        updated_count += 1

        elif role == "leads":
            reader = csv.DictReader(io.StringIO(text))
            for idx, r in enumerate(reader, start=2):
                l_id = r.get("lead_id", "").strip()
                if not l_id:
                    rejected_count += 1
                    row_errors.append(f"Row {idx}: missing lead_id")
                    continue
                created = r.get("created", "").strip()
                name = r.get("name", "").strip()
                business = r.get("business", "").strip()
                email = r.get("email", "").strip()
                phone = r.get("phone", "").strip()
                source = r.get("source", "").strip()
                first_reply = r.get("first_reply", "").strip()
                status = r.get("status", "").strip()

                cur.execute("SELECT first_reply, status, source FROM leads WHERE lead_id = ?", (l_id,))
                existing = cur.fetchone()
                if existing is None:
                    cur.execute("""
                    INSERT INTO leads (lead_id, created, name, business, email, phone, source, first_reply, status, source_file)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (l_id, created, name, business, email, phone, source, first_reply, status, filename))
                    added_count += 1
                else:
                    if (existing["first_reply"] == first_reply and existing["status"] == status and existing["source"] == source):
                        skipped_count += 1
                    else:
                        cur.execute("""
                        UPDATE leads SET created=?, name=?, business=?, email=?, phone=?, source=?, first_reply=?, status=?, source_file=?
                        WHERE lead_id=?
                        """, (created, name, business, email, phone, source, first_reply, status, filename, l_id))
                        updated_count += 1

        elif role == "messages":
            header_regex = re.compile(r"^\[(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})\]\s+([A-Z\s]+)\s+(from|to)\s+([^:]+):\s*(.*)$")
            for idx, line in enumerate(text.splitlines(), start=1):
                raw_line = line.strip()
                if not raw_line: continue
                m = header_regex.match(raw_line)
                if m:
                    dt, chan, direction, entity, body = m.groups()
                    content_sig = f"{dt}|{chan.strip()}|{direction.strip()}|{entity.strip()}|{body.strip()}"
                    msg_h = hashlib.sha256(content_sig.encode("utf-8")).hexdigest()

                    cur.execute("SELECT id FROM messages WHERE msg_hash = ?", (msg_h,))
                    if cur.fetchone() is not None:
                        skipped_count += 1
                    else:
                        cur.execute("""
                        INSERT INTO messages (msg_hash, line_no, msg_datetime, channel, direction, entity, body, source_file)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (msg_h, idx, dt, chan.strip(), direction.strip(), entity.strip(), body.strip(), filename))
                        cur.execute("SELECT id FROM messages WHERE msg_hash = ?", (msg_h,))
                        m_row = cur.fetchone()
                        new_msg_id = m_row["id"] if m_row else (getattr(cur, "lastrowid", None) or idx)
                        new_messages_to_classify.append((new_msg_id, msg_h, body.strip()))
                        added_count += 1
                else:
                    rejected_count += 1
                    row_errors.append(f"Line {idx}: Unparseable message format")

        elif role == "costs":
            reader = csv.DictReader(io.StringIO(text))
            for idx, r in enumerate(reader, start=2):
                item = r.get("item", "").strip()
                cost = r.get("cost", "").strip()
                note = r.get("note", "").strip()
                cur.execute("SELECT id, cost, note FROM costs WHERE item = ?", (item,))
                existing = cur.fetchone()
                if existing is None:
                    cur.execute("INSERT INTO costs (item, cost, note, source_file) VALUES (?, ?, ?, ?)", (item, cost, note, filename))
                    added_count += 1
                else:
                    if existing["cost"] == cost and existing["note"] == note:
                        skipped_count += 1
                    else:
                        cur.execute("UPDATE costs SET cost=?, note=?, source_file=? WHERE item=?", (cost, note, filename, item))
                        updated_count += 1

        elif role == "team":
            reader = csv.DictReader(io.StringIO(text))
            for idx, r in enumerate(reader, start=2):
                name = r.get("name", "").strip()
                role_val = r.get("role", "").strip()
                joined = r.get("joined", "").strip()
                pay = r.get("pay", "").strip()
                cur.execute("SELECT id, role, pay FROM team WHERE name = ?", (name,))
                existing = cur.fetchone()
                if existing is None:
                    cur.execute("INSERT INTO team (name, role, joined, pay, source_file) VALUES (?, ?, ?, ?, ?)", (name, role_val, joined, pay, filename))
                    added_count += 1
                else:
                    if existing["role"] == role_val and existing["pay"] == pay:
                        skipped_count += 1
                    else:
                        cur.execute("UPDATE team SET role=?, joined=?, pay=?, source_file=? WHERE name=?", (role_val, joined, pay, filename, name))
                        updated_count += 1

        # 3. Increment Dataset Revision if data mutated
        new_rev_id = None
        if added_count > 0 or updated_count > 0:
            summary_info = {
                "file": filename,
                "role": role,
                "added": added_count,
                "updated": updated_count,
                "skipped": skipped_count,
                "timestamp": now_iso
            }
            cur.execute("""
            INSERT INTO dataset_revisions (created_at, source_filename, source_file_hash, summary_json)
            VALUES (?, ?, ?, ?)
            """, (now_iso, filename, sha256, json.dumps(summary_info)))
            new_rev_id = getattr(cur, "lastrowid", None) or 1

        # 4. Record Audit Log
        total_rows = added_count + updated_count + skipped_count + rejected_count
        cur.execute("""
        INSERT INTO file_uploads (filename, file_role, sha256_hash, row_count, added_count, updated_count, skipped_count, rejected_count, status, details, uploaded_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            filename, role, sha256, total_rows, added_count, updated_count, skipped_count, rejected_count,
            "success", f"Added: {added_count}, Updated: {updated_count}, Skipped: {skipped_count}, Rejected: {rejected_count}",
            now_iso
        ))

        cur.execute("COMMIT")

    except Exception as e:
        cur.execute("ROLLBACK")
        conn.close()
        return {
            "status": "error",
            "message": f"Database transaction failed during ingestion of '{filename}': {str(e)}",
            "file_role": role,
            "added": 0, "updated": 0, "skipped": 0, "rejected": 0, "needs_review": 0,
            "errors": [str(e)]
        }

    conn.close()

    # Automatically classify newly imported messages via Jev without holding DB transaction open
    if new_messages_to_classify:
        try:
            from services.jev import classify_message
            for m_id, m_hash, m_body in new_messages_to_classify:
                classify_message(m_body, msg_id=m_id, msg_hash=m_hash)
        except Exception:
            pass

    current_rev = new_rev_id if new_rev_id else get_current_revision()["revision_id"]

    return {
        "status": "success",
        "message": f"Imported '{filename}' as role '{role}'. Added: {added_count}, Updated: {updated_count}, Skipped: {skipped_count}.",
        "file_role": role,
        "sha256": sha256,
        "row_count": total_rows,
        "added": added_count,
        "updated": updated_count,
        "skipped": skipped_count,
        "rejected": rejected_count,
        "needs_review": needs_review_count,
        "revision_id": current_rev,
        "errors": row_errors
    }
