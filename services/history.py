"""
Client History & deep-dive drilldown service for Axeom Studio.
Links bookings, invoices, payments, production tasks, and messages for any client.
"""

from services.db import get_db
from services.identity import get_canonical_clients, resolve_client_by_name

def get_client_history(client_id_or_name):
    # Find canonical client
    client = None
    for c in get_canonical_clients():
        if c['id'] == client_id_or_name or c['canonical_name'].lower() == client_id_or_name.lower():
            client = c
            break
    if not client:
        client = resolve_client_by_name(client_id_or_name)
    if not client:
        return None

    aliases = set(c.lower() for c in client['payer_aliases'])
    aliases.add(client['canonical_name'].lower())
    canonical_lower = client['canonical_name'].lower()

    conn = get_db()
    cur = conn.cursor()

    # 1. Bookings
    cur.execute("SELECT * FROM bookings")
    all_bookings = [dict(r) for r in cur.fetchall()]
    client_bookings = []
    for b in all_bookings:
        b_name = b['client_name'].lower()
        if b_name in aliases or any(a in b_name for a in aliases):
            client_bookings.append(b)

    # 2. Invoices
    cur.execute("SELECT * FROM invoices")
    all_invoices = [dict(r) for r in cur.fetchall()]
    client_invoices = []
    for inv in all_invoices:
        bill_to = inv['bill_to'].lower()
        if bill_to in aliases or any(a in bill_to for a in aliases):
            client_invoices.append(inv)
        elif client['canonical_name'] in ["Greenway Pediatrics", "Summit Chiropractic"] and "brightline" in bill_to:
            client_invoices.append(inv)

    # 3. Payments
    cur.execute("SELECT * FROM payments")
    all_payments = [dict(r) for r in cur.fetchall()]
    client_payments = []
    for p in all_payments:
        payer = (p.get('payer') or p.get('client_or_payer') or '').lower()
        if payer in aliases or any(a in payer for a in aliases):
            client_payments.append(p)
        elif client['canonical_name'] in ["Greenway Pediatrics", "Summit Chiropractic"] and "brightline" in payer:
            client_payments.append(p)

    # 4. Production Board
    cur.execute("SELECT * FROM production_board")
    all_videos = [dict(r) for r in cur.fetchall()]
    client_videos = []
    for v in all_videos:
        v_client = (v.get('client') or v.get('client_name') or '').lower()
        if v_client in aliases or any(a in v_client for a in aliases):
            client_videos.append(v)

    # 5. Messages
    cur.execute("SELECT * FROM messages ORDER BY id ASC")
    all_msgs = [dict(r) for r in cur.fetchall()]
    client_messages = []
    contact_keywords = [client['canonical_name'].lower()]
    if client.get('primary_contact'):
        contact_keywords.append(client['primary_contact'].split('(')[0].strip().lower())
    for em in client.get('emails', []):
        contact_keywords.append(em.lower())
    for ph in client.get('phones', []):
        contact_keywords.append(ph.lower())

    for m in all_msgs:
        entity = m['entity'].lower()
        body = m['body'].lower()
        if any(kw in entity for kw in contact_keywords) or any(kw in body for kw in contact_keywords):
            client_messages.append(m)

    conn.close()

    total_invoiced = sum(float(inv['amount']) for inv in client_invoices if inv['status'].lower() != 'void')
    total_paid = sum(float(p['amount']) for p in client_payments)

    return {
        "client": client,
        "summary": {
            "total_invoiced": total_invoiced,
            "total_paid": total_paid,
            "bookings_count": len(client_bookings),
            "invoices_count": len(client_invoices),
            "payments_count": len(client_payments),
            "videos_count": len(client_videos),
            "messages_count": len(client_messages)
        },
        "bookings": client_bookings,
        "invoices": client_invoices,
        "payments": client_payments,
        "videos": client_videos,
        "messages": client_messages
    }
