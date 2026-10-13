"""
Axeom Studio Operations & Owner OS
Main Flask Application Server
"""

import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
from flask import Flask, render_template, jsonify, request, session, make_response
from services.db import init_db, seed_db_if_empty, get_current_revision, get_recent_uploads, is_dataset_cleared, close_request_db
from services.identity import get_canonical_clients, get_third_party_payers
from services.finance import reconcile_finances
from services.requests import get_requests_and_leads
from services.analytics import get_analytics
from services.decisions import get_all_decisions, save_decision
from services.history import get_client_history
from services.ingest import process_file_upload
from services.evidence import EVIDENCE_REGISTER, search_records
from services.export import export_answers_json, build_answers_json
from services.auth import is_owner_authorized, authorize_owner_session, clear_owner_session
from services.data_management import (
    get_records, get_record, update_record, archive_record, restore_record,
    soft_delete_record, calculate_impact, get_upload_history,
    calculate_upload_reversal_impact, revert_upload, get_reset_preview,
    execute_reset, get_audit_logs
)
from services.report_generator import generate_business_report, render_report_html

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "axeom-secret-production-key-2026")
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload

# Register request database cleanup
app.teardown_appcontext(close_request_db)

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
    cleared_workspace = is_dataset_cleared()
    fin = reconcile_finances()
    req = get_requests_and_leads()
    ana = get_analytics(fin=fin)
    decisions = get_all_decisions()

    # Dynamic client listing respecting active vs. archived state
    clients_list = get_canonical_clients(include_archived=True, include_deleted=False)
    active_clients = [c for c in clients_list if not c.get("is_archived")]

    # Enrich canonical clients with financial stats
    enriched_clients = []
    for c in clients_list:
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
        "client_count": len(clients_list),
        "active_clients_count": len(active_clients),
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
        "workspace_cleared": cleared_workspace,
        "metrics": metrics,
        "is_owner_authorized": is_owner_authorized(),
        "today": {
            "hero_action": ana['churn'],
            "monday_top_3": ana['monday_top_3']
        },
        "clients": enriched_clients,
        "third_party_payers": get_third_party_payers(),
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
        "evidence_register": [] if cleared_workspace else EVIDENCE_REGISTER,
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
    answers = build_answers_json()
    response = jsonify(answers)
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

# =====================================================================
# OWNER AUTHENTICATION & SESSION MANAGEMENT
# =====================================================================
@app.route("/api/auth/owner-status")
def owner_status_route():
    auth = is_owner_authorized()
    return jsonify({
        "status": "success",
        "is_authorized": auth,
        "is_owner_authorized": auth
    })

@app.route("/api/auth/owner-session", methods=["POST"])
def owner_session_route():
    data = request.get_json(silent=True) or {}
    pin = data.get("pin") or data.get("owner_pin") or request.form.get("pin")
    if authorize_owner_session(pin):
        return jsonify({"status": "success", "message": "Owner session authorized", "is_authorized": True, "is_owner_authorized": True})
    return jsonify({"status": "error", "message": "Invalid Owner PIN/Passcode", "is_authorized": False, "is_owner_authorized": False}), 401

@app.route("/api/auth/owner-logout", methods=["POST"])
def owner_logout_route():
    clear_owner_session()
    return jsonify({"status": "success", "message": "Owner session cleared", "is_authorized": False, "is_owner_authorized": False})

# =====================================================================
# DATA MANAGEMENT: RECORDS CRUD, ARCHIVE, RESTORE, SOFT-DELETE
# =====================================================================
@app.route("/api/manage/records")
def manage_records_route():
    table = request.args.get("table", "clients")
    filter_status = request.args.get("status", "all")
    search = request.args.get("search", "")
    limit = int(request.args.get("limit", 50))
    offset = int(request.args.get("offset", 0))

    try:
        res = get_records(table, filter_status=filter_status, search=search, limit=limit, offset=offset)
        return jsonify({"status": "success", **res})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route("/api/manage/records/<table_name>/<record_id>", methods=["GET", "PUT", "DELETE"])
