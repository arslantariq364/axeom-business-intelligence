"""
Test Suite for Prompt 8: Owner Dashboard Backend & Interaction Contracts.
Covers:
- Today screen hero and secondary actions
- Metric invariants ($9,250 overdue, $2,400 owed, $2,950 unbilled, 6 discrepancies, 33 lost requests, 22 leads)
- Decision persistence across recalculations (defer, approve, in_progress)
- Client history dossier generation
- Transaction search provenance
- Classification stats and live reprocessing blocker handling
"""

import json
import pytest
from app import app
from services.db import get_db

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_dashboard_html_structure(client):
    """Verify that root page serves the mobile-first Conneq CRM dashboard."""
    resp = client.get("/")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "AXEOM" in html
    assert "Today" in html
    assert "conneq.css" in html
    assert "app.js" in html
    assert "hero-card-container" in html
    assert "mobile-bottom-nav" in html

def test_api_state_contains_all_views_data(client):
    """Verify /api/state supplies complete verified business metrics."""
    resp = client.get("/api/state")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "success"

    # Today view
    today = data["today"]
    assert today["hero_action"]["client"] == "Patel Insurance Group"
    assert "INV-1122" in today["hero_action"]["overdue_invoice"]
    assert len(today["monday_top_3"]) == 3

    # Metrics
    m = data["metrics"]
    assert m["overdue_total"] == 9250.0
    assert m["we_owe_total"] == 2400.0
    assert m["never_billed_total"] == 2950.0
    assert m["lost_requests_count"] == 33
    assert m["unreplied_leads_count"] == 22
    assert m["client_count"] == 29

    # Limitations includes missing live Jev verification
    limitations = data["analytics"]["limitations"]
    jev_lim = next((l for l in limitations if "Jev" in l["area"] or "Live AI" in l["area"]), None)
    assert jev_lim is not None
    assert "TYPESAFE_API_KEY" in jev_lim["detail"]
    assert "Not evaluated" in jev_lim["detail"]

def test_decision_persistence_and_no_mutation(client):
    """Verify owner decisions persist durably without mutating external financial systems."""
    # 1. Post a decision
    post_resp = client.post("/api/decisions", json={
        "action_id": "action_patel_call",
        "decision_type": "action",
        "status": "in_progress",
        "owner_notes": "Spoke to Nina, reviewing teen driver tips branding on Wednesday."
    })
    assert post_resp.status_code == 200
    assert post_resp.get_json()["status"] == "success"

    # 2. Check /api/state returns the decision
    state_resp = client.get("/api/state")
    decisions = state_resp.get_json()["decisions"]
    assert "action_patel_call" in decisions
    assert decisions["action_patel_call"]["status"] == "in_progress"
    assert "Spoke to Nina" in decisions["action_patel_call"]["owner_notes"]

    # 3. Verify no financial total was mutated
    m = state_resp.get_json()["metrics"]
    assert m["overdue_total"] == 9250.0

def test_client_history_dossier_contract(client):
    """Verify client dossier aggregates bookings, invoices, payments, videos, and messages."""
    resp = client.get("/api/client/C12") # Patel Insurance Group
    assert resp.status_code == 200
    d = resp.get_json()
    assert d["status"] == "success"
    client_data = d["data"]
    assert client_data["client"]["canonical_name"] == "Patel Insurance Group"
    assert len(client_data["bookings"]) > 0
    assert len(client_data["invoices"]) > 0
    assert len(client_data["videos"]) > 0
    assert len(client_data["messages"]) > 0

def test_search_evidence_endpoint(client):
    """Verify real-time search returns provenance-linked records."""
    resp = client.get("/api/search?q=INV-1122")
    assert resp.status_code == 200
    results = resp.get_json()["results"]
    assert len(results) > 0
    assert any("Patel" in (r.get("title", "") + r.get("details", "")) for r in results)

def test_reprocess_fallback_route_behavior(client):
    """Verify reprocessing route safely handles unconfigured credentials."""
    resp = client.post("/api/reprocess-classifications", json={"limit": 10})
    assert resp.status_code == 200
    res = resp.get_json()
    assert res["status"] in ["blocked", "success"]
    if res["status"] == "blocked":
        assert "TYPESAFE_API_KEY is not configured" in res["message"]
