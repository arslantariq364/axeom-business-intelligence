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


def upload_batch(api, files_dict):
    file_list = [
        (io.BytesIO(text if isinstance(text, bytes) else text.encode("utf-8")), filename)
        for filename, text in files_dict.items()
    ]
    return api.post("/api/upload-batch", data={"files": file_list}, content_type="multipart/form-data")


def test_new_client_appears_in_directory_and_relevant_counts(api):
    """Scenario 1: Completed booking for new client registers client and increments count."""
    booking = ("booking_id,date,client_name,email,service,status,price\n"
               "B999,2026-09-20,Nova Health Dynamics,contact@novahealth.example,Content Day,completed,1500\n")
    res = upload(api, "bookings.csv", booking)
    assert res.status_code == 200
    state = api.get("/api/state").json
    assert state["metrics"]["client_count"] == 1
    clients = state["clients"]
    assert any(c["canonical_name"] == "Nova Health Dynamics" for c in clients)


def test_complete_lifecycle_lead_booking_invoice_payment(api):
    """Scenario 2: Full lifecycle lead -> booking -> invoice -> payment."""
    lead = ("lead_id,created,name,business,email,phone,source,status\n"
            "L901,2026-09-01,Sam Vance,Vance Logistics,sam@vance.example,555-9011,Website form,Won\n")
    booking = ("booking_id,date,client_name,email,service,status,price\n"
               "B901,2026-09-10,Vance Logistics,sam@vance.example,Content Day,completed,1200\n")
    assert upload(api, "leads.csv", lead).status_code == 200
    assert upload(api, "bookings.csv", booking).status_code == 200

    # Booking is unbilled
    s1 = api.get("/api/state").json
    assert s1["metrics"]["never_billed_total"] == 1200.0
    assert any(row["booking_id_or_month"] == "B901" for row in s1["money"]["never_billed"])

    # Upload invoice referencing booking B901
    invoice = ("invoice_no,bill_to,email,issued,due,amount,status,memo\n"
               "INV-901,Vance Logistics,sam@vance.example,2026-09-12,2026-09-26,1200,unpaid,Shoot B901\n")
    assert upload(api, "invoices.csv", invoice).status_code == 200
    s2 = api.get("/api/state").json
    assert s2["metrics"]["never_billed_total"] == 0.0
    assert s2["metrics"]["overdue_total"] == 1200.0

    # Upload bank payment clearing invoice
    payment = ("payment_id,date,payer,payer_email,amount,method,reference\n"
               "PAY-901,2026-09-28,Vance Logistics,sam@vance.example,1200,bank,INV-901\n")
    assert upload(api, "payments.csv", payment).status_code == 200
    s3 = api.get("/api/state").json
    assert s3["metrics"]["overdue_total"] == 0.0
    assert s3["metrics"]["we_owe_total"] == 0.0


def test_overpayment_adds_credit_owed(api):
    """Scenario 3: $1,000 payment against a $700 invoice clears invoice and adds $300 credit."""
    invoice = ("invoice_no,bill_to,email,issued,due,amount,status,memo\n"
               "INV-700,Summit Peak,summit@example.com,2026-09-01,2026-09-15,700,unpaid,Session\n")
    payment = ("payment_id,date,payer,payer_email,amount,method,reference\n"
               "PAY-1000,2026-09-20,Summit Peak,summit@example.com,1000,bank,INV-700\n")
    assert upload(api, "invoices.csv", invoice).status_code == 200
    assert upload(api, "payments.csv", payment).status_code == 200
    state = api.get("/api/state").json
    assert state["metrics"]["overdue_total"] == 0.0
    assert state["metrics"]["we_owe_total"] == 300.0
    assert any(c["client"] == "Summit Peak" and c["amount"] == 300.0 for c in state["money"]["we_owe"])


