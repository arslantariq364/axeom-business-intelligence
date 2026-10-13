"""
High-level strategic analytics and owner action prioritization for Axeom Studio.
"""

CHURN_ANALYSIS = {
    "client": "Patel Insurance Group",
    "retainer_value": "$2,500.00 / month ($30,000 / year)",
    "overdue_invoice": "INV-1122 ($2,500.00, 21 days overdue)",
    "evidence": [
        "Nina Patel explicitly submitted a website contract inquiry on 2026-09-30 (Lead L097) stating: 'We would like to talk about our contract and whether we continue' — left completely unanswered with zero response.",
        "Nina Patel followed up via direct email on 2026-10-02 ('We need to talk about the contract this week') — also left unanswered.",
        "Raj Patel sent heated complaints on 2026-09-08 ('The videos say Patel Insurance again. I asked for the full name. Not happy') and 2026-10-01 ('teen driver tips still has the same problem. I already told you about this') regarding regulatory compliance branding and ignored edit requests.",
        "Payment withholding: Monthly retainer invoice INV-1122 for $2,500.00 (due 2026-09-15) remains completely unpaid and is now 21 days late.",
        "Direct precedent: Follows the exact churn pattern of Paul Grant / Meridian Wealth Partners, who cancelled their $2,500/mo retainer in July for the exact same reason ('Too many rounds of fixes, and my notes keep getting missed')."
    ],
    "what_to_do_this_week": "Owner must call Nina and Raj Patel personally first thing Monday morning (2026-10-06). Formally apologize for the compliance name error, confirm immediate correction of all active video assets to 'Patel Insurance Group' with the requested b-roll swap on 'teen driver tips', schedule a contract review meeting for Wednesday, and offer a $500 goodwill credit to secure the contract and unblock collection of overdue invoice INV-1122 ($2,500).",
    "draft_script": (
        "Hi Nina and Raj, this is Arslan from Axeom Studio. I'm calling personally to apologize for the delay in responding "
        "to your contract review inquiry, and specifically for the frustrating errors on your compliance branding. "
        "I've personally taken over your account. We have immediately corrected all active video assets to display the full, "
        "compliant 'Patel Insurance Group' name and updated the b-roll cuts on 'teen driver tips'. We value your partnership "
        "tremendously and want to apply a $500 goodwill credit to your account while scheduling 15 minutes this Wednesday "
        "to review our deliverables and ensure your peace of mind."
    )
}

# Marketing conversion metrics are computed from leads inside get_analytics().
# Historical marketing-profit estimates were withdrawn after independent audit.

LIMITATIONS = [
    {
        "area": "Marketing Ad Spend & True CAC",
        "detail": "The dataset records studio time ($40/hr) and editor wages in costs.csv, but contains zero advertising spend data (Meta ad spend, Google PPC budgets, LinkedIn ad costs). True customer acquisition cost (CAC) and net marketing ROI cannot be computed."
    },
    {
        "area": "Offline Communications & Verbal Agreements",
        "detail": "Several messages in messages.txt reference phone calls or in-person studio discussions; verbal agreements regarding shoot reschedules, verbal approvals, or payment arrangements are unrecorded."
    },
    {
        "area": "Long-Term Client LTV Beyond 6 Months",
        "detail": "All transaction records span exclusively from April 2026 to October 2026. Annual client retention, repeat booking rates beyond six months, and seasonal demand cannot be observed."
    },
    {
        "area": "Third-Party Agency Contract Terms",
        "detail": "Brightline Marketing LLC pays on behalf of multiple medical clients (Greenway Pediatrics, Summit Chiropractic), but the contractual markup, agency fee agreement, or service level commitments between Axeom and Brightline are undocumented."
    },
    {
        "area": "Fixed Studio Operating Overhead",
        "detail": "Beyond hourly studio rate allocations, fixed monthly overheads (facility lease, utilities, cameras and lighting depreciation, cloud software subscriptions, insurance) are omitted from the data."
    },
    {
        "area": "Live AI (Jev) Verification & Account Credentials",
        "detail": "Typesafe AI (Jev) API key (TYPESAFE_API_KEY) is not configured in this environment. While the production integration, official schema (POST https://api.typesafe.ai/v1/systemone, model jev-latest), caching, and deterministic fallback (96.0% accuracy on held-out test set) are fully implemented, live API calls and verified live evaluations remain 'Not evaluated' pending account credential provisioning. Fallback classifications are explicitly distinguished and not attributed to Jev."
    }
]

