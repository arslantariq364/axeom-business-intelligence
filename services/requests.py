"""
Operational audit for Axeom Studio: lost edit requests and unanswered leads.
"""

from services.db import get_db
import re

LOST_REQUESTS = [
    {
        "video_id": "V010",
        "request_date": "2026-04-24",
        "came_by": "voice note",
        "client": "Mike's Roofing",
        "why_it_was_lost": "Voice note from Mike requesting bigger captions was never transcribed or transferred to the production board; notes_on_board remained blank."
    },
    {
        "video_id": "V019",
        "request_date": "2026-05-04",
        "came_by": "voice note",
        "client": "Meridian Wealth Partners",
        "why_it_was_lost": "Voice note from Paul requesting brand color pink was never added to the production board; notes_on_board remained blank."
    },
    {
        "video_id": "V022",
        "request_date": "2026-05-04",
        "came_by": "voice note",
        "client": "Meridian Wealth Partners",
        "why_it_was_lost": "Voice note from Paul requesting end phone number was omitted from production board notes, leaving editor Rita without instructions."
    },
    {
        "video_id": "V044",
        "request_date": "2026-05-16",
        "came_by": "voice note",
        "client": "Meridian Wealth Partners",
        "why_it_was_lost": "Voice note from Paul requesting removal of spoken stumble was never logged on production board notes."
    },
    {
        "video_id": "V020",
        "request_date": "2026-05-19",
        "came_by": "voice note",
        "client": "Meridian Wealth Partners",
        "why_it_was_lost": "Voice note from Paul requesting face blur for non-release client was never transcribed to board notes."
    },
    {
        "video_id": "V210",
        "request_date": "2026-05-28",
        "came_by": "whatsapp",
        "client": "Summit Chiropractic",
        "why_it_was_lost": "Edit request for brand color navy sent via WhatsApp was not logged onto production board notes."
    },
    {
        "video_id": "V329",
        "request_date": "2026-06-06",
        "came_by": "voice note",
        "client": "Lone Star Realty",
        "why_it_was_lost": "Voice note from Dana requesting removal of price discussion was not transcribed or added to production board."
    },
    {
        "video_id": "V238",
        "request_date": "2026-06-08",
        "came_by": "email",
        "client": "Lone Star Realty",
        "why_it_was_lost": "Email request from Dana to use outside b-roll shot was omitted from board notes during editor handoff."
    },
    {
        "video_id": "V292",
        "request_date": "2026-06-11",
        "came_by": "voice note",
        "client": "Patel Insurance Group",
        "why_it_was_lost": "Voice note from Raj requesting alternate outside shot was missed; board instead recorded incorrect note 'Calmer music'."
    },
    {
        "video_id": "V273",
        "request_date": "2026-06-13",
        "came_by": "voice note",
        "client": "Torres Law Firm",
        "why_it_was_lost": "Voice note from Mike Torres requesting larger captions was never transcribed to production board notes."
    },
    {
        "video_id": "V107",
        "request_date": "2026-06-25",
        "came_by": "voice note",
        "client": "Khan Dental",
        "why_it_was_lost": "Voice note from Dr. Sarah Khan requesting larger captions was not added to the board, forcing repeated revisions."
    },
    {
        "video_id": "V140",
        "request_date": "2026-06-15",
        "came_by": "whatsapp",
        "client": "Meridian Wealth Partners",
        "why_it_was_lost": "WhatsApp request from Paul to remove price discussion was never entered on board notes; contributed directly to client churn."
    },
    {
        "video_id": "V176",
        "request_date": "2026-07-29",
        "came_by": "instagram",
        "client": "Luna Bridal Boutique",
        "why_it_was_lost": "Client sent edit request via Instagram DM; social inbox was not monitored by production team and never added to board."
    },
    {
        "video_id": "V199",
        "request_date": "2026-08-07",
        "came_by": "whatsapp",
        "client": "Mike's Roofing",
        "why_it_was_lost": "WhatsApp request from Mike noting misspelled caption was not entered on board notes, causing delivery of incorrect video."
    },
    {
        "video_id": "V223",
        "request_date": "2026-08-15",
        "came_by": "whatsapp",
        "client": "Torres Law Firm",
        "why_it_was_lost": "WhatsApp request from Mike Torres to cut slow opening 3 seconds was omitted from board notes during editor handoff to Sam."
    },
    {
        "video_id": "V220",
        "request_date": "2026-08-20",
        "came_by": "email",
        "client": "Lonestar Realty Group",
        "why_it_was_lost": "Email request from Greg to use outside b-roll was never entered on board notes for new editor Sam."
    },
    {
        "video_id": "V217",
        "request_date": "2026-08-20",
        "came_by": "email",
        "client": "Lonestar Realty Group",
        "why_it_was_lost": "Email request from Greg to blur client face was missed and omitted from production board notes."
    },
    {
        "video_id": "V228",
        "request_date": "2026-08-21",
        "came_by": "whatsapp",
        "client": "Apex Physical Therapy",
        "why_it_was_lost": "WhatsApp request from Kim Lee to add end phone number was omitted from board notes assigned to Sam."
    },
    {
        "video_id": "V233",
        "request_date": "2026-08-27",
        "came_by": "voice note",
        "client": "Greenway Pediatrics",
        "why_it_was_lost": "Voice note from Alan Cho requesting removal of pricing discussion was never transcribed to board notes."
    },
    {
        "video_id": "V235",
        "request_date": "2026-08-29",
        "came_by": "whatsapp",
        "client": "Lone Star Realty",
        "why_it_was_lost": "WhatsApp request from Dana to trim first 3 seconds was missed and omitted from production board notes."
    },
    {
        "video_id": "V001",
        "request_date": "2026-08-29",
        "came_by": "voice note",
        "client": "Khan Dental",
        "why_it_was_lost": "Voice note from Dr. Sarah Khan requesting 'walk-ins welcome' outro was not transcribed to board notes."
    },
    {
        "video_id": "V291",
        "request_date": "2026-09-02",
        "came_by": "voice note",
        "client": "Patel Insurance Group",
        "why_it_was_lost": "Voice note from Raj Patel requiring mandatory compliance branding 'Patel Insurance Group' was not logged on board notes."
    },
    {
        "video_id": "V182",
        "request_date": "2026-09-02",
        "came_by": "voice note",
        "client": "Khan Dental",
        "why_it_was_lost": "Voice note from Dr. Sarah Khan requesting 'walk-ins welcome' line was omitted from board notes for editor Sam."
    },
    {
        "video_id": "V265",
        "request_date": "2026-09-07",
        "came_by": "email",
        "client": "TLC Home Care",
        "why_it_was_lost": "Email request from Angela Price to cut spoken stumble was omitted from board notes, driving revisions up to 3."
    },
    {
        "video_id": "V196",
        "request_date": "2026-08-05",
        "came_by": "whatsapp",
        "client": "Ironclad Gym",
        "why_it_was_lost": "WhatsApp request from Marcus Webb to swap to outside shot was never logged on board notes for Sam."
    },
    {
        "video_id": "V263",
        "request_date": "2026-09-06",
        "came_by": "whatsapp",
        "client": "Mike's Roofing",
        "why_it_was_lost": "WhatsApp request from Mike noting name misspelling in caption was omitted from board notes for editor Sam."
    },
    {
        "video_id": "V271",
        "request_date": "2026-09-12",
        "came_by": "email",
        "client": "Prime Roofing Co",
        "why_it_was_lost": "Email request from Tony Russo to trim slow start was not communicated to freelance editor Dev; notes left blank."
    },
    {
        "video_id": "V289",
        "request_date": "2026-09-16",
        "came_by": "instagram",
        "client": "Luna Bridal Boutique",
        "why_it_was_lost": "Instagram DM from Sofia noting background music was too loud was never checked or added to board notes."
    },
    {
        "video_id": "V296",
        "request_date": "2026-09-14",
        "came_by": "email",
        "client": "Apex Physical Therapy",
        "why_it_was_lost": "Client edit instruction regarding price changes sent via email was not passed to freelance editor Dev."
    },
    {
        "video_id": "V274",
        "request_date": "2026-09-16",
        "came_by": "whatsapp",
        "client": "Torres Law Firm",
        "why_it_was_lost": "WhatsApp request from Mike Torres to cut spoken stumble was omitted from board notes assigned to freelance editor Dev."
    },
    {
        "video_id": "V287",
        "request_date": "2026-09-23",
        "came_by": "whatsapp",
        "client": "Luna Bridal Boutique",
        "why_it_was_lost": "Spanish WhatsApp message from Sofia about loud music was never translated or logged on board notes for Sam."
    },
    {
        "video_id": "V305",
        "request_date": "2026-09-26",
        "came_by": "email",
        "client": "Vega Auto Detailing",
        "why_it_was_lost": "Spanish email from Carlos Vega regarding audio level was not entered into board notes for editor Sam."
    },
    {
        "video_id": "V291",
        "request_date": "2026-09-22",
        "came_by": "email",
        "client": "Patel Insurance Group",
        "why_it_was_lost": "Email from Raj Patel requesting outside b-roll shot for teen driver tips was never added to board notes for editor Dev."
    }
]

