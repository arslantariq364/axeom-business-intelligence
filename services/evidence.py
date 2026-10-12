"""
Evidence registry and transactional provenance service for Axeom Studio.
Contains cross-reference links and citations for all financial and operational findings.
"""

from services.db import get_db

EVIDENCE_REGISTER = [
    {
        "category": "Identity Resolution",
        "title": "Dr. Sarah Khan Provenance Trail",
        "files_involved": ["leads.csv", "bookings.csv", "invoices.csv", "payments.csv", "production_board.csv", "messages.txt"],
        "provenance": (
            "Originates in leads.csv (Lead L040) as 'Dr. Sarah Khan' (sarah@khandental.com, 214-555-0141). "
            "Bookings B003, B034, B063, B099, B131, B170 under 'Khan Dental'. Invoices INV-1004, INV-1035, etc. "
            "billed to 'Dr. Sarah Khan'. Payments P5004, P5036 under 'Dr. Sarah Khan' and 'Khan Dental PLLC'. "
            "Production board tracks 16 videos (V001..). Message on 2026-09-05 updates phone to 214-555-0177."
        )
    },
    {
        "category": "Third-Party Payer",
        "title": "Brightline Marketing LLC Agency Payments",
        "files_involved": ["messages.txt", "invoices.csv", "payments.csv", "bookings.csv"],
        "provenance": (
            "Email 2026-06-08 from Kelsey Moore (kelsey@brightlinemktg.com): 'Please bill us (Brightline) for Greenway Pediatrics "
            "and Summit Chiropractic. We pay monthly.' All invoices INV-1046, INV-1061, INV-1080, INV-1100, INV-1110, INV-1130, INV-1141 "
            "billed directly to Brightline Marketing. Payments P5059, P5087, P5111, P5131 received from BRIGHTLINE MARKETING LLC. "
            "Greenway Pediatrics and Summit Chiropractic are independent clinical clients whose bills are handled by Brightline."
        )
    },
    {
        "category": "Accounts Payable / We Owe",
        "title": "Glow Aesthetics $900.00 Overpayment on INV-1086",
        "files_involved": ["invoices.csv", "payments.csv"],
        "provenance": (
            "Invoice INV-1086 issued for $900.00 to Glow Aesthetics (due 2026-08-14). Payment P5091 received on 2026-08-08 for $900.00 "
            "(ref INV-1086). Payment P5093 received on 2026-09-08 for $900.00 (ref INV-1086). Invoiced total across relationship: $3,600.00. "
            "Total payments received: $4,500.00. Axeom holds an unallocated customer credit balance of $900.00 owed to Glow Aesthetics."
        )
    },
    {
        "category": "Accounts Payable / We Owe",
        "title": "Lone Star Realty $1,500.00 Cancelled Shoot Credit",
        "files_involved": ["bookings.csv", "invoices.csv", "payments.csv", "messages.txt"],
        "provenance": (
            "Shoot B148 scheduled for 2026-09-24 was invoiced on INV-1135 ($1,500.00) and paid by Dana Brooks via P5121 ($1,500.00). "
            "On 2026-09-24 at 08:30, Dana sent a WhatsApp message: 'family emergency, have to reschedule today's shoot'. "
            "Axeom rescheduled the shoot as B152 on 2026-10-01, but issued a new invoice INV-1143 ($1,500.00) which Dana paid via P5130. "
            "The initial $1,500 payment on INV-1135 was never applied or refunded. Axeom owes Lone Star Realty a $1,500.00 credit."
        )
    },
    {
        "category": "Unbilled Work",
        "title": "Vega Auto Detailing Completed Content Day ($1,500.00)",
        "files_involved": ["bookings.csv", "production_board.csv", "invoices.csv"],
        "provenance": (
            "Shoot B144 booked and completed on 2026-09-18 for Carlos Vega (Vega Auto Detailing). Service: Content Day (8 hrs), price $1,500.00. "
            "Production board shows videos V283, V284, V285 in editing/ready stages. Cross-reference of invoices.csv reveals zero invoices "
            "issued for B144 or Vega Auto Detailing for September 2026. $1,500.00 in completed chargeable work remains unbilled."
        )
    },
    {
        "category": "Unbilled Work",
        "title": "Ironclad Gym Completed Reels Pack ($900.00)",
        "files_involved": ["bookings.csv", "production_board.csv", "invoices.csv"],
        "provenance": (
            "Shoot B123 completed on 2026-08-31 for Marcus Webb (Ironclad Gym). Service: Reels Pack (4 hrs), price $900.00. "
            "Production board tracks videos V241-V244. Invoices.csv contains INV-1033 ($900) in May and INV-1073 ($900) in July, "
            "but zero invoice issued for August shoot B123. $900.00 in completed chargeable work remains unbilled."
        )
    },
    {
        "category": "Unbilled Work",
        "title": "DFW Founders Completed Podcast Session ($550.00)",
        "files_involved": ["bookings.csv", "invoices.csv"],
        "provenance": (
            "Shoot B136 completed on 2026-09-11 for Ethan Cole (DFW Founders). Service: Podcast Studio (4 hrs), price $550.00. "
            "Invoices.csv contains invoices for earlier sessions, but session B136 was skipped during billing run. $550.00 unbilled."
        )
    },
    {
        "category": "Overdue Receivables",
        "title": "Crown Barbershop INV-1066 ($900.00, 80 Days Overdue)",
        "files_involved": ["invoices.csv", "payments.csv"],
        "provenance": (
            "Invoice INV-1066 issued 2026-07-04 (due 2026-07-18) for $900.00 to Crown Barbers. Invoicing software incorrectly marks it 'paid'. "
            "Inspection of payments.csv shows Andre Jackson paid $900 via P5030 on 2026-05-18 for earlier invoice INV-1029. "
            "Zero payments exist for INV-1066. The invoice is completely unpaid and 80 days late as of 2026-10-06."
        )
    },
    {
        "category": "Client Churn Intervention",
        "title": "Patel Insurance Group Retention Crisis ($2,500 Retainer)",
        "files_involved": ["leads.csv", "messages.txt", "invoices.csv", "production_board.csv"],
        "provenance": (
            "Nina Patel inquiry L097 (2026-09-30) requesting contract renegotiation received zero reply. Direct email follow-up Oct 2 ignored. "
            "Raj Patel sent angry complaints on 2026-09-08 and 2026-10-01 regarding lack of regulatory compliance branding ('Patel Insurance Group') "
            "and unswapped b-roll on 'teen driver tips'. Invoice INV-1122 ($2,500.00) withheld 21 days late. "
            "Mirrors Meridian Wealth Partners churn in July 2026."
        )
    }
]

