"""PostgreSQL-only smoke tests, run against a disposable GitHub Actions DB."""
import os
import pytest
from services.db import init_db, get_db
from services.ingest import process_file_upload
from services.finance import reconcile_finances
from services.requests import get_requests_and_leads
from services.analytics import get_analytics
from services.identity import get_canonical_clients

pytestmark = pytest.mark.skipif(
    not os.getenv("AXEOM_POSTGRES_SMOKE"),
    reason="Requires ephemeral PostgreSQL service; never connect this test to Neon production."
)


def test_postgres_migrations_import_and_live_recomputation():
    init_db(force=True)
    invoice = ("invoice_no,bill_to,email,issued,due,amount,status,memo\n"
               "INV-PG-1,Harborview Bikes,owner@harborview.example,2026-09-01,2026-09-15,1000.00,unpaid,One-off\n")
    payment = ("payment_id,date,payer,payer_email,amount,method,reference\n"
               "P-PG-1,2026-10-01,Harborview Bikes,owner@harborview.example,1200,bank,INV-PG-1\n")
    booking = ("booking_id,date,client_name,email,service,status,price\n"
               "B9001,2026-09-18,Harborview Bikes,owner@harborview.example,Content Day,completed,1234\n")
    for filename, blob in (
        ("invoices.csv", invoice),
        ("payments.csv", payment),
        ("booking-changes.csv", booking),
    ):
        result = process_file_upload(filename, blob.encode("utf-8"))
        assert result["status"] == "success", result
        assert result["added"] == 1

    clients = get_canonical_clients()
    assert len(clients) == 1, clients
    assert clients[0]["canonical_name"] == "Harborview Bikes"

    finance = reconcile_finances()
    assert finance["overdue_total"] == 0
    assert finance["we_owe_total"] == 200
    assert finance["never_billed_total"] == 1234

    lead = ("lead_id,created,name,business,email,phone,source,first_reply,status\n"
            "L-PG-1,2026-09-10,A. Owner,Harborview Bikes,owner@harborview.example,,Website form,2026-09-11,Won\n")
    assert process_file_upload("newlead.csv", lead.encode())["status"] == "success"
    marketing = get_analytics()["marketing"]
    assert marketing["channels"][0]["converted"] == 1
    assert not marketing["profitability_verified"]

    board = ("video_id,client,title,editor,stage,notes_on_board,revisions,editor_hours,client_approved_on,shoot_booking\n"
             "V9007,Harborview Bikes,Launch,Sam,In Progress,,0,1.0,,B9001\n")
    message = "[2026-09-22 11:30] EMAIL from owner@harborview.example: On video V9007 please trim the intro.\n"
    assert process_file_upload("board.csv", board.encode())["status"] == "success"
    assert process_file_upload("new_messages.txt", message.encode())["status"] == "success"
    requests = get_requests_and_leads()
    assert requests["lost_requests_count"] == 1
    assert requests["lost_requests"][0]["video_id"] == "V9007"
    conn = get_db()
    assert conn.execute("SELECT COUNT(*) FROM payments").fetchone()[0] == 1
    conn.close()
