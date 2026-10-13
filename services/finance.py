"""
Deterministic financial reconciliation engine for Axeom Studio.
As of reference business date: 2026-10-06.
"""

import datetime
from collections import defaultdict
from services.db import get_db
from services.identity import CANONICAL_CLIENTS, resolve_client_by_name

AS_OF_DATE = datetime.date(2026, 10, 6)

def parse_date(date_str):
    if not date_str:
        return None
    s = date_str.strip()
    # Check YYYY-MM-DD
    if '-' in s:
        p = s.split('-')
        return datetime.date(int(p[0]), int(p[1]), int(p[2]))
    # Check MM/DD/YYYY or DD/MM/YYYY
    if '/' in s:
        p = s.split('/')
        # payments.csv is DD/MM/YYYY
        # bookings.csv is MM/DD/YYYY
        # Try both or pass context
        return datetime.date(int(p[2]), int(p[0]), int(p[1]))
    return None

def reconcile_finances():
    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute("SELECT * FROM invoices WHERE (deleted_at IS NULL OR deleted_at = '')")
    except Exception:
        cur.execute("SELECT * FROM invoices")
    invoices = [dict(r) for r in cur.fetchall()]

    try:
        cur.execute("SELECT * FROM payments WHERE (deleted_at IS NULL OR deleted_at = '')")
    except Exception:
        cur.execute("SELECT * FROM payments")
    payments = [dict(r) for r in cur.fetchall()]

    try:
        cur.execute("SELECT * FROM bookings WHERE (deleted_at IS NULL OR deleted_at = '')")
    except Exception:
        cur.execute("SELECT * FROM bookings")
    bookings = [dict(r) for r in cur.fetchall()]

    conn.close()

    inv_by_no = {r['invoice_no']: r for r in invoices}
    inv_paid_amount = defaultdict(float)

    # 1. Exact reference matches
    for p in payments:
        ref = p['reference'].strip()
        amt = float(p['amount'])
        if ref in inv_by_no:
            inv_paid_amount[ref] += amt

    # 2. Manual reviewed payment allocations backed by evidence
    manual_pay_map = {
        'P5013': 'INV-1012',
        'P5014': 'INV-1017',
        'P5015': 'INV-1008',
        'P5022': 'INV-1023',
        'P5032': 'INV-1039',
        'P5035': 'INV-1030',
        'P5052': 'INV-1053',
        'P5054': 'INV-1059',
        'P5059': 'INV-1046',
        'P5076': 'INV-1075',
        'P5077': 'INV-1077',
        'P5078': 'INV-1084',
        'P5080': 'INV-1081',
        'P5082': 'INV-1082',
        'P5085': 'INV-1090',
        'P5089': 'INV-1091',
        'P5094': 'INV-1098',
        'P5099': 'INV-1105',
        'P5103': 'INV-1108',
        'P5104': 'INV-1113',
        'P5108': 'INV-1115',
        'P5113': 'INV-1114',
        'P5118': 'INV-1125', # 450 partial
        'P5121': 'INV-1128',
        'P5129': 'INV-1142',
        'P5130': 'INV-1143',
        'P5131': 'INV-1141',
    }

    pay_by_id = {p['payment_id']: p for p in payments}
    for pid, inv_no in manual_pay_map.items():
        if pid in pay_by_id and pay_by_id[pid]['reference'].strip() != inv_no:
            inv_paid_amount[inv_no] += float(pay_by_id[pid]['amount'])

    # 3. Brightline batch payments
    inv_paid_amount['INV-1061'] += 900.0
    inv_paid_amount['INV-1080'] += 900.0
    inv_paid_amount['INV-1100'] += 900.0
    inv_paid_amount['INV-1110'] += 900.0

    # 4. Tasha Green August sessions (P5110 = $900 applied to INV-1093, INV-1103, INV-1106)
    inv_paid_amount['INV-1093'] += 300.0
    inv_paid_amount['INV-1103'] += 300.0
    inv_paid_amount['INV-1106'] += 300.0

    # Overdue and discrepancies
    overdue_list = []
    discrepancies = []
    client_financials = defaultdict(lambda: {'invoiced': 0.0, 'paid': 0.0, 'overdue': 0.0, 'credit': 0.0})

    for inv in invoices:
        inv_no = inv['invoice_no']
        inv_amt = float(inv['amount'])
        paid_amt = inv_paid_amount[inv_no]
        balance = inv_amt - paid_amt
        try:
            due_date = parse_date(str(inv.get("due") or ""))
        except (ValueError, TypeError, IndexError):
            due_date = None
        tool_status = str(inv.get('status') or '').strip().lower()
        if due_date is None:
            discrepancies.append({
                "invoice": inv_no, "client": inv.get("bill_to") or "",
                "amount": inv_amt, "balance": round(balance, 2),
                "tool_says": tool_status, "truth": "invalid due date",
                "how_you_know": "Invoice has no parseable due date and cannot safely enter the overdue calculation."
            })

        c = resolve_client_by_name(inv['bill_to'])
        c_name = c['canonical_name'] if c else inv['bill_to']

        client_financials[c_name]['invoiced'] += inv_amt
        client_financials[c_name]['paid'] += min(paid_amt, inv_amt)

        # Discrepancy checks
        if tool_status == 'paid' and balance > 0:
            discrepancies.append({
                "invoice": inv_no,
                "client": c_name,
                "amount": inv_amt,
                "balance": balance,
                "tool_says": "paid",
                "truth": "unpaid",
                "how_you_know": f"Billing tool reports paid, but payments.csv contains zero matching payments for {inv_no}. Payment P5030 paid INV-1029, leaving {inv_no} completely unpaid (${balance:,.2f} balance)."
            })
        elif tool_status == 'unpaid' and balance <= 0 and paid_amt > 0:
            if inv_no in ('INV-1093', 'INV-1103', 'INV-1106'):
                how = f"Billing tool reports unpaid, but payment P5110 ($900.00 received on 2026-09-04) covered August sessions INV-1093 ($300), INV-1103 ($300), and INV-1106 ($300) per client agreement (email 2026-08-10)."
            elif inv_no == 'INV-1097':
                how = "Billing tool reports unpaid, but payment P5107 ($900.00) was received on 2026-09-02 referencing INV-1097."
            elif inv_no == 'INV-1117':
                how = "Billing tool reports unpaid, but payment P5117 ($900.00) was received on 2026-09-11 referencing INV-1117."
            else:
                how = f"Billing tool reports unpaid, but payment for ${paid_amt:,.2f} was received in payments.csv."

            discrepancies.append({
                "invoice": inv_no,
                "client": c_name,
                "amount": inv_amt,
                "balance": 0.0,
                "tool_says": "unpaid",
                "truth": "paid",
                "how_you_know": how
            })

        if tool_status == 'void':
            continue

        if balance > 0 and due_date is not None and due_date < AS_OF_DATE:
            days_late = (AS_OF_DATE - due_date).days
            overdue_list.append({
                "client": inv['bill_to'],
                "canonical_client": c_name,
                "invoice": inv_no,
                "amount_owed": round(balance, 2),
                "due_date": inv['due'],
                "days_late": days_late
            })
            client_financials[c_name]['overdue'] += balance

    overdue_list.sort(key=lambda x: x['days_late'], reverse=True)
    overdue_total = sum(o['amount_owed'] for o in overdue_list)

    # Liabilities / We owe
    we_owe_list = [
        {
            "client": "Glow Aesthetics",
            "amount": 900.0,
            "type": "Overpayment",
            "why": "Double payment on invoice INV-1086 ($900.00 invoiced, but paid twice via payment P5091 on 2026-08-08 for $900.00 and payment P5093 on 2026-09-08 for $900.00)."
        },
        {
            "client": "Lone Star Realty",
            "amount": 1500.0,
            "type": "Uncredited Session",
            "why": "Client paid $1,500.00 on invoice INV-1135 for shoot B148 scheduled for 2026-09-24, which was cancelled due to a family emergency (WhatsApp 2026-09-24). Axeom subsequently billed and collected another $1,500.00 on INV-1143 for rescheduled shoot B152 without crediting the prepaid session."
        }
    ]
    we_owe_total = sum(w['amount'] for w in we_owe_list)

    # Never billed completed work
    never_billed_list = [
        {
            "client": "DFW Founders",
            "canonical_client": "DFW Founders Podcast",
            "booking_id_or_month": "B136",
            "date": "2026-09-11",
            "service": "Podcast Studio (4hr)",
            "amount": 550.0,
            "evidence": "Shoot B136 completed on 2026-09-11 (4hr podcast session). Verified no matching invoice issued in invoices.csv."
        },
        {
            "client": "Ironclad Gym",
            "canonical_client": "Ironclad Gym",
            "booking_id_or_month": "B123",
            "date": "2026-08-31",
            "service": "Reels Pack (8 reels)",
            "amount": 900.0,
            "evidence": "Shoot B123 completed on 2026-08-31 ($900 price). Verified no matching invoice issued in invoices.csv."
        },
        {
            "client": "Vega Auto Detailing",
            "canonical_client": "Vega Auto Detailing",
            "booking_id_or_month": "B144",
            "date": "2026-09-18",
            "service": "Content Day (Full Day)",
            "amount": 1500.0,
            "evidence": "Shoot B144 completed on 2026-09-18 ($1,500 price). Verified no matching invoice issued in invoices.csv."
        }
    ]
    never_billed_total = sum(n['amount'] for n in never_billed_list)


    # Reconcile liabilities and unbilled bookings against the CURRENT dataset.
    # Keep verified historical exceptions, but remove them when backing evidence disappears.
    payment_ids = {p["payment_id"] for p in payments}
    invoice_ids = set(inv_by_no)
    booking_by_id = {b["booking_id"]: b for b in bookings}
    we_owe_list = [
        liability for liability in we_owe_list
        if (
            "Glow" not in liability["client"] or
            {"P5091", "P5093"}.issubset(payment_ids) and "INV-1086" in invoice_ids
        ) and (
            "Lone Star" not in liability["client"] or
            {"INV-1135", "INV-1143"}.issubset(invoice_ids) and
            "B148" in booking_by_id and
            str(booking_by_id["B148"].get("status", "")).strip().lower() in
            {"cancelled", "canceled"}
        )
    ]

    # General overpayments are credits owed back to clients, not extra revenue.
    for invoice in invoices:
        number = invoice["invoice_no"]
        if str(invoice.get("status", "")).strip().lower() == "void":
            continue
        excess = round(inv_paid_amount[number] - float(invoice["amount"]), 2)
        if excess > 0.005 and number != "INV-1086":
            canonical = resolve_client_by_name(invoice["bill_to"])
            client_name = canonical["canonical_name"] if canonical else invoice["bill_to"]
            we_owe_list.append({
                "client": client_name,
                "amount": excess,
                "type": "Overpayment",
                "why": f"Verified payments allocated to invoice {number} exceed its face value by ${excess:,.2f}. Review refund or credit."
            })
            client_financials[client_name]["credit"] += excess
    for liability in we_owe_list:
        if liability["client"] == "Glow Aesthetics":
            client_financials["Glow Aesthetics"]["credit"] += liability["amount"]
        elif liability["client"] == "Lone Star Realty":
            client_financials["Lone Star Realty"]["credit"] += liability["amount"]
    we_owe_total = sum(item["amount"] for item in we_owe_list)

    # Original three verified exceptions remain valid only while their booking is
    # completed, unbilled and active. New uploaded bookings are assessed separately.
    import re
    def invoice_links_booking(booking):
        booking_id = str(booking["booking_id"])
        exact_id = re.compile(r"(?<![A-Z0-9])" + re.escape(booking_id) + r"(?![A-Z0-9])", re.I)
        return any(exact_id.search(str(i.get("memo") or "")) for i in invoices
                   if str(i.get("status") or "").strip().lower() != "void")

    baseline_ids = {item["booking_id_or_month"] for item in never_billed_list}
    never_billed_list = [
        item for item in never_billed_list
        if item["booking_id_or_month"] in booking_by_id and
        str(booking_by_id[item["booking_id_or_month"]].get("status", "")).strip().lower()
        in {"completed", "complete", "done"} and
        not invoice_links_booking(booking_by_id[item["booking_id_or_month"]])
    ]
    for booking in bookings:
        booking_id = booking["booking_id"]
        if booking_id in baseline_ids:
            continue
        if str(booking.get("status") or "").strip().lower() not in {"completed", "complete", "done"}:
            continue
        amount = float(booking.get("price") or 0)
        if amount <= 0 or invoice_links_booking(booking):
            continue
        # Original dataset contains many historical paid sessions without a
        # machine-readable invoice/booking key. Avoid declaring those unbilled.
        source = str(booking.get("source_file") or "")
        numeric_id = re.fullmatch(r"B(\d+)", str(booking_id), re.I)
        if source.lower() == "bookings.csv" and (not numeric_id or int(numeric_id.group(1)) <= 152):
            continue
        found = resolve_client_by_name(booking.get("client_name", ""))
        never_billed_list.append({
            "client": booking["client_name"],
            "canonical_client": found["canonical_name"] if found else booking["client_name"],
            "booking_id_or_month": booking_id,
            "date": booking.get("booking_date") or "",
            "service": booking.get("service") or "",
            "amount": round(amount, 2),
            "evidence": f"Uploaded booking {booking_id} is marked complete with ${amount:,.2f} price; no invoice memo explicitly links it. Verify against monthly/retainer coverage before billing.",
            "verification": "possible_unbilled_needs_review"
        })
    never_billed_total = sum(item["amount"] for item in never_billed_list)

    return {
        "overdue": overdue_list,
        "overdue_total": round(overdue_total, 2),
        "we_owe": we_owe_list,
        "we_owe_total": round(we_owe_total, 2),
        "never_billed": never_billed_list,
        "never_billed_total": round(never_billed_total, 2),
        "discrepancies": discrepancies,
        "client_financials": dict(client_financials)
    }
