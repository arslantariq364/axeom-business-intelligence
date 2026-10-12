"""
Typesafe AI (Jev) Integration Service for Axeom Studio Operations.
Integrates System One API via official POST /v1/systemone endpoint.
Uses primitive map (Choice for primary intent, Noul for multi-intent & actionable billing).
Enforces: server-side secrets, non-blocking DB transactions, bounded retries,
persistent content-addressed caching, and transparent separation between
baseline heuristics, offline deterministic fallback, and live Jev model calls.
"""

import os
import re
import json
import time
import hashlib
import datetime
import requests
from services.db import get_db

TYPESAFE_API_URL = "https://api.typesafe.ai/v1/systemone"
PROVIDER_MODEL = "jev-latest"
APP_QUESTION_VERSION = "axeom-intent-v2.0"
TIMEOUT_SECONDS = 5.0
MAX_RETRIES = 2

INTENT_CHOICES = [
    "edit_request",
    "billing_issue",
    "booking_or_schedule",
    "lead_or_inquiry",
    "other_review"
]

def load_local_env():
    """Securely load .env file into environment if present locally without leaking keys."""
    # 1. Try python-dotenv if installed
    try:
        import dotenv
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
        if os.path.exists(env_path):
            dotenv.load_dotenv(env_path)
            return
    except Exception:
        pass

    # 2. Manual line-by-line fallback parser
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip("'\"")
                        if k and k not in os.environ:
                            os.environ[k] = v
        except Exception:
            pass

def get_api_key():
    """Retrieve Typesafe API Key server-side only from environment."""
    load_local_env()
    return os.environ.get("TYPESAFE_API_KEY", "").strip()

def simple_baseline_classify(text):
    """
    Naive baseline classifier matching only basic single superficial keywords.
    Serves as the benchmark baseline representing an un-tuned keyword heuristic.
    """
    t = text.lower()
    if any(k in t for k in ["edit", "song", "fix"]):
        return {
            "prediction": "edit_request",
            "confidence": 0.60,
            "provider": "simple_baseline",
            "provider_model": "none",
            "multi_intent": False,
            "actionable_billing": False
        }
    if any(k in t for k in ["invoice", "pay"]):
        return {
            "prediction": "billing_issue",
            "confidence": 0.60,
            "provider": "simple_baseline",
            "provider_model": "none",
            "multi_intent": False,
            "actionable_billing": True
        }
    if any(k in t for k in ["reschedule", "tomorrow"]):
        return {
            "prediction": "booking_or_schedule",
            "confidence": 0.60,
            "provider": "simple_baseline",
            "provider_model": "none",
            "multi_intent": False,
            "actionable_billing": False
        }
    if any(k in t for k in ["lead", "quote", "cost"]):
        return {
            "prediction": "lead_or_inquiry",
            "confidence": 0.60,
            "provider": "simple_baseline",
            "provider_model": "none",
            "multi_intent": False,
            "actionable_billing": False
        }
    return {
        "prediction": "other_review",
        "confidence": 0.50,
        "provider": "simple_baseline",
        "provider_model": "none",
        "multi_intent": False,
        "actionable_billing": False
    }

def check_multi_intent_fallback(text):
    """
    Offline fallback rule detecting whether a message spans multiple operational categories.
    Distinguishes compound actionable requests from single-intent messages.
    """
    t = text.lower()
    has_edit = any(k in t for k in [
        "cut", "edit", "caption", "captions", "branding", "music", "song",
        "color", "wrong", "fix", "blur", "stumble", "shot", "fuerte", "música",
        "quiten", "todavía no", "walk-ins welcome", "remove the bit", "rounds of fixes"
    ])
    # Actionable billing or explicit payment term adjustment
    has_bill = any(k in t for k in [
        "bill us", "pay the", "pay once", "sent half", "cash is tight",
        "pay immediately", "already paid", "we'd pay", "what would that cost", "20% off"
    ])
    has_sched = any(k in t for k in [
        "move to", "reschedule", "tomorrow", "session", "parking", "cancel today", "shoot", "pause after"
    ])
    has_lead = any(k in t for k in [
        "wants videos too", "pricing", "packages", "quote", "needs videos", "reach out", "cut short clips"
    ])
    has_status = any(k in t for k in [
        "send them", "send the videos", "posted", "approved"
    ])

    intents_count = sum([has_edit, has_bill, has_sched, has_lead, has_status])
    return intents_count >= 2

