"""
Export service: generates answers_working.json directly from current database state.
Strictly adheres to the original answers.json template schema.
"""

import os
import json
from services.identity import CANONICAL_CLIENTS, THIRD_PARTY_PAYERS, get_canonical_clients
from services.finance import reconcile_finances
from services.requests import get_requests_and_leads
from services.analytics import get_analytics

def build_answers_json():
    """Build the exact challenge submission JSON directly from current data without file writes."""
    fin = reconcile_finances()
    req = get_requests_and_leads()
    ana = get_analytics()

    # 1. Clients formatted (using canonical client list)
    clients_list = get_canonical_clients(include_archived=False, include_deleted=False)
    clients_formatted = []
    for c in clients_list:
        other_names = sorted(list(set(a for a in c.get('payer_aliases', []) if a != c['canonical_name'])))
        clients_formatted.append({
            "name": c['canonical_name'],
            "other_names_used_in_the_data": other_names,
            "emails": c.get('emails', []),
            "phones": c.get('phones', [])
        })

    # 2. Payers who are not clients
    payers_formatted = []
    for p in THIRD_PARTY_PAYERS:
        payers_formatted.append({
            "name": p['name'],
            "pays_for": p['pays_for']
        })

    # 3. Overdue invoices
    overdue_formatted = []
    for o in fin['overdue']:
        overdue_formatted.append({
            "client": o['client'],
            "invoice": o['invoice'],
            "amount_owed": o['amount_owed'],
            "days_late": o['days_late']
        })

    # 4. We owe
    we_owe_formatted = []
    for w in fin['we_owe']:
        we_owe_formatted.append({
            "client": w['client'],
            "amount": w['amount'],
            "why": w['why']
        })

    # 5. Never billed
    never_billed_formatted = []
    for n in fin['never_billed']:
        never_billed_formatted.append({
            "client": n['client'],
            "booking_id_or_month": n['booking_id_or_month'],
            "amount": n['amount']
        })

    # 6. Billing tool discrepancies
    discrepancies_formatted = []
    for d in fin['discrepancies']:
        discrepancies_formatted.append({
            "invoice": d['invoice'],
            "tool_says": d['tool_says'],
            "truth": d['truth'],
            "how_you_know": d['how_you_know']
        })

    # 7. Lost requests
    lost_formatted = []
    for l in req['lost_requests']:
        lost_formatted.append({
            "video_id": l['video_id'],
            "request_date": l['request_date'],
            "came_by": l['came_by'],
            "why_it_was_lost": l['why_it_was_lost']
        })

    # 8. Unreplied leads
    unreplied_lead_ids = [l['lead_id'] for l in req['unreplied_leads']]

    live_link = os.environ.get("LIVE_LINK", "")
    if not live_link:
        for lp in ["submission/live_link.txt", "docs/live_link.txt"]:
            if os.path.exists(lp):
                live_link = open(lp, encoding="utf-8").read().strip()
                if live_link:
                    break

    # 9. Complete answers dictionary
    answers = {
        "pack_id": "01",
        "your_name": "Arslan Tariq",
        "your_email": os.environ.get("SUBMISSION_EMAIL", "tsa6648@gmail.com"),
        "live_link": live_link or "https://axeom-business-intelligence.vercel.app",
        "video_link": os.environ.get("SUBMISSION_VIDEO_LINK", "https://drive.google.com/file/d/10gawKb1ZWhdLixC-LrnjNLXrgM5K-m9D/view?usp=sharing"),
        "code_or_files_link": "https://github.com/arslantariq364/axeom-business-intelligence",

        "client_count": len(clients_formatted),
        "clients": clients_formatted,
        "payers_who_are_not_clients": payers_formatted,

        "overdue": overdue_formatted,
        "overdue_total": fin['overdue_total'],

        "we_owe": we_owe_formatted,

        "never_billed": never_billed_formatted,
        "never_billed_total": fin['never_billed_total'],

        "billing_tool_is_wrong": discrepancies_formatted,

        "lost_requests": lost_formatted,
        "lost_requests_root_causes": [r['title'] + ": " + r['desc'] for r in req['root_causes']],
        "lost_requests_started_getting_worse_in": req['deterioration']['month'],

        "never_replied_leads": unreplied_lead_ids,

        "most_likely_to_leave": {
            "client": ana['churn']['client'],
            "evidence": ana['churn']['evidence'],
            "what_to_do_this_week": ana['churn']['what_to_do_this_week']
        },

        "best_marketing_channel": {
            "channel": ana['marketing']['recommended_channel'],
            "why": ana['marketing']['why']
        },

        "what_this_data_cannot_tell_us": [lim['area'] + ": " + lim['detail'] for lim in ana['limitations']],

        "monday_top_3": [a['summary'] for a in ana['monday_top_3']]
    }

    return answers


def export_answers_json(target_path=None):
    """Persists current answers to a local file when explicitly requested."""
    if target_path is None:
        db_override = os.environ.get("AXEOM_DB_PATH")
        if db_override and os.path.basename(db_override) != "axeom.db":
            target_path = f"{db_override}.answers.json"
        else:
            target_path = "answers_working.json"

    answers = build_answers_json()

    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(answers, f, indent=2)

    # Also keep submission/ directory synchronized if present
    if target_path == "answers_working.json" and os.path.isdir("submission"):
        with open("submission/answers_working.json", "w", encoding="utf-8") as sf:
            json.dump(answers, sf, indent=2)

    return answers
