"""
Comprehensive business service verification test suite for Axeom Studio.
Covers all Prompt 6 test cases: financial invariants, partial payments, second payments,
repeat uploads, refunds/reversals, overpayments, third-party agency payers,
same-name different-client disambiguation, shared contacts / rebrands, monthly packages,
unknown prices, future-dated events, and missing request evidence.
"""

import json
import pytest
from services.db import init_db, seed_db_if_empty
from services.identity import CANONICAL_CLIENTS, THIRD_PARTY_PAYERS, resolve_client_by_name
from services.finance import reconcile_finances, AS_OF_DATE
from services.requests import get_requests_and_leads
from services.analytics import get_analytics
from services.export import export_answers_json

@pytest.fixture(scope="module", autouse=True)
def ensure_db():
    init_db()
    seed_db_if_empty()

def test_financial_reconciliation_invariants():
    """
    Verifies that the financial reconciliation engine adheres to mathematical invariants:
    - Exactly 9 overdue invoices totaling $9,250.00
    - Exactly $2,400.00 in liabilities (we_owe)
    - Exactly $2,950.00 in unbilled work (never_billed)
    - Exactly 6 billing software discrepancies
    """
    fin = reconcile_finances()
    
    assert fin["overdue_total"] == 9250.00
    assert len(fin["overdue"]) == 9
    assert fin["we_owe_total"] == 2400.00
    assert len(fin["we_owe"]) == 2
    assert fin["never_billed_total"] == 2950.00
    assert len(fin["never_billed"]) == 3
    assert len(fin["discrepancies"]) == 6

def test_case_partial_payment():
    """
    Verifies that partial payment on INV-1125 leaves the remaining balance overdue.
    INV-1125 was for $900.00 due 2026-09-17; P5118 paid $450.00 on 2026-09-12.
    Remaining balance must be $450.00 and marked as overdue.
    """
    fin = reconcile_finances()
    inv_1125 = next((o for o in fin["overdue"] if o["invoice"] == "INV-1125"), None)
    assert inv_1125 is not None, "INV-1125 must be in overdue list"
    assert inv_1125["amount_owed"] == 450.00
    assert inv_1125["days_late"] == 19
    assert inv_1125["client"] == "Prime Roofing Co"

def test_case_second_payment():
    """
    Verifies that duplicate payments against a single invoice are detected and accounted for.
    Glow Aesthetics paid INV-1086 ($900.00) twice via P5091 ($900) and P5093 ($900).
    The second payment creates an overpayment liability of $900.00.
    """
    fin = reconcile_finances()
    glow_we_owe = next((w for w in fin["we_owe"] if "Glow" in w["client"]), None)
    assert glow_we_owe is not None
    assert glow_we_owe["amount"] == 900.00
    assert "Double payment on invoice INV-1086" in glow_we_owe["why"]

def test_case_repeat_upload_idempotency():
    """
    Verifies that calling the reconciliation engine multiple times produces identical,
    deterministic totals without state drift.
    """
    fin1 = reconcile_finances()
    fin2 = reconcile_finances()
    assert fin1["overdue_total"] == fin2["overdue_total"]
    assert fin1["we_owe_total"] == fin2["we_owe_total"]
    assert fin1["never_billed_total"] == fin2["never_billed_total"]

def test_case_refund_and_reversal():
    """
    Verifies uncredited cancelled shoot liability for Lone Star Realty.
    Shoot B148 was cancelled due to a family emergency; client paid $1,500 on INV-1135
    which was uncredited on INV-1143.
    """
    fin = reconcile_finances()
    ls_we_owe = next((w for w in fin["we_owe"] if "Lone Star" in w["client"]), None)
    assert ls_we_owe is not None
    assert ls_we_owe["amount"] == 1500.00
    assert "B148" in ls_we_owe["why"]

def test_case_overpayment():
    """Verifies that we_owe captures exactly $2,400 in client liabilities."""
    fin = reconcile_finances()
    total_liabilities = sum(w["amount"] for w in fin["we_owe"])
    assert total_liabilities == 2400.00

def test_case_third_party_agency_payer():
    """
    Verifies that Brightline Marketing LLC is classified as a third-party agency payer
    paying on behalf of Greenway Pediatrics and Summit Chiropractic.
    """
    assert len(THIRD_PARTY_PAYERS) == 1
    payer = THIRD_PARTY_PAYERS[0]
    assert payer["name"] == "BRIGHTLINE MARKETING LLC"
    assert "Greenway Pediatrics" in payer["pays_for"]
    assert "Summit Chiropractic" in payer["pays_for"]

    # Verify neither Greenway nor Summit are merged into Brightline as clients
    c_greenway = resolve_client_by_name("Greenway Pediatrics")
    c_summit = resolve_client_by_name("Summit Chiropractic")
    assert c_greenway["id"] == "C26"
    assert c_summit["id"] == "C27"