def manage_single_record_route(table_name, record_id):
    if request.method == "GET":
        rec = get_record(table_name, record_id)
        if not rec:
            return jsonify({"status": "error", "message": "Record not found"}), 404
        return jsonify({"status": "success", "record": rec})

    elif request.method == "PUT":
        data = request.get_json(force=True) or {}
        res = update_record(table_name, record_id, data)
        if res.get("status") == "error":
            return jsonify(res), 400
        return jsonify(res)

    elif request.method == "DELETE":
        if not is_owner_authorized():
            return jsonify({
                "status": "error",
                "message": "Owner authorization required to delete records. Please enter your Owner PIN."
            }), 403
        res = soft_delete_record(table_name, record_id)
        return jsonify(res)

@app.route("/api/manage/records/<table_name>/<record_id>/archive", methods=["POST"])
def manage_archive_record_route(table_name, record_id):
    res = archive_record(table_name, record_id)
    return jsonify(res)

@app.route("/api/manage/records/<table_name>/<record_id>/restore", methods=["POST"])
def manage_restore_record_route(table_name, record_id):
    res = restore_record(table_name, record_id)
    return jsonify(res)

@app.route("/api/manage/records/<table_name>/<record_id>/impact")
def manage_record_impact_route(table_name, record_id):
    res = calculate_impact(table_name, record_id)
    return jsonify(res)

# =====================================================================
# DATA MANAGEMENT: UPLOADS & REVERSAL
# =====================================================================
@app.route("/api/manage/uploads")
def manage_uploads_route():
    uploads = get_upload_history()
    return jsonify({"status": "success", "uploads": uploads})

@app.route("/api/manage/uploads/<int:upload_id>/impact")
def manage_upload_impact_route(upload_id):
    impact = calculate_upload_reversal_impact(upload_id)
    return jsonify(impact)

@app.route("/api/manage/uploads/<int:upload_id>/revert", methods=["POST"])
def manage_upload_revert_route(upload_id):
    if not is_owner_authorized():
        return jsonify({
            "status": "error",
            "message": "Owner authorization required to reverse an upload dataset. Please enter your Owner PIN."
        }), 403
    res = revert_upload(upload_id)
    if res.get("status") == "error":
        return jsonify(res), 400
    return jsonify(res)

# =====================================================================
# DATA MANAGEMENT: DATASET RESET & AUDIT LOGS
# =====================================================================
@app.route("/api/manage/reset/preview")
def manage_reset_preview_route():
    preview = get_reset_preview()
    return jsonify({"status": "success", "preview": preview})

@app.route("/api/manage/reset", methods=["POST"])
def manage_reset_route():
    if not is_owner_authorized():
        return jsonify({
            "status": "error",
            "message": "Owner authorization required to reset business dataset. Please enter your Owner PIN."
        }), 403

    data = request.get_json(silent=True) or {}
    phrase = data.get("confirmation_phrase") or data.get("phrase", "")
    res = execute_reset(phrase, expected_total_records=data.get("expected_total_records"))
    if res.get("status") == "error":
        # 409 = valid request rejected because verified restore capability is absent.
        code = 400 if "Invalid confirmation phrase" in res.get("message", "") else 409
        return jsonify(res), code
    return jsonify(res)

@app.route("/api/manage/audit-logs")
def manage_audit_logs_route():
    limit = int(request.args.get("limit", 100))
    logs = get_audit_logs(limit)
    return jsonify({"status": "success", "audit_logs": logs, "logs": logs})

# =====================================================================
# OWNER REPORTS: MODE B DYNAMIC BUSINESS REPORT
# =====================================================================
@app.route("/api/reports/business-report")
def business_report_json_route():
    report = generate_business_report()
    fmt = request.args.get("format", "json").lower()
    if fmt == "html":
        html_content = render_report_html(report)
        return html_content, 200, {"Content-Type": "text/html; charset=utf-8"}
    return jsonify(report)

@app.route("/api/reports/business-report.json")
def business_report_download_route():
    report = generate_business_report()
    resp = make_response(jsonify(report))
    resp.headers["Content-Disposition"] = "attachment; filename=axeom_business_report.json"
    return resp

@app.route("/api/reports/business-report.html")
def business_report_html_route():
    report = generate_business_report()
    html_content = render_report_html(report)
    return html_content, 200, {"Content-Type": "text/html; charset=utf-8"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
