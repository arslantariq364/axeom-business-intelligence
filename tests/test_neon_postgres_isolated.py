"""
Isolated Neon PostgreSQL End-to-End Suite.
Connects to Neon PostgreSQL dev branch, provisions an ephemeral isolated schema,
executes table migrations, multi-file batch uploads, entity resolution,
and financial recomputations against true cloud PostgreSQL.
"""

import os
import pytest
import psycopg
from services.db import normalize_database_url

def get_neon_dev_url():
    if not os.path.exists(".env"):
        return None
    with open(".env", "r") as f:
        for line in f:
            if line.startswith("DEV_DATABASE_URL="):
                val = line.split("=", 1)[1].strip("\"'\n\r ")
                return val.replace("-pooler", "")
    return None

DEV_DIRECT_URL = get_neon_dev_url()

pytestmark = pytest.mark.skipif(
    not DEV_DIRECT_URL,
    reason="Requires DEV_DATABASE_URL in .env"
)


@pytest.fixture(scope="module")
def neon_isolated_schema():
    """Provisions and tears down a completely isolated ephemeral schema on Neon."""
    admin_url = normalize_database_url(DEV_DIRECT_URL)
    test_schema = "axeom_iso_neon_qa"

    # 1. Create isolated schema on Neon
    with psycopg.connect(admin_url, autocommit=True) as conn:
        conn.execute(f"DROP SCHEMA IF EXISTS {test_schema} CASCADE;")
        conn.execute(f"CREATE SCHEMA {test_schema};")

    # Set env vars to direct the application to this schema
    old_env = os.environ.get("DATABASE_URL")
    old_force = os.environ.get("AXEOM_FORCE_SQLITE")
    old_schema = os.environ.get("AXEOM_PG_SCHEMA")

    os.environ["DATABASE_URL"] = admin_url
    os.environ["AXEOM_PG_SCHEMA"] = test_schema
    os.environ.pop("AXEOM_FORCE_SQLITE", None)

    from services.db import init_db, invalidate_caches
    invalidate_caches()
    init_db(force=True)

    yield test_schema

    # Teardown
    invalidate_caches()
    if old_env is not None:
        os.environ["DATABASE_URL"] = old_env
    else:
        os.environ.pop("DATABASE_URL", None)
    if old_force is not None:
        os.environ["AXEOM_FORCE_SQLITE"] = old_force
    if old_schema is not None:
        os.environ["AXEOM_PG_SCHEMA"] = old_schema
    else:
        os.environ.pop("AXEOM_PG_SCHEMA", None)

    with psycopg.connect(admin_url, autocommit=True) as conn:
        conn.execute(f"DROP SCHEMA IF EXISTS {test_schema} CASCADE;")


def test_neon_postgres_batch_upload_and_reconciliation(neon_isolated_schema):
    """Verifies that all 8 original pack files ingest into Neon PostgreSQL and compute accurate metrics."""
    from services.ingest import process_batch_upload
    from services.finance import reconcile_finances
    from services.identity import get_canonical_clients
    from services.requests import get_requests_and_leads
    from services.analytics import get_analytics

    # Construct batch with all 8 file roles in reversed dependency order
    files = {
        "messages.txt": (
            "[2026-04-24 10:15] VOICE NOTE from Mike (Mike's Roofing, +1-214-555-0199): Hey guys, for video V010, make the captions bigger please.\n"
            "[2026-09-25 14:00] EMAIL from alex@revbatch.example: For video V7701, please trim the ending logo.\n"
        ).encode("utf-8"),
        "production_board.csv": (
            "video_id,client,title,editor,stage,notes_on_board,revisions,editor_hours,client_approved_on,shoot_booking\n"
            "V010,Mike's Roofing,Commercial Roof,Rita,Delivered,,1,4.0,2026-05-01,B010\n"
            "V7701,RevBatch Co,Product Demo,Dev,In Progress,,0,3.0,,B7701\n"
        ).encode("utf-8"),
        "payments.csv": (
            "payment_id,date,payer,payer_email,amount,method,reference\n"
            "P-NEON-1,28/09/2026,RevBatch Co,alex@revbatch.example,1800,bank,INV-7701\n"
        ).encode("utf-8"),
        "invoices.csv": (
            "invoice_no,bill_to,email,issued,due,amount,status,memo\n"
            "INV-7701,RevBatch Co,alex@revbatch.example,2026-09-10,2026-09-24,1500,unpaid,Ref: B7701\n"
            "INV-7702,Overdue Client,overdue@example.com,2026-09-01,2026-09-15,850,unpaid,Old Work\n"
        ).encode("utf-8"),
        "bookings.csv": (
            "booking_id,date,client_name,email,service,status,price\n"
            "B7701,09/10/2026,RevBatch Co,alex@revbatch.example,Content Day,completed,1500\n"
            "B7702,09/20/2026,Unbilled Client,unbilled@example.com,Podcast Studio,completed,750\n"
            "B7703,09/22/2026,Retainer Client,retainer@example.com,Retainer Shoot,completed,0\n"
        ).encode("utf-8"),
        "leads.csv": (
            "lead_id,created,name,business,email,phone,source,status\n"
            "L7701,2026-09-01,Alex Rev,RevBatch Co,alex@revbatch.example,555-7701,Website form,Won\n"
        ).encode("utf-8"),
        "costs.csv": "item,cost,note\nStudio Time / Hour,40.0,Standard studio rate\n".encode("utf-8"),
        "team.csv": "name,role,joined,pay\nDev,Editor,2026-09-01,$40/hour\nRita,Editor,2026-01-01,$30/hour\n".encode("utf-8")
    }

    res = process_batch_upload(files)
    assert res["status"] == "success"
    assert res["imported_count"] == 8
    assert res["rejected_count"] == 0

    # 1. Identity Verification on Neon
    clients = get_canonical_clients()
    client_names = {c["canonical_name"] for c in clients}
    assert "RevBatch Co" in client_names
    assert "Unbilled Client" in client_names
    assert "Overdue Client" in client_names

    # 2. Financial Reconciliation on Neon
    fin = reconcile_finances()
    # INV-7701 was $1,500, paid with $1,800 -> $300 overpayment in we_owe
    assert fin["we_owe_total"] == 300.0
    assert any(w["client"] == "RevBatch Co" and w["amount"] == 300.0 for w in fin["we_owe"])

    # Overdue invoice INV-7702 is $850
    assert fin["overdue_total"] == 850.0
    assert any(o["invoice"] == "INV-7702" for o in fin["overdue"])

    # B7701 was explicitly referenced by INV-7701 -> NOT unbilled
    # B7703 is $0 retainer shoot -> NOT unbilled
    # B7702 is completed $750 without invoice -> unbilled!
    assert fin["never_billed_total"] == 750.0
    assert any(n["booking_id_or_month"] == "B7702" for n in fin["never_billed"])

    # 3. Requests Tracking on Neon
    req = get_requests_and_leads()
    assert req["lost_requests_count"] >= 1
    assert any(lr["video_id"] == "V010" for lr in req["lost_requests"])

    # 4. Analytics Attribution on Neon
    ana = get_analytics(fin=fin)
    wf_channel = next(ch for ch in ana["marketing"]["channels"] if ch["name"] == "Website form")
    assert wf_channel["leads"] == 1
    assert wf_channel["converted"] == 1