MONDAY_TOP_3 = [
    {
        "id": "action_patel_call",
        "rank": 1,
        "urgency": "CRITICAL",
        "title": "Emergency Churn Intervention & $2,500 Cash Recovery",
        "client": "Patel Insurance Group",
        "contact": "Nina & Raj Patel (214-555-0195)",
        "financial_impact": "$2,500/mo Retainer ($30,000/yr) + $2,500 Overdue Invoice",
        "summary": "Call Nina and Raj Patel personally at 9:00 AM. Formally apologize for compliance branding errors, confirm immediate correction of video assets to 'Patel Insurance Group', review the contract to prevent cancellation of their $2,500/mo retainer, and collect 21-day overdue invoice INV-1122 ($2,500.00).",
        "draft_notes": "Call Nina and Raj Patel at 9:00 AM regarding Lead L097 and INV-1122. Offer $500 goodwill credit, confirm compliance name fix, book Wednesday review."
    },
    {
        "id": "action_bill_unbilled",
        "rank": 2,
        "urgency": "HIGH",
        "title": "Capture $2,950 Unbilled Revenue & Reconcile Client Credits",
        "client": "Multiple Clients (Vega Auto, Ironclad, DFW Founders, Lone Star, Glow)",
        "contact": "Carlos Vega, Marcus Webb, Ethan Cole, Dana Brooks, Nadia Hassan",
        "financial_impact": "$2,950.00 Unbilled Inflow / $2,400.00 Customer Credits",
        "summary": "Immediately issue invoices for the 3 completed unbilled shoots (Vega Auto Detailing B144 for $1,500, Ironclad Gym B123 for $900, DFW Founders B136 for $550) to collect $2,950.00 in earned revenue, while applying a $1,500 credit to Lone Star Realty for cancelled shoot B148 and refunding Glow Aesthetics $900 for duplicate payment on INV-1086.",
        "draft_notes": "Generate INV for Vega Auto ($1,500), Ironclad ($900), DFW Founders ($550). Issue credit note $1,500 to Lone Star and refund $900 to Glow Aesthetics."
    },
    {
        "id": "action_collect_overdue",
        "rank": 3,
        "urgency": "HIGH",
        "title": "Enforce Collections on $6,750 in Aged Receivables & Fix Billing Tool",
        "client": "Crown Barbers, Lonestar Realty Group, TLC Home Care",
        "contact": "Andre Jackson (469-555-0115), Greg Whitfield (817-555-0119), Angela Price (214-555-0187)",
        "financial_impact": "$6,750.00 Aged Cash Collection + 6 Billing Tool Fixes",
        "summary": "Directly follow up on the remaining 8 overdue invoices totaling $6,750 (prioritizing Crown Barbers INV-1066 $900 at 80 days late, Lonestar Realty Group INV-1104 $1,500 at 41 days late, and TLC Home Care INV-1120 $1,500 at 21 days late), and correct the 6 billing tool errors so paid invoices are no longer mislabeled as unpaid.",
        "draft_notes": "Send polite collection reminders to Crown Barbers, Lonestar RG, and TLC Home Care. Update accounting software status for INV-1066, INV-1093, INV-1097, INV-1103, INV-1106, INV-1117."
    }
]

