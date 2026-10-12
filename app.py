"""
Axeom Studio Operations & Owner OS
Main Flask Application Server
"""

import os
from flask import Flask, render_template, jsonify, request
from services.db import init_db, seed_db_if_empty, get_current_revision, get_recent_uploads
from services.identity import CANONICAL_CLIENTS, THIRD_PARTY_PAYERS
from services.finance import reconcile_finances
from services.requests import get_requests_and_leads
from services.analytics import get_analytics
from services.decisions import get_all_decisions, save_decision
from services.history import get_client_history
from services.ingest import process_file_upload
from services.evidence import EVIDENCE_REGISTER, search_records
from services.export import export_answers_json, build_answers_json

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload

# Ensure database is initialized and seeded
if not os.environ.get("VERCEL"):
    init_db()
    seed_db_if_empty()
else:
    try:
        init_db()
    except Exception:
        pass

@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
    return response

@app.errorhandler(500)
def handle_internal_error(e):
    return jsonify({"status": "error", "message": "An internal server error occurred."}), 500

@app.errorhandler(404)
def handle_not_found(e):
    if request.path.startswith("/api/"):
        return jsonify({"status": "error", "message": "Endpoint not found."}), 404
    return render_template("index.html"), 404

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/favicon.ico")
def favicon():
    return "", 204

@app.route("/guide")
def guide_route():
    guide_path = os.path.join(os.path.dirname(__file__), "docs", "master-guide.html")
    with open(guide_path, "r", encoding="utf-8") as f:
        return f.read(), 200, {"Content-Type": "text/html; charset=utf-8"}

@app.route("/api/state")
def get_state():
    fin = reconcile_finances()
    req = get_requests_and_leads()
    ana = get_analytics()
    decisions = get_all_decisions()

    # Enrich canonical clients with financial stats
    enriched_clients = []
    for c in CANONICAL_CLIENTS:
        cf = fin['client_financials'].get(c['canonical_name'], {'invoiced': 0.0, 'paid': 0.0, 'overdue': 0.0, 'credit': 0.0})
        enriched_clients.append({
            **c,
            "financials": {
                "invoiced": round(cf['invoiced'], 2),
                "paid": round(cf['paid'], 2),
                "overdue": round(cf['overdue'], 2),
                "credit": round(cf['credit'], 2),
                "balance": round(cf['invoiced'] - cf['paid'], 2)
            }
        })

    # High-level business pulse metrics
    metrics = {
        "as_of_date": "2026-10-06",
        "client_count": len(CANONICAL_CLIENTS),
        "active_clients_count": len(CANONICAL_CLIENTS),
        "overdue_total": fin['overdue_total'],
        "overdue_count": len(fin['overdue']),
        "we_owe_total": fin['we_owe_total'],
        "we_owe_count": len(fin['we_owe']),
        "never_billed_total": fin['never_billed_total'],
        "never_billed_count": len(fin['never_billed']),
        "discrepancies_count": len(fin['discrepancies']),
        "lost_requests_count": req['lost_requests_count'],
        "unreplied_leads_count": req['unreplied_leads_count'],
        "total_leads_count": req['total_leads_count']
    }

    return jsonify({
        "status": "success",
        "metrics": metrics,
        "today": {
            "hero_action": ana['churn'],
            "monday_top_3": ana['monday_top_3']
        },
        "clients": enriched_clients,
        "third_party_payers": THIRD_PARTY_PAYERS,
        "money": {
            "overdue": fin['overdue'],
            "overdue_total": fin['overdue_total'],
            "we_owe": fin['we_owe'],
            "we_owe_total": fin['we_owe_total'],
            "never_billed": fin['never_billed'],
            "never_billed_total": fin['never_billed_total'],
            "discrepancies": fin['discrepancies']
        },
        "requests": {
            "lost_requests": req['lost_requests'],
            "root_causes": req['root_causes'],
            "deterioration": req['deterioration'],
            "unreplied_leads": req['unreplied_leads']
        },
        "analytics": {
            "marketing": ana['marketing'],
            "limitations": ana['limitations']
        },
        "evidence_register": EVIDENCE_REGISTER,
        "decisions": decisions,
        "revision": get_current_revision(),
        "recent_uploads": get_recent_uploads()
    })

@app.route("/api/decisions", methods=["POST"])
def post_decision():
    data = request.get_json(force=True)
    action_id = data.get("action_id")
    decision_type = data.get("decision_type", "action")
    status = data.get("status", "in_progress")
    notes = data.get("owner_notes", "")

    if not action_id:
        return jsonify({"status": "error", "message": "Missing action_id"}), 400

    decision = save_decision(action_id, decision_type, status, notes)
    return jsonify({"status": "success", "decision": decision})

@app.route("/api/client/<client_id>")
def client_history_route(client_id):
    history = get_client_history(client_id)
    if not history:
        return jsonify({"status": "error", "message": f"Client '{client_id}' not found"}), 404
    return jsonify({"status": "success", "data": history})

@app.route("/api/upload", methods=["POST"])
def upload_file_route():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file uploaded"}), 400

    file = request.files['file']
    if not file.filename:
        return jsonify({"status": "error", "message": "Empty filename"}), 400

    content_bytes = file.read()
    result = process_file_upload(file.filename, content_bytes)

    # Automatically recompute working answers export if successful and not in testing mode
    if result.get("status") == "success" and not app.config.get("TESTING"):
        try:
            export_answers_json()
        except Exception:
            pass

    status_code = 200 if result.get("status") in ["success", "duplicate_file"] else 400
    return jsonify(result), status_code

@app.route("/api/search")
def search_evidence_route():
    query = request.args.get("q", "")
    results = search_records(query)
    return jsonify({"status": "success", "query": query, "results": results})

@app.route("/api/export-answers")
def export_answers_route():
    # Serverless environments may not permit writes to the project directory.
    # Return the actual JSON attachment directly, rather than saving it on the server
    # and showing a success alert that does not download anything.
    response = jsonify(build_answers_json())
    response.headers["Content-Disposition"] = 'attachment; filename="answers.json"'
    response.headers["Cache-Control"] = "no-store"
    return response

@app.route("/api/classifications")
def get_classifications_route():
    from services.jev import get_message_classifications, get_classification_stats
    limit = int(request.args.get("limit", 100))
    stats = get_classification_stats()
    items = get_message_classifications(limit=limit)
    return jsonify({
        "status": "success",
        "stats": stats,
        "items": items
    })

@app.route("/api/reprocess-classifications", methods=["POST"])
def reprocess_classifications_route():
    from services.jev import reprocess_fallback_classifications
    data = request.get_json(silent=True) or {}
    limit = data.get("limit")
    result = reprocess_fallback_classifications(limit=limit)
    return jsonify(result)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