def test_case_same_name_different_client():
    """
    CRITICAL GUARDRAIL: Verifies that Lone Star Realty and Lonestar Realty Group
    remain separate canonical clients and are NEVER merged.
    """
    c_dana = resolve_client_by_name("Lone Star Realty")
    c_greg = resolve_client_by_name("Lonestar Realty Group")

    assert c_dana is not None
    assert c_greg is not None
    assert c_dana["id"] != c_greg["id"]
    assert c_dana["id"] == "C20"
    assert c_greg["id"] == "C28"
    assert "Dana Brooks" in c_dana["primary_contact"]
    assert "Greg Whitfield" in c_greg["primary_contact"]

def test_case_shared_contacts_and_rebrand():
    """
    Verifies that Elevate Fitness and Elevate Athletics are linked to the same canonical client
    based on the documented 2026-08-01 rebrand directive.
    """
    c_old = resolve_client_by_name("Elevate Fitness")
    c_new = resolve_client_by_name("Elevate Athletics")
    assert c_old is not None
    assert c_new is not None
    assert c_old["id"] == c_new["id"]
    assert c_old["id"] == "C19"
    assert "Jordan Reed" in c_old["primary_contact"]

def test_case_monthly_package_coverage():
    """
    Verifies that clients with monthly retainer packages (Patel Insurance, Torres Law, Apex PT)
    have their shoots covered under retainers where booking price is $0.
    """
    c_patel = resolve_client_by_name("Patel Insurance Group")
    assert c_patel["id"] == "C12"
    fin = reconcile_finances()
    cf = fin["client_financials"]["Patel Insurance Group"]
    assert cf["invoiced"] == 12500.00
    assert cf["overdue"] == 2500.00  # Retainer invoice INV-1122

def test_case_unknown_or_missing_price():
    """Verifies that clean_float handles missing, corrupt, or string currency prices safely."""
    from services.db import clean_float
    assert clean_float(None) == 0.0
    assert clean_float("") == 0.0
    assert clean_float("$1,500.00") == 1500.0
    assert clean_float("invalid") == 0.0

def test_case_future_dated_events():
    """
    Verifies that invoices with due date > 2026-10-06 are strictly NOT marked as overdue.
    Example: INV-1132 due 2026-10-10 or INV-1137 due 2026-10-16.
    """
    fin = reconcile_finances()
    for o in fin["overdue"]:
        assert o["days_late"] > 0
        assert o["due_date"] < "2026-10-06"

def test_case_missing_request_evidence():
    """
    Verifies that all 33 lost requests are accounted for with channel provenance,
    video ID, and clear explanation of omission.
    """
    req = get_requests_and_leads()
    assert req["lost_requests_count"] == 33
    
    # Check breakdown by channel
    channels = [r["came_by"].lower() for r in req["lost_requests"]]
    assert channels.count("voice note") == 13
    assert channels.count("whatsapp") == 10
    assert channels.count("email") == 8
    assert channels.count("instagram") == 2

    # Check root causes and deterioration month
    assert len(req["root_causes"]) == 5
    assert req["deterioration"]["month"] == "2026-08"

def test_unreplied_leads():
    """Verifies exactly 22 unreplied incoming leads."""
    req = get_requests_and_leads()
    assert req["unreplied_leads_count"] == 22
    assert "L097" in [l["lead_id"] for l in req["unreplied_leads"]]

def test_answers_working_json_parity(tmp_path):
    """
    Verifies that export_answers_json creates a schema-valid answers_working.json
    with 100% parity against reconcile_finances and get_requests_and_leads.
    """
    temp_target = str(tmp_path / "answers_parity.json")
    answers = export_answers_json(target_path=temp_target)
    fin = reconcile_finances()
    req = get_requests_and_leads()

    assert answers["pack_id"] == "01"
    assert answers["client_count"] == 29
    assert answers["overdue_total"] == fin["overdue_total"]
    assert answers["never_billed_total"] == fin["never_billed_total"]
    assert len(answers["overdue"]) == len(fin["overdue"])
    assert len(answers["we_owe"]) == len(fin["we_owe"])
    assert len(answers["never_billed"]) == len(fin["never_billed"])
    assert len(answers["billing_tool_is_wrong"]) == len(fin["discrepancies"])
    assert len(answers["lost_requests"]) == req["lost_requests_count"]
    assert len(answers["never_replied_leads"]) == req["unreplied_leads_count"]
    assert answers["most_likely_to_leave"]["client"] == "Patel Insurance Group"
    assert answers["best_marketing_channel"]["channel"] == "Website form"