def search_records(query):
    if not query or len(query.strip()) < 2:
        return []
    q = f"%{query.strip().lower()}%"
    results = []
    conn = get_db()
    cur = conn.cursor()

    # Search invoices
    cur.execute("SELECT * FROM invoices WHERE LOWER(invoice_no) LIKE ? OR LOWER(bill_to) LIKE ?", (q, q))
    for r in cur.fetchall():
        results.append({
            "type": "Invoice",
            "id": r['invoice_no'],
            "title": f"Invoice {r['invoice_no']} to {r['bill_to']}",
            "amount": f"${float(r['amount']):,.2f}",
            "date": r['due'],
            "status": r['status'],
            "details": f"Issued: {r['issued']}, Due: {r['due']}, Status: {r['status']}"
        })

    # Search payments
    cur.execute("SELECT * FROM payments WHERE LOWER(payment_id) LIKE ? OR LOWER(payer) LIKE ? OR LOWER(reference) LIKE ?", (q, q, q))
    for r in cur.fetchall():
        results.append({
            "type": "Payment",
            "id": r['payment_id'],
            "title": f"Payment {r['payment_id']} from {r['payer']}",
            "amount": f"${float(r['amount']):,.2f}",
            "date": r['payment_date'],
            "status": r['method'],
            "details": f"Reference: {r['reference']}, Method: {r['method']}"
        })

    # Search bookings
    cur.execute("SELECT * FROM bookings WHERE LOWER(booking_id) LIKE ? OR LOWER(client_name) LIKE ? OR LOWER(service) LIKE ?", (q, q, q))
    for r in cur.fetchall():
        results.append({
            "type": "Booking",
            "id": r['booking_id'],
            "title": f"Booking {r['booking_id']} for {r['client_name']}",
            "amount": f"${float(r['price']):,.2f}",
            "date": r['booking_date'],
            "status": r['status'],
            "details": f"Service: {r['service']}, Status: {r['status']}"
        })

    # Search messages
    cur.execute("SELECT * FROM messages WHERE LOWER(entity) LIKE ? OR LOWER(body) LIKE ? LIMIT 20", (q, q))
    for r in cur.fetchall():
        results.append({
            "type": "Message",
            "id": f"Msg L{r['line_no']}",
            "title": f"[{r['channel']}] {r['direction']} {r['entity']}",
            "amount": "-",
            "date": r['msg_datetime'],
            "status": r['channel'],
            "details": r['body']
        })

    conn.close()
    return results[:30]