def test_booking_b123_unbilled_cleared_by_referencing_invoice(api):
    """Scenario 4: Booking B123 unbilled work disappears after invoice explicitly references B123."""
    booking = ("booking_id,date,client_name,email,service,status,price\n"
               "B123,2026-08-15,Ironclad Gym,iron@gym.example,Studio Half Day,completed,900\n")
    assert upload(api, "bookings.csv", booking).status_code == 200
    s1 = api.get("/api/state").json
    assert any(row["booking_id_or_month"] == "B123" for row in s1["money"]["never_billed"])

    invoice = ("invoice_no,bill_to,email,issued,due,amount,status,memo\n"
               "INV-888,Ironclad Gym,iron@gym.example,2026-09-01,2026-09-15,900,unpaid,Ref: B123\n")
    assert upload(api, "invoices.csv", invoice).status_code == 200
    s2 = api.get("/api/state").json
    assert not any(row["booking_id_or_month"] == "B123" for row in s2["money"]["never_billed"])


def test_retainer_zero_dollar_booking_not_unbilled(api):
    """Scenario 5: $0 retainer package bookings (e.g. B023) are not separately billable."""
    booking = ("booking_id,date,client_name,email,service,status,price\n"
               "B023,2026-07-20,Apex Physical Therapy,kim@apexpt.example,Retainer Shoot,completed,0\n")
    assert upload(api, "bookings.csv", booking).status_code == 200
    state = api.get("/api/state").json
    assert state["metrics"]["never_billed_total"] == 0.0
    assert len(state["money"]["never_billed"]) == 0


def test_similar_names_with_conflicting_contacts_kept_separate(api):
    """Scenario 6: Similar names with conflicting contact details are kept strictly separate."""
    b1 = ("booking_id,date,client_name,email,service,status,price\n"
          "B801,2026-09-10,Crown Auto Detailing,dan@crownauto.example,Content Day,completed,1000\n")
    b2 = ("booking_id,date,client_name,email,service,status,price\n"
          "B802,2026-09-12,Crown Barbers,marcus@crownbarbers.example,Content Day,completed,1000\n")
    assert upload(api, "b1.csv", b1).status_code == 200
    assert upload(api, "b2.csv", b2).status_code == 200
    state = api.get("/api/state").json
    assert state["metrics"]["client_count"] == 2
    names = [c["canonical_name"] for c in state["clients"]]
    assert "Crown Auto Detailing" in names
    assert "Crown Barbers" in names


def test_batch_upload_all_eight_pack_file_types_in_reversed_order(api):
    """Scenario 7: Batch upload all 8 pack file types together in reversed dependency order."""
    batch_files = {
        "messages.txt": "[2026-09-25 10:00] EMAIL from alex@revbatch.example: For video V7701, please trim the ending logo.\n",
        "production_board.csv": "video_id,client,title,editor,stage,notes_on_board,revisions,editor_hours,client_approved_on,shoot_booking\nV7701,RevBatch Co,Product Demo,Dev,In Progress,,0,3.0,,B7701\n",
        "payments.csv": "payment_id,date,payer,payer_email,amount,method,reference\nPAY-7701,2026-09-28,RevBatch Co,alex@revbatch.example,1500,bank,INV-7701\n",
        "invoices.csv": "invoice_no,bill_to,email,issued,due,amount,status,memo\nINV-7701,RevBatch Co,alex@revbatch.example,2026-09-15,2026-09-29,1500,unpaid,Demo shoot B7701\n",
        "bookings.csv": "booking_id,date,client_name,email,service,status,price\nB7701,2026-09-10,RevBatch Co,alex@revbatch.example,Content Day,completed,1500\n",
        "leads.csv": "lead_id,created,name,business,email,phone,source,status\nL7701,2026-09-01,Alex Rev,RevBatch Co,alex@revbatch.example,555-7701,Website form,Won\n",
        "costs.csv": "item,cost,note\nStudio Time / Hour,40.0,Standard studio rate\n",
        "team.csv": "name,role,joined,pay\nDev,Editor,2026-09-01,$40/hour\n"
    }
    res = upload_batch(api, batch_files)
    assert res.status_code == 200
    data = res.json
    assert data["status"] == "success"
    assert data["total_files"] == 8
    assert data["imported_count"] == 8
    assert data["rejected_count"] == 0
    assert "8 files processed: 8 imported, 0 duplicate, 0 rejected." in data["summary"]

    # Verify state reflects full cross-file resolution
    state = api.get("/api/state").json
    assert state["metrics"]["client_count"] == 1
    assert state["metrics"]["overdue_total"] == 0.0  # Cleared by payment
    assert state["metrics"]["never_billed_total"] == 0.0  # Cleared by invoice


