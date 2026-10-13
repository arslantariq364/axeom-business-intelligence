"""Independent, data-isolated regression tests for the October 2026 audit.
Run without production Neon credentials or bundled challenge data.
"""
import io
import pytest
from app import app
from services.db import init_db, get_db


@pytest.fixture
def api(tmp_path, monkeypatch):
    monkeypatch.setenv("AXEOM_FORCE_SQLITE", "1")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("AXEOM_DB_PATH", str(tmp_path / "audit.db"))
    init_db()
    app.config.update(TESTING=True)
    with app.test_client() as client:
        yield client


def upload(api, filename, text):
    return api.post("/api/upload", data={
        "file": (io.BytesIO(text if isinstance(text, bytes) else text.encode("utf-8")), filename)
    }, content_type="multipart/form-data")


def test_invalid_amount_is_rejected_not_silently_coerced(api):
    result = upload(api, "invoice.csv",
        "invoice_no,bill_to,email,issued,due,amount,status,memo\n"
        "INV-X1,Acme,acme@example.com,2026-09-01,2026-09-15,garbage,unpaid,test\n")
    assert result.status_code == 400
    assert result.json["rejected"] == 1
    conn = get_db()
    assert conn.execute("SELECT COUNT(*) FROM invoices").fetchone()[0] == 0
    conn.close()


def test_invalid_date_cannot_crash_dashboard(api):
    result = upload(api, "invoice.csv",
        "invoice_no,bill_to,email,issued,due,amount,status,memo\n"
        "INV-X2,Acme,acme@example.com,2026-09-01,not-a-date,200,unpaid,test\n")
    assert result.status_code == 400
    assert api.get("/api/state").status_code == 200


def test_bom_csv_and_date_only_booking_correction(api):
    content = ("booking_id,date,client_name,email,service,status,price\n"
               "B901,2026-09-15,Zenith Dental Care,alicia@zenithdental.com,Reels Pack,completed,900\n")
    first = upload(api, "anything.csv", content.encode("utf-8-sig"))
    assert first.status_code == 200 and first.json["added"] == 1
    before = api.get("/api/state").json["metrics"]["client_count"]
    assert before == 1
    second = upload(api, "update-booking.csv", content.replace("2026-09-15", "2026-09-16"))
    assert second.status_code == 200 and second.json["updated"] == 1
    conn = get_db()
    assert conn.execute("SELECT booking_date FROM bookings WHERE booking_id='B901'").fetchone()[0] == "2026-09-16"
    conn.close()


def test_overpayment_increases_customer_credits(api):
    inv = ("invoice_no,bill_to,email,issued,due,amount,status,memo\n"
           "INV-X3,TLC Home Care,angela@tlchomecare.com,2026-09-01,2026-09-15,1000,unpaid,test\n")
    pay = ("payment_id,date,payer,payer_email,amount,method,reference\n"
           "PAY-X3,2026-10-01,TLC Home Care,angela@tlchomecare.com,1200,bank,INV-X3\n")
    assert upload(api, "invoice.csv", inv).status_code == 200
    assert upload(api, "payment.csv", pay).status_code == 200
    state = api.get("/api/state").json
    assert state["metrics"]["we_owe_total"] == 200.0
    assert state["metrics"]["overdue_total"] == 0.0


def test_new_unbilled_booking_is_visible(api):
    csv = ("booking_id,date,client_name,email,service,status,price\n"
           "B906,18/09/2026,Bloom Florals,chloe@bloomflorals.com,Content Day,completed,1234\n")
    assert upload(api, "booking.csv", csv).status_code == 200
    state = api.get("/api/state").json
    assert state["metrics"]["never_billed_total"] == 1234.0
    assert any(row["booking_id_or_month"] == "B906" for row in state["money"]["never_billed"])


def test_marketing_recomputes_after_lead_upload(api):
    header = "lead_id,created,name,business,email,phone,source,first_reply,status\n"
    rows = "".join(
        f"L{i},2026-09-10,Bob {i},Company {i},bob{i}@example.com,,Referral,2026-09-11,Won\n"
        for i in range(1, 6)
    )
    assert upload(api, "leads_1.csv", header + rows).status_code == 200
    first = api.get("/api/state").json["analytics"]["marketing"]
    assert first["recommended_channel"] == "Referral"
    new_rows = "".join(
        f"L{i},2026-09-12,Jane {i},Firm {i},jane{i}@example.com,,Website form,2026-09-13,Won\n"
        for i in range(20, 26)
    )
    assert upload(api, "leads_2.csv", header + new_rows).status_code == 200
    second = api.get("/api/state").json["analytics"]["marketing"]
    assert second["recommended_channel"] == "Website form"
    website = next(row for row in second["channels"] if row["name"] == "Website form")
    assert website["leads"] == 6 and website["converted"] == 6
    assert website["gross_profit"] is None
    assert second["profitability_verified"] is False


def test_uploaded_video_request_enters_candidate_queue(api):
    board = ("video_id,client,title,editor,stage,notes_on_board,revisions,editor_hours,client_approved_on,shoot_booking\n"
             "V9007,Cedar & Stone Builders,Luxury kitchen tour,Ali,In Progress,,0,2.5,,B040\n")
    message = ("[2026-09-22 11:30] EMAIL from will@cedarstone.build: "
               "On luxury kitchen tour video V9007, please trim the drone shot intro.\n")
    assert upload(api, "board.csv", board).status_code == 200
    assert upload(api, "messages_patch.txt", message).status_code == 200
    state = api.get("/api/state").json
    assert state["metrics"]["lost_requests_count"] == 1
    assert state["requests"]["lost_requests"][0]["verification"] == "automated_candidate_needs_owner_review"


def test_patel_hero_drops_paid_invoice_claim(api):
    invoice = ("invoice_no,bill_to,email,issued,due,amount,status,memo\n"
               "INV-1122,Patel Insurance Group,raj@patelinsures.com,2026-09-01,2026-09-15,2500,unpaid,retainer\n")
    payment = ("payment_id,date,payer,payer_email,amount,method,reference\n"
               "PAY-PAID,2026-10-01,Patel Insurance Group,raj@patelinsures.com,2500,bank,INV-1122\n")
    assert upload(api, "inv.csv", invoice).status_code == 200
    assert "INV-1122" in api.get("/api/state").json["today"]["hero_action"]["overdue_invoice"]
    assert upload(api, "pay.csv", payment).status_code == 200
    state = api.get("/api/state").json
    assert state["today"]["hero_action"]["overdue_invoice"] == ""
    assert "overdue" not in state["today"]["monday_top_3"][0]["summary"].lower() or "not currently" in state["today"]["monday_top_3"][0]["summary"].lower()