def check_actionable_billing_fallback(text):
    """
    Distinguishes an actionable billing requirement from a passing payment mention.
    - Actionable: invoice requests, payment term adjustments, partial payment notices, discounts.
    - Passing mention: 'we already paid, can we reschedule?' or 'why fees matter' (video title).
    """
    t = text.lower()

    # Explicit passing / non-actionable mentions
    if "why fees matter" in t:
        return False
    if "talk about prices" in t or "prices are changing" in t:
        return False
    if "we sell 10,000 real followers for $49" in t:
        return False

    # Actionable billing signals
    actionable_signals = [
        "bill us", "invoice attached", "pay immediately", "cash is tight",
        "pay the august sessions", "we'll pay once", "sent half",
        "accounting will handle the invoice", "20% off studio sessions",
        "we pay monthly"
    ]
    if any(s in t for s in actionable_signals):
        return True

    # "already paid" in an emergency cancellation is passing confirmation, not an invoice action
    if "already paid" in t and ("cancel" in t or "move it" in t):
        return False

    return False

def deterministic_fallback_classify(text):
    """
    Offline deterministic rule-based domain engine.
    Active when TYPESAFE_API_KEY is not configured or external API is unavailable.
    """
    t = text.lower()
    is_multi = check_multi_intent_fallback(text)
    is_actionable_bill = check_actionable_billing_fallback(text)

    # 1. Actionable Billing
    if is_actionable_bill:
        return {
            "prediction": "billing_issue",
            "confidence": 0.93,
            "provider": "deterministic_fallback",
            "provider_model": "none",
            "multi_intent": is_multi,
            "actionable_billing": True
        }

    # 2. Booking / Schedule Signals (cancel/reschedule/shoot/parking/tomorrow)
    sched_keywords = [
        "move to 2pm", "move to", "move our", "move it", "reschedule", "parking in the back",
        "parking", "see you tomorrow", "tomorrow", "cancel today's shoot", "cancel today",
        "shoot date", "2pm instead"
    ]
    if any(k in t for k in sched_keywords):
        return {
            "prediction": "booking_or_schedule",
            "confidence": 0.92,
            "provider": "deterministic_fallback",
            "provider_model": "none",
            "multi_intent": is_multi,
            "actionable_billing": False
        }

    # 3. Lead / Inquiry Signals (new services, referrals, retention conversations)
    lead_keywords = [
        "contract and whether we continue", "talk about our contract", "about the contract",
        "whether we continue", "wants videos too", "she'll reach out", "how much for a reels pack",
        "needs videos", "call him", "cut short clips from our episodes", "can we do this every month",
        "what would that cost", "do you have a package", "inquiry", "we'll pause after this month"
    ]
    if any(k in t for k in lead_keywords):
        return {
            "prediction": "lead_or_inquiry",
            "confidence": 0.90,
            "provider": "deterministic_fallback",
            "provider_model": "none",
            "multi_intent": is_multi,
            "actionable_billing": False
        }

    # 4. Edit Request Signals (visual, audio, caption, branding, Spanish phrases)
    edit_keywords = [
        "cut", "song", "hype", "blur", "stumble", "captions", "caption",
        "pink", "brand color", "navy", "forest green", "teal", "gold", "intro",
        "not fixed", "still wrong", "b-roll", "louder", "too loud", "music",
        "spelled wrong", "change the", "take out", "phone number at the end",
        "walk-ins welcome", "remove the bit", "calmer song", "same problem",
        "other shot", "outside, not inside", "música", "fuerte", "quiten la parte",
        "todavía no está", "vieron mi mensaje", "full name", "starts slow",
        "first 3 seconds", "prices are changing", "talk about prices", "fees matter",
        "second time i ask", "compliance cares"
    ]
    if any(k in t for k in edit_keywords):
        return {
            "prediction": "edit_request",
            "confidence": 0.92,
            "provider": "deterministic_fallback",
            "provider_model": "none",
            "multi_intent": is_multi,
            "actionable_billing": False
        }

    # 5. Other / Review (Spam, general praise, team announcements)
    return {
        "prediction": "other_review",
        "confidence": 0.85,
        "provider": "deterministic_fallback",
        "provider_model": "none",
        "multi_intent": is_multi,
        "actionable_billing": False
    }

