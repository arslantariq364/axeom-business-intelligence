"""
Generator script for deterministic synthetic test fixtures (Tests A through P).
Stores all fixtures in tests/fixtures/axeom_uploads/
"""

import os
from pathlib import Path

FIXTURES_DIR = Path("/home/arslan-tariq/Downloads/Axeom Challenge - Pack 01/tests/fixtures/axeom_uploads")
FIXTURES_DIR.mkdir(parents=True, exist_ok=True)

FIXTURES = {
    # TEST A: NEW CLIENT
    "test_a_new_client_booking.csv": (
        "booking_id,date,client_name,email,service,status,price\n"
        "B901,15/09/2026,Zenith Dental Care,alicia@zenithdental.com,Reels Pack,completed,$900\n"
    ),

    # TEST B: CLIENT NAME VARIATION
    "test_b_client_name_variation_booking.csv": (
        "booking_id,date,client_name,email,service,status,price\n"
        "B902,20/09/2026,NORTHPOINT MEDIA TEAM,media@northpointdfw.org,Podcast Studio 2hr,completed,$300\n"
    ),

    # TEST C: NEW OVERDUE INVOICE
    "test_c_new_overdue_invoice.csv": (
        "invoice_no,bill_to,email,issued,due,amount,status,memo\n"
        "INV-9003,Cedar & Stone Builders,will@cedarstone.build,2026-08-15,2026-09-01,1200.00,unpaid,Site Walkthrough Video\n"
    ),

    # TEST D: PARTIAL PAYMENT
    "test_d_partial_payment.csv": (
        "payment_id,date,payer,payer_email,amount,method,reference\n"
        "P9004,28/09/2026,Lonestar Realty Group,dana@lonestarrealty.com,500.00,ach,INV-1104\n"
    ),

    # TEST E: OVERPAYMENT
    "test_e_overpayment.csv": (
        "payment_id,date,payer,payer_email,amount,method,reference\n"
        "P9005,02/10/2026,TLC Home Care,lisa@tlchomecare.com,2000.00,check,INV-1120\n"
    ),

    # TEST F: UNBILLED WORK
    "test_f_unbilled_work_booking.csv": (
        "booking_id,date,client_name,email,service,status,price\n"
        "B906,18/09/2026,Bloom Florals,chloe@bloomflorals.com,Content Day,completed,$1500\n"
    ),

    # TEST G: LOST CLIENT REQUEST (messages + companion production board)
    "test_g_lost_client_request.txt": (
        "[2026-09-22 11:30] EMAIL from will@cedarstone.build: On luxury kitchen tour video V9007, please trim the drone shot intro.\n"
    ),
    "test_g_production_record.csv": (
        "video_id,client,title,editor,stage,notes_on_board,revisions,editor_hours,client_approved_on,shoot_booking\n"
        "V9007,Cedar & Stone Builders,Luxury kitchen tour,Ali,In Progress,,0,2.5,,B040\n"
    ),

    # TEST H: NEW LEAD
    "test_h_new_lead.csv": (
        "lead_id,created,name,business,email,phone,source,first_reply,status\n"
        "L908,2026-10-01 10:15,Marcus Brody,Brody Architecture,marcus@brodyarch.com,214-555-0199,Website form,2026-10-01,Open\n"
    ),

    # TEST I: UNANSWERED LEAD
    "test_i_unanswered_lead.csv": (
        "lead_id,created,name,business,email,phone,source,first_reply,status\n"
        "L909,2026-10-03 16:45,Elena Rostova,Rostova Designs,elena@rostovadesigns.com,469-555-0198,Instagram DM,,Open\n"
    ),

    # TEST J: DUPLICATE FILE
    "test_j_duplicate_file.csv": (
        "booking_id,date,client_name,email,service,status,price\n"
        "B910,25/09/2026,Khan Dental,sarah@khandental.com,Podcast Studio 1hr,completed,$200\n"
    ),

    # TEST K: MALFORMED FILE
    "test_k_malformed_missing_columns.csv": (
        "random_column_1,random_column_2\n"
        "value_1,value_2\n"
    ),

    # TEST L: MIXED NEW AND EXISTING RECORDS
    "test_l_mixed_records_invoices.csv": (
        "invoice_no,bill_to,email,issued,due,amount,status,memo\n"
        "INV-1001,Northpoint Church,media@northpointdfw.org,2026-04-03,2026-04-17,300.00,paid,Podcast Studio 2hr 4/3\n"
        "INV-9012,Northpoint Church,media@northpointdfw.org,2026-09-20,2026-10-04,800.00,unpaid,Fall Conference Promo\n"
    ),

    # TEST M: CROSS-FILE CONSISTENCY (Lead, Booking, Invoice, Payment)
    "test_m1_lead.csv": (
        "lead_id,created,name,business,email,phone,source,first_reply,status\n"
        "L913,2026-09-10 09:00,Dr. Arthur Smith,Summit Peak Health,drsmith@summitpeak.org,214-555-0197,Website form,2026-09-10,Won\n"
    ),
    "test_m2_booking.csv": (
        "booking_id,date,client_name,email,service,status,price\n"
        "B913,15/09/2026,Summit Peak Health,drsmith@summitpeak.org,Content Day,completed,$1200\n"
    ),
    "test_m3_invoice.csv": (
        "invoice_no,bill_to,email,issued,due,amount,status,memo\n"
        "INV-9013,Summit Peak Health,drsmith@summitpeak.org,2026-09-15,2026-10-01,1200.00,unpaid,Summit Peak Health Shoot\n"
    ),
    "test_m4_payment.csv": (
        "payment_id,date,payer,payer_email,amount,method,reference\n"
        "P9013,01/10/2026,Summit Peak Health,drsmith@summitpeak.org,1200.00,card,INV-9013\n"
    ),

    # TEST N: AMBIGUOUS IDENTITY
    "test_n_ambiguous_identity_booking.csv": (
        "booking_id,date,client_name,email,service,status,price\n"
        "B914,28/09/2026,Torres Tire & Auto,carlos@torrestireauto.com,Content Day,completed,$1500\n"
    ),

    # TEST O: UNKNOWN CLIENT PAYMENT
    "test_o_unknown_client_payment.csv": (
        "payment_id,date,payer,payer_email,amount,method,reference\n"
        "P9015,30/09/2026,Vanguard Holding Escrow LLC,escrow@vanguardholdings.com,1000.00,wire,REF-UNASSIGNED\n"
    ),

    # TEST P: REPEATED REQUESTS
    "test_p_repeated_requests.txt": (
        "[2026-09-25 14:10] WHATSAPP from +1 214-555-0135 (Sofia): Can we swap the outro music on video V022?\n"
        "[2026-09-25 14:40] EMAIL from sofia@lunabridal.com: Following up on WhatsApp regarding video V022, please swap the outro music.\n"
    )
}

for filename, content in FIXTURES.items():
    p = FIXTURES_DIR / filename
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated fixture: {p.name} ({len(content)} bytes)")

print("\nAll 16 test fixtures generated successfully in tests/fixtures/axeom_uploads/")