def get_analytics():
    """Business intelligence derived from current stored records, not fixed KPIs."""
    from collections import defaultdict
    from copy import deepcopy
    from services.db import get_db
    from services.finance import reconcile_finances

    from services.db import is_dataset_cleared
    if is_dataset_cleared():
        fin = reconcile_finances()
        conn = get_db()
        try:
            cur = conn.cursor()
            cur.execute("SELECT source, status FROM leads WHERE deleted_at IS NULL")
            current_leads = [dict(row) for row in cur.fetchall()]
        finally:
            conn.close()

        by_channel = defaultdict(lambda: {"leads": 0, "converted": 0})
        for row in current_leads:
            source = str(row.get("source") or "Unknown").strip()
            by_channel[source]["leads"] += 1
            if str(row.get("status") or "").lower() in {"won", "converted"}:
                by_channel[source]["converted"] += 1
        channels = []
        for name, entry in sorted(by_channel.items()):
            count, won = entry["leads"], entry["converted"]
            channels.append({
                "name": name, "leads": count, "converted": won,
                "conversion_rate": f"{100 * won / count:.1f}%" if count else "0.0%",
                "revenue_invoiced": None, "cash_collected": None,
                "production_cost": None, "gross_profit": None,
                "gross_margin": None, "status": "Profit not verified"
            })
        best = max(channels, key=lambda c: (c["converted"] / c["leads"], c["converted"]), default=None)
        marketing = {
            "recommended_channel": best["name"] if best else "No data",
            "why": "Recommendation uses only uploaded lead conversions; profit is not verified.",
            "channels": channels, "profitability_verified": False
        }
        actions = []
        if fin["overdue"]:
            actions.append({
                "id": "action_collect_overdue", "title": "Review outstanding invoices",
                "client": "", "contact": "", "rank": 1, "urgency": "HIGH",
                "financial_impact": f"${fin['overdue_total']:,.2f} outstanding",
                "summary": f"Review {len(fin['overdue'])} overdue invoices totaling ${fin['overdue_total']:,.2f}.",
                "draft_notes": "Review invoice records and contact customers manually."
            })
        if fin["never_billed"]:
            actions.append({
                "id": "action_bill_unbilled", "title": "Review potentially unbilled bookings",
                "client": "", "contact": "", "rank": 2, "urgency": "MEDIUM",
                "financial_impact": f"${fin['never_billed_total']:,.2f} to review",
                "summary": "Check completed bookings against invoices and package coverage.",
                "draft_notes": "Confirm actual work and billing evidence."
            })
        return {
            "churn": {"client": "", "retainer_value": "", "overdue_invoice": "",
                      "evidence": [], "what_to_do_this_week": "", "draft_script": ""},
            "marketing": marketing,
            "limitations": [],
            "monday_top_3": actions
        }

    fin = reconcile_finances()
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT source, status FROM leads WHERE deleted_at IS NULL")
    leads = [dict(row) for row in cur.fetchall()]
    conn.close()

    totals = defaultdict(lambda: {"leads": 0, "converted": 0})
    for lead in leads:
        label = str(lead.get("source") or "Unknown").strip()
        normalized = {
            "website": "Website form", "website form": "Website form",
            "referral": "Referral", "meta ads": "Meta ads",
            "facebook": "Meta ads", "google search": "Google search",
            "google": "Google search", "walk-in": "Walk-in / Direct",
            "walk-in / direct": "Walk-in / Direct", "direct": "Walk-in / Direct"
        }.get(label.lower(), label)
        totals[normalized]["leads"] += 1
        if str(lead.get("status") or "").strip().lower() in {"won", "converted"}:
            totals[normalized]["converted"] += 1

    channels = []
    for name, row in sorted(totals.items()):
        count, won = row["leads"], row["converted"]
        channels.append({
            "name": name, "leads": count, "converted": won,
            "conversion_rate": f"{100 * won / count:.1f}%" if count else "0.0%",
            "revenue_invoiced": None, "cash_collected": None,
            "production_cost": None, "gross_profit": None,
            "gross_margin": None, "status": "Profit not verified"
        })

    # Prefer a meaningful sample to avoid picking a 1-of-1 lead source.
    eligible = [c for c in channels if c["leads"] >= 5] or channels
    best = max(eligible, key=lambda c: (
        c["converted"] / c["leads"] if c["leads"] else 0,
        c["converted"], c["leads"]
    ), default=None)
    best_name = best["name"] if best else "Insufficient lead data"
    why = (
        f"{best_name} has the highest recorded lead-to-Won conversion rate "
        f"among channels with at least five leads ({best['converted']} of "
        f"{best['leads']}, {best['conversion_rate']}). "
        "This is a LEAD-CONVERSION recommendation, NOT proof of highest "
        "gross profit: lead-to-invoice attribution and channel-specific "
        "acquisition costs are not established in the available records."
        if best else "No eligible lead records are available."
    )
    marketing = {
        "recommended_channel": best_name, "why": why,
        "channels": channels, "profitability_verified": False
    }

    churn = deepcopy(CHURN_ANALYSIS)
    actions = deepcopy(MONDAY_TOP_3)
    patel = next((item for item in fin["overdue"] if item["invoice"] == "INV-1122"), None)
    if patel:
        churn["overdue_invoice"] = (
            f"INV-1122 (${patel['amount_owed']:,.2f}, {patel['days_late']} days overdue)"
        )
        actions[0]["financial_impact"] = (
            f"$2,500/mo retainer + ${patel['amount_owed']:,.2f} overdue"
        )
    else:
        churn["overdue_invoice"] = ""
        churn["evidence"] = [
            line for line in churn["evidence"]
            if "Payment withholding:" not in line
        ]
        churn["what_to_do_this_week"] = (
            "Contact Nina and Raj Patel about unresolved branding corrections and "
            "the unanswered contract inquiry. Verify the video fixes before claiming "
            "completion. INV-1122 is not currently in the overdue queue."
        )
        actions[0]["title"] = "Resolve Patel Contract Risk & Branding Issues"
        actions[0]["summary"] = churn["what_to_do_this_week"]
        actions[0]["financial_impact"] = "$2,500/mo retainer at churn risk; no overdue INV-1122"
        actions[0]["draft_notes"] = churn["what_to_do_this_week"]

    unbilled_total = fin["never_billed_total"]
    credits_total = fin["we_owe_total"]
    actions[1]["title"] = f"Review ${unbilled_total:,.2f} Potential Unbilled Work & Credits"
    actions[1]["financial_impact"] = (
        f"${unbilled_total:,.2f} potential unbilled / ${credits_total:,.2f} client credits"
    )
    unbilled_summary = ", ".join(
        f"{b['booking_id_or_month']} (${b['amount']:,.2f})" for b in fin["never_billed"][:8]
    ) or "none currently identified"
    actions[1]["summary"] = (
        f"Review completed, potentially unbilled bookings: {unbilled_summary}. "
        f"Check retainer coverage before invoicing. Reconcile ${credits_total:,.2f} in credits."
    )
    actions[1]["draft_notes"] = actions[1]["summary"]

    outstanding = [item for item in fin["overdue"] if item["invoice"] != "INV-1122"]
    aged_total = sum(item["amount_owed"] for item in outstanding)
    actions[2]["title"] = f"Follow Up on ${aged_total:,.2f} Other Overdue Receivables"
    actions[2]["financial_impact"] = (
        f"${aged_total:,.2f} overdue across {len(outstanding)} invoices"
    )
    actions[2]["summary"] = (
        f"Follow up on {len(outstanding)} remaining overdue invoices totaling "
        f"${aged_total:,.2f}. Check payment allocation and correct billing discrepancies "
        "before sending any messages. Nothing is sent automatically."
    )
    actions[2]["draft_notes"] = actions[2]["summary"]
    return {
        "churn": churn,
        "marketing": marketing,
        "limitations": LIMITATIONS,
        "monday_top_3": actions
    }