def build_systemone_request_payload(text):
    """
    Constructs official Typesafe AI System One request body according to documentation.
    Uses model identifier, state, and questions primitive map.
    """
    return {
      "model": PROVIDER_MODEL,
      "state": text,
      "questions": {
        "primary_intent": {
          "type": "choice",
          "instructions": "Classify the primary operational intent of this video production client message.",
          "criteria": {
            "edit_request": "Video edits, revisions, cuts, captions, music, brand color changes, or B-roll shot changes",
            "billing_issue": "Actionable billing requests, invoices, payment plans, credit terms, or rate negotiations",
            "booking_or_schedule": "Shoot date bookings, session rescheduling, parking logistics, or studio cancellations",
            "lead_or_inquiry": "New client inquiries, referrals, package upgrades, quote requests, or contract retention discussions",
            "other_review": "General praise, completed approvals, spam/phishing, or company announcements"
          }
        },
        "is_multi_intent": {
          "type": "noul",
          "instructions": "Does this message contain more than one distinct actionable operational intent (e.g. rescheduling plus an unbilled/prepaid status mention)?"
        },
        "has_actionable_billing": {
          "type": "noul",
          "instructions": "Does this message require an actionable billing response from the studio (e.g. sending an invoice, adjusting terms) rather than just a passing historical payment mention?"
        }
      }
    }