def test_batch_upload_partial_failure_atomic_policy_and_retry(api):
    """Scenario 8: Batch upload with 1 valid file and 1 malformed file reports partial success and permits retry."""
    batch_files = {
        "valid_bookings.csv": "booking_id,date,client_name,email,service,status,price\nB9901,2026-09-10,Alpha Co,alpha@example.com,Content Day,completed,1000\n",
        "invalid_invoices.csv": "invoice_no,bill_to,email,issued,due,amount,status,memo\nINV-BAD,Alpha Co,alpha@example.com,2026-09-12,2026-09-26,NOT_MONEY,unpaid,Broken\n"
    }
    res = upload_batch(api, batch_files)
    assert res.status_code == 200
    data = res.json
    assert data["status"] == "partial_success"
    assert data["imported_count"] == 1
    assert data["rejected_count"] == 1
    assert "2 files processed: 1 imported, 0 duplicate, 1 rejected." in data["summary"]

    # Verify atomic retention of valid file
    state = api.get("/api/state").json
    assert state["metrics"]["never_billed_total"] == 1000.0

    # Retry with corrected invoice file
    retry_files = {
        "valid_bookings.csv": "booking_id,date,client_name,email,service,status,price\nB9901,2026-09-10,Alpha Co,alpha@example.com,Content Day,completed,1000\n",
        "corrected_invoices.csv": "invoice_no,bill_to,email,issued,due,amount,status,memo\nINV-FIXED,Alpha Co,alpha@example.com,2026-09-12,2026-09-26,1000,unpaid,Ref: B9901\n"
    }
    res2 = upload_batch(api, retry_files)
    assert res2.status_code == 200
    data2 = res2.json
    assert data2["duplicate_count"] == 1  # Bookings skipped idempotently
    assert data2["imported_count"] == 1   # Invoice imported
    assert data2["rejected_count"] == 0


def test_owner_decision_persistence(api):
    """Scenario 9: Owner decisions persist and update action states across refreshes."""
    # Seed invoice to trigger action
    inv = ("invoice_no,bill_to,email,issued,due,amount,status,memo\n"
           "INV-DEC,Patel Insurance Group,raj@patelinsures.com,2026-09-01,2026-09-15,2500,unpaid,retainer\n")
    assert upload(api, "inv.csv", inv).status_code == 200
    
    # Post owner decision
    dec_res = api.post("/api/decision", json={
        "action_id": "call_raj_patel",
        "decision": "defer",
        "status": "deferred",
        "notes": "Spoke to Raj; deferred to Wednesday review"
    })
    assert dec_res.status_code == 200
    assert dec_res.json["status"] == "success"

    # Verify decision persists in /api/state
    state = api.get("/api/state").json
    assert "call_raj_patel" in state["decisions"]
    assert state["decisions"]["call_raj_patel"]["status"] == "deferred"


def test_downloadable_answers_json_endpoint(api):
    """Scenario 10: /api/export-answers provides downloadable answers.json with live URL and computed results."""
    rv = api.get("/api/export-answers")
    assert rv.status_code == 200
    assert 'attachment; filename="answers.json"' in rv.headers.get("Content-Disposition", "")
    data = rv.json
    assert data["pack_id"] == "01"
    assert data["live_link"] == "https://axeom-business-intelligence.vercel.app"
    assert "client_count" in data
    assert "overdue_total" in data
    assert "never_billed_total" in data
    assert "we_owe" in data