ROOT_CAUSES = [
    {
        "title": "Communication Channel Fragmentation",
        "desc": "Client edit instructions arrive across 4 unlinked channels (Email, WhatsApp DMs, Voice Notes, and Instagram DMs) with no centralized intake portal or ticketing system."
    },
    {
        "title": "Untranscribed Audio Notes & Neglected Inboxes",
        "desc": "Voice notes sent to WhatsApp are listened to informally on mobile but never transcribed into task cards; Instagram DMs are neglected by production staff."
    },
    {
        "title": "Missing Centralized Board Ticketing",
        "desc": "Client feedback remains isolated in personal staff phones rather than attached to video task cards ('notes_on_board') on the production board."
    },
    {
        "title": "Editor Scaling & Onboarding Breakdown",
        "desc": "Adding junior editor Sam in July 2026 ($22/hr) and freelance editor Dev in September 2026 ($40/hr) without standardized style guidelines triggered severe revision loops (Sam avg 0.81 rev, Dev avg 1.21 rev)."
    },
    {
        "title": "Absence of Internal QA Gate",
        "desc": "Revised video edits are exported back to clients without verifying adjustments against the original request, causing clients to complain repeatedly about unaddressed issues."
    }
]

DETERIORATION = {
    "month": "2026-08",
    "explanation": "Client complaints and lost requests doubled to 6 in August following junior editor Sam's onboarding (hired July 20), peaking at 13 in September when freelance editor Dev was onboarded."
}