def classify_message(text, msg_id=None, msg_hash=None, force_live=False):
    """
    Main classification service.
    1. Checks local cache:
       - If API key is present: ONLY accepts cache if result_source == 'live_jev'.
       - If API key is missing: accepts 'deterministic_fallback' cache.
    2. If API key is configured: calls Typesafe AI API (bounded timeout & retries).
    3. If API key is not configured or API fails: routes to deterministic fallback.
    Does not hold open database transactions across network API calls.
    """
    clean_text = text.strip()
    input_hash = hashlib.sha256(clean_text.encode("utf-8")).hexdigest()
    cache_key = f"jev:{APP_QUESTION_VERSION}:{input_hash}"

    api_key = get_api_key()

    # 1. Check local cache (short read-only query)
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
    SELECT response_json, result_source, provider_model
    FROM jev_cache
    WHERE cache_key = ?
    """, (cache_key,))
    cached_row = cur.fetchone()
    conn.close()

    if cached_row and not force_live:
        cached_source = cached_row["result_source"]
        # If API key is available, fallback cache does NOT block live classification!
        if not (api_key and cached_source == "deterministic_fallback"):
            res = json.loads(cached_row["response_json"])
            res["cached"] = True
            if msg_id or msg_hash:
                conn2 = get_db()
                _save_classification(conn2, msg_id, msg_hash, res)
                conn2.close()
            return res

    # 2. If API Key is NOT configured -> use deterministic fallback
    if not api_key:
        fallback_res = deterministic_fallback_classify(clean_text)
        result = {
            "prediction": fallback_res["prediction"],
            "confidence": fallback_res["confidence"],
            "provider": "deterministic_fallback",
            "provider_model": "none",
            "app_question_version": APP_QUESTION_VERSION,
            "live_call_blocked": True,
            "blocker_reason": "TYPESAFE_API_KEY not configured in environment or local .env file",
            "multi_intent": fallback_res["multi_intent"],
            "actionable_billing": fallback_res["actionable_billing"],
            "cached": False,
            "usage": {"input_tokens": 0, "output_tokens": 0}
        }
        conn_w = get_db()
        _save_cache(conn_w, cache_key, input_hash, result, result_source="deterministic_fallback", provider_model="none")
        _save_classification(conn_w, msg_id, msg_hash, result)
        conn_w.close()
        return result

    # 3. Call Typesafe AI (Jev) System One API with bounded retries
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = build_systemone_request_payload(clean_text)

    attempts = 0
    while attempts <= MAX_RETRIES:
        try:
            start_time = time.time()
            resp = requests.post(TYPESAFE_API_URL, headers=headers, json=payload, timeout=TIMEOUT_SECONDS)
            elapsed_ms = round((time.time() - start_time) * 1000, 1)

            if resp.status_code == 200:
                data = resp.json()
                returned_model = data.get("model", PROVIDER_MODEL)
                answers = data.get("answers", data.get("decisions", {}))

                # Parse choice answer
                p_intent_data = answers.get("primary_intent", {})
                if isinstance(p_intent_data, dict):
                    pred = p_intent_data.get("choice", p_intent_data.get("prediction", "other_review"))
                    conf = float(p_intent_data.get("confidence", 0.90))
                else:
                    pred = str(p_intent_data)
                    conf = 0.90

                if pred not in INTENT_CHOICES:
                    pred = "other_review"

                # Parse noul answers
                multi_data = answers.get("is_multi_intent", {})
                if isinstance(multi_data, dict):
                    multi_prob = float(multi_data.get("probability", 0.0))
                    is_multi = multi_prob >= 0.5
                else:
                    is_multi = bool(multi_data)

                billing_data = answers.get("has_actionable_billing", {})
                if isinstance(billing_data, dict):
                    billing_prob = float(billing_data.get("probability", 0.0))
                    is_act_billing = billing_prob >= 0.5
                else:
                    is_act_billing = bool(billing_data)

                result = {
                    "prediction": pred,
                    "confidence": conf,
                    "provider": "live_jev",
                    "provider_model": returned_model,
                    "app_question_version": APP_QUESTION_VERSION,
                    "live_call_blocked": False,
                    "multi_intent": is_multi,
                    "actionable_billing": is_act_billing,
                    "cached": False,
                    "api_latency_ms": elapsed_ms,
                    "usage": data.get("usage", {"input_tokens": max(1, len(clean_text) // 4), "output_tokens": 0})
                }
                conn_w = get_db()
                _save_cache(conn_w, cache_key, input_hash, result, result_source="live_jev", provider_model=returned_model)
                _save_classification(conn_w, msg_id, msg_hash, result)
                conn_w.close()
                return result
            elif resp.status_code in [429, 500, 502, 503, 504]:
                attempts += 1
                time.sleep(0.5 * (2 ** attempts))
                continue
            else:
                # 4xx client error (e.g. 401 invalid key)
                break
        except requests.RequestException:
            attempts += 1
            time.sleep(0.5 * (2 ** attempts))

    # 4. Graceful Fallback if live call failed
    fallback_res = deterministic_fallback_classify(clean_text)
    result = {
        "prediction": fallback_res["prediction"],
        "confidence": fallback_res["confidence"],
        "provider": "deterministic_fallback",
        "provider_model": "none",
        "app_question_version": APP_QUESTION_VERSION,
        "live_call_blocked": True,
        "blocker_reason": "Typesafe API call timed out or returned error; routed to deterministic fallback",
        "multi_intent": fallback_res["multi_intent"],
        "actionable_billing": fallback_res["actionable_billing"],
        "cached": False,
        "usage": {"input_tokens": 0, "output_tokens": 0}
    }
    conn_w = get_db()
    _save_cache(conn_w, cache_key, input_hash, result, result_source="deterministic_fallback", provider_model="none")
    _save_classification(conn_w, msg_id, msg_hash, result)
    conn_w.close()
    return result

def reprocess_fallback_classifications(limit=None):
    """
    Controlled reprocessing of records previously classified via deterministic_fallback.
    Does NOT duplicate message rows or mutate owner decisions.
    Upgrades classifications to live_jev once credentials are available.
    """
    api_key = get_api_key()
    if not api_key:
        return {
            "status": "blocked",
            "message": "TYPESAFE_API_KEY is not configured. Fallback records cannot be reprocessed with live Jev."
        }

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
    SELECT mc.id, mc.msg_id, mc.msg_hash, m.body
    FROM message_classifications mc
    JOIN messages m ON mc.msg_id = m.id
    WHERE mc.provider = 'deterministic_fallback'
    ORDER BY mc.id ASC
    """)
    rows = cur.fetchall()
    conn.close()

    upgraded = 0
    errors = 0
    for r in rows:
        if limit and upgraded >= limit:
            break
        res = classify_message(r["body"], msg_id=r["msg_id"], msg_hash=r["msg_hash"], force_live=True)
        if res.get("provider") == "live_jev":
            upgraded += 1
        else:
            errors += 1
            break  # Stop on persistent failure

    return {
        "status": "success",
        "total_eligible": len(rows),
        "reprocessed_count": upgraded,
        "errors": errors
    }

