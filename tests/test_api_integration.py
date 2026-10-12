"""
End-to-end integration tests for Flask REST API endpoints and decision persistence.
"""

import json
import pytest
from app import app
from services.db import init_db, seed_db_if_empty

def test_index_page_loads(client):
    rv = client.get('/')
    assert rv.status_code == 200
    assert b"AXEOM" in rv.data

def test_guide_page_loads(client):
    rv = client.get('/guide')
    assert rv.status_code == 200
    assert b"Axeom Challenge" in rv.data

def test_api_state_endpoint(client):
    rv = client.get('/api/state')
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert data["status"] == "success"
    
    # Financial metrics verification
    metrics = data["metrics"]
    assert metrics["as_of_date"] == "2026-10-06"
    assert metrics["active_clients_count"] == 29
    assert metrics["overdue_total"] == 9250.00
    assert metrics["overdue_count"] == 9
    assert metrics["we_owe_total"] == 2400.00
    assert metrics["never_billed_total"] == 2950.00
    assert metrics["discrepancies_count"] == 6
    assert metrics["lost_requests_count"] == 33
    assert metrics["unreplied_leads_count"] == 22
    assert "revision" in data
    assert "recent_uploads" in data

def test_api_decisions_persistence(client):
    payload = {
        "action_id": "test_action_01",
        "decision_type": "action",
        "status": "in_progress",
        "owner_notes": "Owner tested decision persistence"
    }
    rv = client.post('/api/decisions', data=json.dumps(payload), content_type='application/json')
    assert rv.status_code == 200
    res = json.loads(rv.data)
    assert res["status"] == "success"
    assert res["decision"]["status"] == "in_progress"

    # Verify decision is reflected in state
    state_rv = client.get('/api/state')
    state_data = json.loads(state_rv.data)
    assert "test_action_01" in state_data["decisions"]
    assert state_data["decisions"]["test_action_01"]["status"] == "in_progress"

def test_api_client_history_dossier(client):
    rv = client.get('/api/client/C12')
    assert rv.status_code == 200
    res = json.loads(rv.data)
    assert res["status"] == "success"
    client_data = res["data"]
    assert client_data["client"]["canonical_name"] == "Patel Insurance Group"
    assert len(client_data["bookings"]) == 6
    assert len(client_data["invoices"]) == 5
    assert len(client_data["videos"]) == 20
    assert len(client_data["messages"]) == 17

def test_api_search(client):
    rv = client.get('/api/search?q=INV-1066')
    assert rv.status_code == 200
    res = json.loads(rv.data)
    assert res["status"] == "success"
    assert len(res["results"]) > 0
    assert any("INV-1066" in str(item) for item in res["results"])

def test_api_export_answers(client):
    rv = client.get('/api/export-answers')
    assert rv.status_code == 200
    res = json.loads(rv.data)
    assert res.get("pack_id") == "01"
    assert res["client_count"] == 29