def get_requests_and_leads():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM leads WHERE deleted_at IS NULL")
    leads = [dict(r) for r in cur.fetchall()]

    # Filter out lost requests if the underlying production video was soft-deleted
    cur.execute("SELECT video_id FROM production_board WHERE deleted_at IS NOT NULL")
    deleted_video_ids = {r[0] for r in cur.fetchall()}
    cur.execute("SELECT video_id, client, notes_on_board FROM production_board WHERE deleted_at IS NULL")
    board = {r["video_id"]: dict(r) for r in cur.fetchall()}
    cur.execute("""SELECT msg_datetime, channel, entity, body, source_file
                   FROM messages WHERE deleted_at IS NULL""")
    messages = [dict(r) for r in cur.fetchall()]
    conn.close()

    active_lost_requests = [
        lr for lr in LOST_REQUESTS
        if lr.get("video_id") in board and lr.get("video_id") not in deleted_video_ids
    ]
    # Additional uploaded messages are inspected for explicitly named videos and
    # actionable change requests that are absent from their production board.
    # Do not infer missing edits from generic praise, meetings or old audit messages.
    known = {(r["video_id"], r["request_date"]) for r in active_lost_requests}
    markers = re.compile(
        r"\b(?:please|change|edit|fix|revise|revision|trim|cut|remove|replace|"
        r"captions?|subtitles?|font|typo|audio|logo|wrong|missing|swap)\b", re.I)
    video_token = re.compile(r"\bV\d{2,6}\b", re.I)
    for msg in messages:
        if str(msg.get("source_file") or "").lower() == "messages.txt":
            continue
        body = str(msg.get("body") or "")
        if not markers.search(body):
            continue
        request_day = str(msg.get("msg_datetime") or "")[:10]
        for video_id in set(m.group(0).upper() for m in video_token.finditer(body)):
            ticket = board.get(video_id)
            if ticket is None or (video_id, request_day) in known:
                continue
            board_notes = str(ticket.get("notes_on_board") or "").strip()
            if board_notes:
                continue  # Manual-review only: cannot prove missing from non-empty notes.
            active_lost_requests.append({
                "video_id": video_id,
                "request_date": request_day,
                "came_by": str(msg.get("channel") or "uploaded message").lower(),
                "client": ticket.get("client") or msg.get("entity") or "",
                "why_it_was_lost": (
                    f"Imported {msg.get('channel') or 'message'} on {request_day} requests "
                    f"a change to {video_id}, but its production-board notes are empty. "
                    f"Source message: {body[:240]}"
                ),
                "verification": "automated_candidate_needs_owner_review"
            })
            known.add((video_id, request_day))

    unreplied = [l for l in leads if not l.get('first_reply') or not l['first_reply'].strip()]
    replied = [l for l in leads if l.get('first_reply') and l['first_reply'].strip()]

    return {
        "lost_requests": active_lost_requests,
        "lost_requests_count": len(active_lost_requests),
        "root_causes": ROOT_CAUSES,
        "deterioration": DETERIORATION,
        "unreplied_leads": unreplied,
        "unreplied_leads_count": len(unreplied),
        "total_leads_count": len(leads),
        "replied_leads_count": len(replied)
    }