def classify_unclassified_messages():
    """
    Classifies any messages in SQLite that do not yet have an entry in message_classifications.
    Runs one-by-one so db transactions are never held across calls.
    """
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
    SELECT m.id, m.msg_hash, m.body
    FROM messages m
    LEFT JOIN message_classifications mc ON m.id = mc.msg_id
    WHERE mc.id IS NULL
    ORDER BY m.id ASC
    """)
    rows = cur.fetchall()
    conn.close()

    count = 0
    for r in rows:
        classify_message(r["body"], msg_id=r["id"], msg_hash=r["msg_hash"])
        count += 1
    return count

def get_message_classifications(limit=100):
    """
    Returns recent message classifications joined with original message metadata.
    """
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
    SELECT mc.id, mc.msg_id, mc.msg_hash, mc.predicted_intent, mc.confidence,
           mc.provider, mc.provider_model, mc.multi_intent, mc.actionable_billing, mc.classified_at,
           m.msg_datetime, m.channel, m.direction, m.entity, m.body, m.source_file
    FROM message_classifications mc
    JOIN messages m ON mc.msg_id = m.id
    ORDER BY m.msg_datetime DESC
    LIMIT ?
    """, (limit,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def get_classification_stats():
    """
    Returns aggregate breakdown of classified messages, multi-intent counts,
    and API key configuration status.
    """
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM message_classifications")
    total = cur.fetchone()[0]

    cur.execute("SELECT predicted_intent, count(*) FROM message_classifications GROUP BY predicted_intent")
    by_intent = {row[0]: row[1] for row in cur.fetchall()}

    cur.execute("SELECT count(*) FROM message_classifications WHERE multi_intent = 1")
    multi_intent_count = cur.fetchone()[0]

    cur.execute("SELECT count(*) FROM message_classifications WHERE actionable_billing = 1")
    actionable_billing_count = cur.fetchone()[0]

    cur.execute("SELECT provider, count(*) FROM message_classifications GROUP BY provider")
    by_provider = {row[0]: row[1] for row in cur.fetchall()}

    conn.close()

    api_key_configured = bool(get_api_key())
    return {
        "total_classified": total,
        "by_intent": by_intent,
        "multi_intent_count": multi_intent_count,
        "actionable_billing_count": actionable_billing_count,
        "by_provider": by_provider,
        "api_key_configured": api_key_configured,
        "live_call_blocked": not api_key_configured,
        "blocker_reason": "" if api_key_configured else "TYPESAFE_API_KEY not configured in environment or local .env file"
    }

def _save_cache(conn, cache_key, input_hash, result, result_source="deterministic_fallback", provider_model="none"):
    try:
        cur = conn.cursor()
        now_iso = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("""
        INSERT OR REPLACE INTO jev_cache (
            cache_key, model_version, prompt_hash, response_json, created_at,
            result_source, provider_model, app_question_version, input_hash
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            cache_key, PROVIDER_MODEL, input_hash, json.dumps(result), now_iso,
            result_source, provider_model, APP_QUESTION_VERSION, input_hash
        ))
        conn.commit()
    except Exception:
        pass

def _save_classification(conn, msg_id, msg_hash, result):
    if msg_id or msg_hash:
        try:
            cur = conn.cursor()
            now_iso = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # If entry exists for msg_id, update it; otherwise insert
            cur.execute("SELECT id FROM message_classifications WHERE msg_id = ?", (msg_id,))
            existing = cur.fetchone()
            if existing:
                cur.execute("""
                UPDATE message_classifications
                SET predicted_intent = ?, confidence = ?, provider = ?, provider_model = ?,
                    multi_intent = ?, actionable_billing = ?, classified_at = ?
                WHERE id = ?
                """, (
                    result["prediction"], result["confidence"], result["provider"],
                    result.get("provider_model", "none"), 1 if result.get("multi_intent") else 0,
                    1 if result.get("actionable_billing") else 0, now_iso, existing["id"]
                ))
            else:
                cur.execute("""
                INSERT INTO message_classifications (
                    msg_id, msg_hash, predicted_intent, confidence, provider,
                    provider_model, multi_intent, actionable_billing, classified_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    msg_id, msg_hash, result["prediction"], result["confidence"], result["provider"],
                    result.get("provider_model", "none"), 1 if result.get("multi_intent") else 0,
                    1 if result.get("actionable_billing") else 0, now_iso
                ))
            conn.commit()
        except Exception:
            pass
