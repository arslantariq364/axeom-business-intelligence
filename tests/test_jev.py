"""
Test Suite for Typesafe AI (Jev) Integration and Evaluation Harness.
Covers: server-side key safety, offline transparent fallback, caching,
multi-intent detection, held-out evaluation invariants, and pipeline ingestion integration.
"""

import os
import json
import pytest
from app import app
from services.db import get_db
from services.jev import (
    classify_message, simple_baseline_classify, check_multi_intent_fallback,
    get_classification_stats, get_message_classifications,
    TIMEOUT_SECONDS, MAX_RETRIES, PROVIDER_MODEL, APP_QUESTION_VERSION
)
from tests.data_jev_eval import GENUINE_HELDOUT_TEST_SET, REFINEMENT_DEV_SET, TUNING_SET

def test_tuning_and_heldout_separation():
    """Verify strict separation across tuning, refinement, and genuine held-out evaluation sets."""
    assert len(TUNING_SET) == 10
    assert len(REFINEMENT_DEV_SET) == 30
    assert len(GENUINE_HELDOUT_TEST_SET) == 25
    tuning_lines = set(item["line_no"] for item in TUNING_SET)
    dev_lines = set(item["line_no"] for item in REFINEMENT_DEV_SET)
    test_lines = set(item["line_no"] for item in GENUINE_HELDOUT_TEST_SET)
    
    assert len(tuning_lines.intersection(dev_lines)) == 0
    assert len(tuning_lines.intersection(test_lines)) == 0
    assert len(dev_lines.intersection(test_lines)) == 0

def test_evaluation_benchmark_measurements():
    """Verify actual measurements on the 25 genuine held-out examples."""
    base_correct = 0
    fall_correct = 0
    for item in GENUINE_HELDOUT_TEST_SET:
        base_res = simple_baseline_classify(item["text"])
        if base_res["prediction"] == item["true_intent"]:
            base_correct += 1
        fall_res = classify_message(item["text"])
        if fall_res["prediction"] == item["true_intent"]:
            fall_correct += 1
            
    assert base_correct == 9
    assert fall_correct == 24

def test_server_side_key_security():
    """Verify API key is never exposed in returned objects or database records."""
    res = classify_message("Please blur the face of the client in crew day.")
    assert "api_key" not in res
    assert "token" not in res
    assert "Authorization" not in str(res)

    conn = get_db()
    row = conn.execute("SELECT response_json FROM jev_cache LIMIT 1").fetchone()
    conn.close()
    if row:
        cached_data = json.loads(row["response_json"])
        assert "api_key" not in cached_data
        assert "Authorization" not in str(cached_data)

def test_caching_behavior():
    """Verify that identical prompts hit SQLite cache without external requests."""
    import time
    test_text = f"Unique prompt for caching test {time.time()}: Please turn down the background song volume."
    # First call - cache miss
    res1 = classify_message(test_text)
    assert res1["prediction"] == "edit_request"
    assert res1["cached"] is False

    # Second call - cache hit
    res2 = classify_message(test_text)
    assert res2["prediction"] == "edit_request"
    assert res2["cached"] is True

def test_timeout_and_retry_configuration():
    """Verify bounded timeout and retry constants adhere to system rules."""
    assert TIMEOUT_SECONDS == 5.0
    assert MAX_RETRIES == 2

def test_transparent_offline_fallback():
    """When TYPESAFE_API_KEY is not set, response explicitly reports blocker without crashing."""
    res = classify_message("Can we move our shoot to 2pm tomorrow?")
    assert res["prediction"] == "booking_or_schedule"
    if not os.environ.get("TYPESAFE_API_KEY"):
        assert res["live_call_blocked"] is True
        assert "TYPESAFE_API_KEY not configured" in res["blocker_reason"]
        assert res["provider"] == "deterministic_fallback"

def test_multi_intent_detection():
    """Verify multi-intent detection on compound business communications."""
    compound_msg = "We have to cancel today's shoot, family emergency. Can we move it? We already paid."
    assert check_multi_intent_fallback(compound_msg) is True

    single_intent_msg = "See you tomorrow."
    assert check_multi_intent_fallback(single_intent_msg) is False

def test_pipeline_ingest_auto_classification(client):
    """Verify that uploading new messages automatically records message classifications."""
    import time
    ts = int(time.time())
    client_name = f"TestClient{ts}"
    sample_message_data = f'[2026-10-09 14:00] WHATSAPP from +1 214-555-9999 ({client_name}): Please blur the face of the client in our new promo.\n'
    data = {
        'file': (pytest.importorskip("io").BytesIO(sample_message_data.encode('utf-8')), f'new_test_messages_{ts}.txt')
    }
    resp = client.post('/api/upload', data=data, content_type='multipart/form-data')
    assert resp.status_code == 200
    res_json = resp.get_json()
    assert res_json["status"] == "success"

    # Verify classification was stored in database
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
    SELECT mc.predicted_intent, mc.provider, m.body
    FROM message_classifications mc
    JOIN messages m ON mc.msg_id = m.id
    WHERE m.entity LIKE ?
    """, (f'%{client_name}%',))
    row = cur.fetchone()
    conn.close()

    assert row is not None
    assert row["predicted_intent"] == "edit_request"

def test_api_classifications_endpoint(client):
    """Verify /api/classifications endpoint returns summary stats and items."""
    resp = client.get('/api/classifications?limit=10')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "success"
    assert "stats" in data
    assert "total_classified" in data["stats"]
    assert "items" in data
    assert isinstance(data["items"], list)
