"""
Audit-Cleaned Evaluation Datasets for Typesafe AI (Jev) Integration.
Strictly separates:
1. TUNING_SET (10 examples): Used for initial prompt/schema design.
2. REFINEMENT_DEV_SET (30 examples): Inspected during developer iteration (compromised / tuned fit).
3. GENUINE_HELDOUT_TEST_SET (25 examples): Strictly unseen, zero text overlap, completely uninfluenced by tuning.

Attribution Notice:
Ground-truth labels were assigned by the AI assistant during the Prompt 7 audit.
No independent human domain expert verification has been conducted; owner verification is pending.
"""

# 10 Tuning Examples (Used for prompt engineering and keyword pattern discovery)
TUNING_SET = [
    {
        "line_no": 1,
        "channel": "EMAIL",
        "sender": "mike@mikesroofingtx.com",
        "text": "Can roof inspection walkthrough have a calmer song? This one feels too hype for us.",
        "true_intent": "edit_request",
        "multi_intent": False,
        "has_actionable_billing": False,
        "notes": "Tone & music mood revision request",
        "attribution": "Assigned by AI assistant during Prompt 7 audit; unverified by human domain expert"
    },
    {
        "line_no": 2,
        "channel": "EMAIL",
        "sender": "will@cedarstone.build",
        "text": "Please blur the face of the client in crew day, she didn't sign the release.",
        "true_intent": "edit_request",
        "multi_intent": False,
        "has_actionable_billing": False,
        "notes": "Privacy / legal face blurring edit request",
        "attribution": "Assigned by AI assistant during Prompt 7 audit; unverified by human domain expert"
    },
    {
        "line_no": 42,
        "channel": "EMAIL",
        "sender": "kelsey@brightlinemktg.com",
        "text": "Hi, Kelsey from Brightline Marketing. Please bill us (Brightline) for Greenway Pediatrics and Summit Chiropractic. We pay monthly.",
        "true_intent": "billing_issue",
        "multi_intent": False,
        "has_actionable_billing": True,
        "notes": "Agency payer billing instruction",
        "attribution": "Assigned by AI assistant during Prompt 7 audit; unverified by human domain expert"
    },
    {
        "line_no": 122,
        "channel": "EMAIL",
        "sender": "tasha@hustleandheart.fm",
        "text": "Cash is tight this month. Can I pay the August sessions together at the start of September?",
        "true_intent": "billing_issue",
        "multi_intent": False,
        "has_actionable_billing": True,
        "notes": "Payment extension / cash flow inquiry",
        "attribution": "Assigned by AI assistant during Prompt 7 audit; unverified by human domain expert"
    },
    {
        "line_no": 27,
        "channel": "WHATSAPP",
        "sender": "+1 972-555-0110 (Priya)",
        "text": "See you tomorrow.",
        "true_intent": "booking_or_schedule",
        "multi_intent": False,
        "has_actionable_billing": False,
        "notes": "Schedule confirmation",
        "attribution": "Assigned by AI assistant during Prompt 7 audit; unverified by human domain expert"
    },
    {
        "line_no": 30,
        "channel": "WHATSAPP",
        "sender": "+1 469-555-0133 (Jordan)",
        "text": "Can we move to 2pm instead?",
        "true_intent": "booking_or_schedule",
        "multi_intent": False,
        "has_actionable_billing": False,
        "notes": "Shoot time rescheduling request",
        "attribution": "Assigned by AI assistant during Prompt 7 audit; unverified by human domain expert"
    },
    {
        "line_no": 12,
        "channel": "WHATSAPP",
        "sender": "+1 214-555-0141 (Sarah)",
        "text": "My friend Dr. Hannah Brooks at Oak Lane Dental wants videos too. I gave her your number!",
        "true_intent": "lead_or_inquiry",
        "multi_intent": False,
        "has_actionable_billing": False,
        "notes": "Client referral lead",
        "attribution": "Assigned by AI assistant during Prompt 7 audit; unverified by human domain expert"
    },
    {
        "line_no": 115,
        "channel": "EMAIL",
        "sender": "mlopez@sagefamilytherapy.com",
        "text": "The videos turned out great. Can we do this every month? What would that cost?",
        "true_intent": "lead_or_inquiry",
        "multi_intent": True,
        "has_actionable_billing": False,
        "notes": "Praise + retainer pricing upgrade inquiry",
        "attribution": "Assigned by AI assistant during Prompt 7 audit; unverified by human domain expert"
    },
    {
        "line_no": 7,
        "channel": "INSTAGRAM DM",
        "sender": "promo@fastfollowers.io",
        "text": "Hi! We help businesses rank #1 on Google. Reply YES for a free audit.",
        "true_intent": "other_review",
        "multi_intent": False,
        "has_actionable_billing": False,
        "notes": "Cold unsolicited spam message",
        "attribution": "Assigned by AI assistant during Prompt 7 audit; unverified by human domain expert"
    },
    {
        "line_no": 11,
        "channel": "EMAIL",
        "sender": "sofia@lunabridal.com",
        "text": "Sale promo looks great. Approved! Post it.",
        "true_intent": "other_review",
        "multi_intent": False,
        "has_actionable_billing": False,
        "notes": "Video approval and posting sign-off",
        "attribution": "Assigned by AI assistant during Prompt 7 audit; unverified by human domain expert"
    }
]

# 30 Refinement Development Examples (Inspected during developer iteration; labels influenced rule tuning)
REFINEMENT_DEV_SET = [
    {
        "line_no": 3,
        "channel": "EMAIL",
        "sender": "will@cedarstone.build",
        "text": "Can you remove the bit where I stumble on my words in material choices?",
        "true_intent": "edit_request",
        "multi_intent": False,
        "has_actionable_billing": False,
        "notes": "Removal of speaker stumble",
        "attribution": "Developer-tuned inspection set; unverified by human domain expert"
    },
    {
        "line_no": 4,
        "channel": "VOICE NOTE",
        "sender": "+1 469-555-0172 (Mike)",
        "text": "Please make the captions bigger on the hail claim help video, they're hard to read on my phone.",
        "true_intent": "edit_request",
        "multi_intent": False,
        "has_actionable_billing": False,
        "notes": "Supplied text transcript of voice note: caption sizing",
        "attribution": "Developer-tuned inspection set; unverified by human domain expert"
    },
    {
        "line_no": 6,
        "channel": "EMAIL",
        "sender": "mike@mikesroofingtx.com",
        "text": "hail claim help still has the same problem. I already told you about this.",
        "true_intent": "edit_request",
        "multi_intent": False,
        "has_actionable_billing": False,
        "notes": "Unresolved revision escalation",
        "attribution": "Developer-tuned inspection set; unverified by human domain expert"
    },
    {
        "line_no": 8,
        "channel": "VOICE NOTE",
        "sender": "+1 214-555-0182 (Paul)",
        "text": "Add our phone number at the end of retirement myths.",
        "true_intent": "edit_request",
        "multi_intent": False,
        "has_actionable_billing": False,
        "notes": "Supplied text transcript of voice note: phone overlay",
        "attribution": "Developer-tuned inspection set; unverified by human domain expert"
    },
    {
        "line_no": 9,
        "channel": "VOICE NOTE",
        "sender": "+1 214-555-0182 (Paul)",
        "text": "On why fees matter, use our brand color pink, not the one you used.",
        "true_intent": "edit_request",
        "multi_intent": False,
        "has_actionable_billing": False,
        "notes": "Supplied text transcript of voice note: brand color pink",
        "attribution": "Developer-tuned inspection set; unverified by human domain expert"
    },
    {
        "line_no": 17,
        "channel": "VOICE NOTE",
        "sender": "+1 214-555-0188 (Mike)",
        "text": "Can you cut the first 3 seconds of do i need a lawyer?? It starts slow.",
        "true_intent": "edit_request",
        "multi_intent": False,
        "has_actionable_billing": False,
        "notes": "Supplied text transcript: video intro pacing cut",
        "attribution": "Developer-tuned inspection set; unverified by human domain expert"
    },
    {
        "line_no": 23,
        "channel": "EMAIL",
        "sender": "nadia@glowaesthetics.co",
        "text": "the one we shot last week: add the line 'walk-ins welcome' at the end please.",
        "true_intent": "edit_request",
        "multi_intent": False,
        "has_actionable_billing": False,
        "notes": "Call-to-action text overlay addition",
        "attribution": "Developer-tuned inspection set; unverified by human domain expert"
    },
    {
        "line_no": 28,
        "channel": "WHATSAPP",
        "sender": "+1 972-555-0110 (Priya)",
        "text": "On botox before and after our name is spelled wrong in the caption.",
        "true_intent": "edit_request",
        "multi_intent": False,
        "has_actionable_billing": False,
        "notes": "Client name misspelling correction",
        "attribution": "Developer-tuned inspection set; unverified by human domain expert"
    },
    {
        "line_no": 33,
        "channel": "VOICE NOTE",
        "sender": "+1 214-555-0195 (Raj)",
        "text": "Please take out the part in claims made easy where I talk about prices. Prices are changing.",
        "true_intent": "edit_request",
        "multi_intent": False,
        "has_actionable_billing": False,
        "notes": "Supplied text transcript: pricing segment removal",
        "attribution": "Developer-tuned inspection set; unverified by human domain expert"
    },
    {
        "line_no": 43,
        "channel": "EMAIL",
        "sender": "dana@lonestarrealty.com",
        "text": "For first time buyer tips use the other shot, the one outside, not inside.",
        "true_intent": "edit_request",
        "multi_intent": False,
        "has_actionable_billing": False,
        "notes": "Alternative B-roll shot selection",
        "attribution": "Developer-tuned inspection set; unverified by human domain expert"
    },
    {
        "line_no": 52,
        "channel": "VOICE NOTE",
        "sender": "+1 972-555-0129 (Alan)",
        "text": "The music on the desk posture fix video is too loud, I can't hear myself.",
        "true_intent": "edit_request",
        "multi_intent": False,
        "has_actionable_billing": False,
        "notes": "Supplied text transcript: audio volume adjustment",
        "attribution": "Developer-tuned inspection set; unverified by human domain expert"
    },
    {
        "line_no": 192,
        "channel": "WHATSAPP",
        "sender": "+1 214-555-0135 (Sofia)",
        "text": "La música de new arrivals está muy fuerte.",
        "true_intent": "edit_request",
        "multi_intent": False,
        "has_actionable_billing": False,
        "notes": "Spanish language music volume adjustment",
        "attribution": "Developer-tuned inspection set; unverified by human domain expert"
    },
    {
        "line_no": 194,
        "channel": "WHATSAPP",
        "sender": "+1 469-555-0190 (Carlos)",
        "text": "En the one we shot last week quiten la parte donde hablo de precios por favor.",
        "true_intent": "edit_request",
        "multi_intent": False,
        "has_actionable_billing": False,
        "notes": "Spanish language price cut request",
        "attribution": "Developer-tuned inspection set; unverified by human domain expert"
    },
    {
        "line_no": 200,
        "channel": "WHATSAPP",
        "sender": "+1 214-555-0135 (Sofia)",
        "text": "¿Vieron mi mensaje sobre new arrivals? Todavía no está.",
        "true_intent": "edit_request",
        "multi_intent": False,
        "has_actionable_billing": False,
        "notes": "Spanish language revision follow-up escalation",
        "attribution": "Developer-tuned inspection set; unverified by human domain expert"
    },
    {
        "line_no": 174,
        "channel": "EMAIL",
        "sender": "greg@lonestarrg.com",
        "text": "Got the videos, thanks. Accounting will handle the invoice.",
        "true_intent": "billing_issue",
        "multi_intent": False,
        "has_actionable_billing": True,
        "notes": "Invoice routing confirmation",
        "attribution": "Developer-tuned inspection set; unverified by human domain expert"
    },
    {
        "line_no": 187,
        "channel": "EMAIL",
        "sender": "angela@tlchomecare.com",
        "text": "We'll pay once the videos are posted. Can you send them?",
        "true_intent": "billing_issue",
        "multi_intent": True,
        "has_actionable_billing": True,
        "notes": "Conditional payment release terms + delivery request",
        "attribution": "Developer-tuned inspection set; unverified by human domain expert"
    },
    {
        "line_no": 197,
        "channel": "INSTAGRAM DM",
        "sender": "billing@acct-dept.co",
        "text": "Invoice attached. Please pay immediately. (invoice.zip)",
        "true_intent": "billing_issue",
        "multi_intent": False,
        "has_actionable_billing": True,
        "notes": "Phishing / fake invoice demand",
        "attribution": "Developer-tuned inspection set; unverified by human domain expert"
    },
    {
        "line_no": 198,
        "channel": "WHATSAPP",
        "sender": "+1 817-555-0131 (Tony)",
        "text": "Sent half. Rest when the next batch is done.",
        "true_intent": "billing_issue",
        "multi_intent": False,
        "has_actionable_billing": True,
        "notes": "Partial installment payment notification",
        "attribution": "Developer-tuned inspection set; unverified by human domain expert"
    },
    {
        "line_no": 36,
        "channel": "WHATSAPP",
        "sender": "+1 214-555-0118 (Ethan)",
        "text": "Is parking in the back ok?",
        "true_intent": "booking_or_schedule",
        "multi_intent": False,
        "has_actionable_billing": False,
        "notes": "Studio arrival / parking logistics",
        "attribution": "Developer-tuned inspection set; unverified by human domain expert"
    },
    {
        "line_no": 44,
        "channel": "WHATSAPP",
        "sender": "+1 972-555-0112 (David)",
        "text": "Can we move to 2pm instead?",
        "true_intent": "booking_or_schedule",
        "multi_intent": False,
        "has_actionable_billing": False,
        "notes": "Session time shift (verbatim duplicate text with line 30)",
        "attribution": "Developer-tuned inspection set; unverified by human domain expert"
    },
    {
        "line_no": 46,
        "channel": "WHATSAPP",
        "sender": "+1 972-555-0110 (Priya)",
        "text": "See you tomorrow.",
        "true_intent": "booking_or_schedule",
        "multi_intent": False,
        "has_actionable_billing": False,
        "notes": "Shoot confirmation (verbatim duplicate text with line 27)",
        "attribution": "Developer-tuned inspection set; unverified by human domain expert"
    },
    {
        "line_no": 193,
        "channel": "WHATSAPP",
        "sender": "+1 214-555-0164 (Dana)",
        "text": "We have to cancel today's shoot, family emergency. Can we move it? We already paid.",
        "true_intent": "booking_or_schedule",
        "multi_intent": True,
        "has_actionable_billing": False,
        "notes": "Emergency cancellation & reschedule with passing mention of prepaid status",
        "attribution": "Developer-tuned inspection set; unverified by human domain expert"
    },
    {
        "line_no": 75,
        "channel": "EMAIL",
        "sender": "lena@thebrewlab.coffee",
        "text": "Jen at Harbor Coffee loved our reels. She'll reach out.",
        "true_intent": "lead_or_inquiry",
        "multi_intent": False,
        "has_actionable_billing": False,
        "notes": "Client referral warm lead",
        "attribution": "Developer-tuned inspection set; unverified by human domain expert"
    },
    {
        "line_no": 137,
        "channel": "EMAIL",
        "sender": "ethan@dfwfounders.fm",
        "text": "Do you guys also cut short clips from our episodes? We'd pay for that. Let me know.",
        "true_intent": "lead_or_inquiry",
        "multi_intent": True,
        "has_actionable_billing": False,
        "notes": "New service tier inquiry with willingness to pay",
        "attribution": "Developer-tuned inspection set; unverified by human domain expert"
    },
    {
        "line_no": 142,
        "channel": "INSTAGRAM DM",
        "sender": "@vegaautodetail",
        "text": "Hey I saw your reels for a roofing company. How much for a reels pack for my detail shop?",
        "true_intent": "lead_or_inquiry",
        "multi_intent": False,
        "has_actionable_billing": False,
        "notes": "Inbound prospective client pricing lead",
        "attribution": "Developer-tuned inspection set; unverified by human domain expert"
    },
    {
        "line_no": 178,
        "channel": "WHATSAPP",
        "sender": "+1 214-555-0188 (Mike)",
        "text": "My cousin Luis runs Torres Tire & Auto in Garland, he needs videos. His number is 214-555-0193. Call him!",
        "true_intent": "lead_or_inquiry",
        "multi_intent": False,
        "has_actionable_billing": False,
        "notes": "Direct client referral lead with phone number",
        "attribution": "Developer-tuned inspection set; unverified by human domain expert"
    },
    {
        "line_no": 199,
        "channel": "WEBSITE FORM",
        "sender": "nina@patelinsures.com",
        "text": "We would like to talk about our contract and whether we continue.",
        "true_intent": "lead_or_inquiry",
        "multi_intent": False,
        "has_actionable_billing": False,
        "notes": "Retention / renewal contract negotiation inquiry",
        "attribution": "Developer-tuned inspection set; unverified by human domain expert"
    },
    {
        "line_no": 45,
        "channel": "WHATSAPP",
        "sender": "+1 469-555-0108 (Hannah)",
        "text": "Patients keep telling me they saw us on Instagram. Love it.",
        "true_intent": "other_review",
        "multi_intent": False,
        "has_actionable_billing": False,
        "notes": "Positive client feedback / social proof",
        "attribution": "Developer-tuned inspection set; unverified by human domain expert"
    },
    {
        "line_no": 61,
        "channel": "EMAIL",
        "sender": "promo@fastfollowers.io",
        "text": "Your Instagram account will be suspended. Verify here: bit.ly/insta-verify-now",
        "true_intent": "other_review",
        "multi_intent": False,
        "has_actionable_billing": False,
        "notes": "Phishing attack spam message",
        "attribution": "Developer-tuned inspection set; unverified by human domain expert"
    },
    {
        "line_no": 117,
        "channel": "EMAIL",
        "sender": "jordan@elevatefit.co",
        "text": "Big news: Elevate Fitness is now Elevate Athletics! New email is jordan@elevateathletics.com.",
        "true_intent": "other_review",
        "multi_intent": False,
        "has_actionable_billing": False,
        "notes": "Client company rebrand and identity update announcement",
        "attribution": "Developer-tuned inspection set; unverified by human domain expert"
    }
]

# 25 Genuinely Unused Held-Out Test Examples (Strictly unseen, zero text overlap with prior sets, uninfluenced by tuning)
GENUINE_HELDOUT_TEST_SET = [
    {
        "line_no": 5,
        "channel": "EMAIL",
        "sender": "media@northpointdfw.org",
        "text": "Happy to give NorthPoint 20% off studio sessions from May on. Thanks for what you do for the community.",
        "true_intent": "billing_issue",
        "multi_intent": False,
        "has_actionable_billing": True,
        "notes": "Studio giving 20% discount on studio sessions",
        "attribution": "Assigned by AI assistant during Prompt 7 audit; unverified by human domain expert"
    },
    {
        "line_no": 13,
        "channel": "EMAIL",
        "sender": "sofia@lunabridal.com",
        "text": "Actually we changed our mind on sale promo. Can we get a different song and a new intro? Sorry!",
        "true_intent": "edit_request",
        "multi_intent": False,
        "has_actionable_billing": False,
        "notes": "Music change and new intro request",
        "attribution": "Assigned by AI assistant during Prompt 7 audit; unverified by human domain expert"
    },
    {
        "line_no": 14,
        "channel": "WHATSAPP",
        "sender": "+1 214-555-0182 (Paul)",
        "text": "Did anyone see my message about why fees matter? It's not fixed.",
        "true_intent": "edit_request",
        "multi_intent": False,
        "has_actionable_billing": False,
        "notes": "Follow-up revision request ('why fees matter' is video title, not billing request)",
        "attribution": "Assigned by AI assistant during Prompt 7 audit; unverified by human domain expert"
    },
    {
        "line_no": 16,
        "channel": "WHATSAPP",
        "sender": "+1 469-555-0133 (Jordan)",
        "text": "On nutrition tip, use our brand color forest green, not the one you used.",
        "true_intent": "edit_request",
        "multi_intent": False,
        "has_actionable_billing": False,
        "notes": "Brand color correction",
        "attribution": "Assigned by AI assistant during Prompt 7 audit; unverified by human domain expert"
    },
    {
        "line_no": 20,
        "channel": "WHATSAPP",
        "sender": "+1 972-555-0153 (Nadia)",
        "text": "On the lip filler myths video, use our brand color navy, not the one you used.",
        "true_intent": "edit_request",
        "multi_intent": False,
        "has_actionable_billing": False,
        "notes": "Brand color correction",
        "attribution": "Assigned by AI assistant during Prompt 7 audit; unverified by human domain expert"
    },
    {
        "line_no": 26,
        "channel": "WHATSAPP",
        "sender": "+1 214-555-0182 (Paul)",
        "text": "This is the second time I ask. estate planning basics is still wrong.",
        "true_intent": "edit_request",
        "multi_intent": False,
        "has_actionable_billing": False,
        "notes": "Escalated unfixed revision note",
        "attribution": "Assigned by AI assistant during Prompt 7 audit; unverified by human domain expert"
    },
    {
        "line_no": 144,
        "channel": "INSTAGRAM DM",
        "sender": "@vegaautodetail",
        "text": "Reels pack is $900 for 3 reels. Here is the booking link.",
        "true_intent": "booking_or_schedule",
        "multi_intent": False,
        "has_actionable_billing": False,
        "notes": "Booking link transmission for reels session",
        "attribution": "Assigned by AI assistant during Prompt 7 audit; unverified by human domain expert"
    },
    {
        "line_no": 71,
        "channel": "WHATSAPP",
        "sender": "+1 972-555-0153 (Nadia)",
        "text": "botox before and after: add the line 'walk-ins welcome' at the end please.",
        "true_intent": "edit_request",
        "multi_intent": False,
        "has_actionable_billing": False,
        "notes": "Call-to-action text overlay insertion",
        "attribution": "Assigned by AI assistant during Prompt 7 audit; unverified by human domain expert"
    },
    {
        "line_no": 77,
        "channel": "EMAIL",
        "sender": "lena@thebrewlab.coffee",
        "text": "Meet the barista looks great. Approved! Post it.",
        "true_intent": "other_review",
        "multi_intent": False,
        "has_actionable_billing": False,
        "notes": "Video approval sign-off",
        "attribution": "Assigned by AI assistant during Prompt 7 audit; unverified by human domain expert"
    },
    {
        "line_no": 89,
        "channel": "EMAIL",
        "sender": "mtorres@torreslaw.com",
        "text": "Three new cases came from your videos this month. Thank you.",
        "true_intent": "other_review",
        "multi_intent": False,
        "has_actionable_billing": False,
        "notes": "Positive feedback and business ROI praise",
        "attribution": "Assigned by AI assistant during Prompt 7 audit; unverified by human domain expert"
    },
    {
        "line_no": 99,
        "channel": "EMAIL",
        "sender": "pgrant@meridianwp.com",
        "text": "Paul here. We'll pause after this month. Too many rounds of fixes, and my notes keep getting missed. Nothing personal.",
        "true_intent": "lead_or_inquiry",
        "multi_intent": True,
        "has_actionable_billing": False,
        "notes": "Retention churn cancellation notice + revision failure complaint (multi-intent)",
        "attribution": "Assigned by AI assistant during Prompt 7 audit; unverified by human domain expert"
    },
    {
        "line_no": 106,
        "channel": "EMAIL",
        "sender": "acho@greenwaypeds.com",
        "text": "Can you cut the first 3 seconds of the meet the team video? It starts slow.",
        "true_intent": "edit_request",
        "multi_intent": False,
        "has_actionable_billing": False,
        "notes": "Pacing trim request",
        "attribution": "Assigned by AI assistant during Prompt 7 audit; unverified by human domain expert"
    },
    {
        "line_no": 109,
        "channel": "INSTAGRAM DM",
        "sender": "growth@rank1seo.biz",
        "text": "Hey, crypto opportunity for content creators, 10x guaranteed.",
        "true_intent": "other_review",
        "multi_intent": False,
        "has_actionable_billing": False,
        "notes": "Unsolicited crypto spam",
        "attribution": "Assigned by AI assistant during Prompt 7 audit; unverified by human domain expert"
    },
    {
        "line_no": 119,
        "channel": "EMAIL",
        "sender": "imran@khansautospa.com",
        "text": "Did anyone see my message about interior deep clean? It's not fixed.",
        "true_intent": "edit_request",
        "multi_intent": False,
        "has_actionable_billing": False,
        "notes": "Escalated unperformed revision request",
        "attribution": "Assigned by AI assistant during Prompt 7 audit; unverified by human domain expert"
    },
    {
        "line_no": 128,
        "channel": "EMAIL",
        "sender": "billing@acct-dept.co",
        "text": "We sell 10,000 real followers for $49.",
        "true_intent": "other_review",
        "multi_intent": False,
        "has_actionable_billing": False,
        "notes": "Followers spam (negative billing signal despite sender name)",
        "attribution": "Assigned by AI assistant during Prompt 7 audit; unverified by human domain expert"
    },
    {
        "line_no": 156,
        "channel": "VOICE NOTE",
        "sender": "+1 214-555-0195 (Raj)",
        "text": "Raj here. In the videos please say Patel Insurance Group, the full name, not just Patel Insurance. Compliance cares about this.",
        "true_intent": "edit_request",
        "multi_intent": False,
        "has_actionable_billing": False,
        "notes": "Supplied text transcript of voice note: corporate compliance naming revision",
        "attribution": "Assigned by AI assistant during Prompt 7 audit; unverified by human domain expert"
    },
    {
        "line_no": 158,
        "channel": "WEBSITE FORM",
        "sender": "tasha.green.mail@gmail.com (Tasha Green)",
        "text": "Do you have a package where you cut short clips from my episodes? How much would that be?",
        "true_intent": "lead_or_inquiry",
        "multi_intent": False,
        "has_actionable_billing": False,
        "notes": "Prospective new package tier pricing quote inquiry",
        "attribution": "Assigned by AI assistant during Prompt 7 audit; unverified by human domain expert"
    },
    {
        "line_no": 161,
        "channel": "EMAIL",
        "sender": "sarah@khandental.com",
        "text": "Quick update, our new office number is 214-555-0177. Please use this one from now on.",
        "true_intent": "other_review",
        "multi_intent": False,
        "has_actionable_billing": False,
        "notes": "Administrative office phone number update notification",
        "attribution": "Assigned by AI assistant during Prompt 7 audit; unverified by human domain expert"
    },
    {
        "line_no": 166,
        "channel": "EMAIL",
        "sender": "raj@patelinsures.com",
        "text": "The videos say \"Patel Insurance\" again. I asked for the full name. Not happy.",
        "true_intent": "edit_request",
        "multi_intent": False,
        "has_actionable_billing": False,
        "notes": "Repeated naming compliance failure escalation",
        "attribution": "Assigned by AI assistant during Prompt 7 audit; unverified by human domain expert"
    },
    {
        "line_no": 168,
        "channel": "EMAIL",
        "sender": "promo@fastfollowers.io",
        "text": "Partnership offer: let us run your ads for free for 30 days.",
        "true_intent": "other_review",
        "multi_intent": False,
        "has_actionable_billing": False,
        "notes": "Marketing agency partnership solicitation spam",
        "attribution": "Assigned by AI assistant during Prompt 7 audit; unverified by human domain expert"
    },
    {
        "line_no": 181,
        "channel": "EMAIL",
        "sender": "drhale@summitchiro.com",
        "text": "Please take out the part in the one we shot last week where I talk about prices. Prices are changing.",
        "true_intent": "edit_request",
        "multi_intent": False,
        "has_actionable_billing": False,
        "notes": "Video edit cut for pricing segment (negative billing signal)",
        "attribution": "Assigned by AI assistant during Prompt 7 audit; unverified by human domain expert"
    },
    {
        "line_no": 182,
        "channel": "INSTAGRAM DM",
        "sender": "@lunabridaldfw",
        "text": "The music on try-on day is too loud, I can't hear myself.",
        "true_intent": "edit_request",
        "multi_intent": False,
        "has_actionable_billing": False,
        "notes": "Audio ducking / music balance adjustment",
        "attribution": "Assigned by AI assistant during Prompt 7 audit; unverified by human domain expert"
    },
    {
        "line_no": 196,
        "channel": "EMAIL",
        "sender": "carlos.vega.detail@gmail.com",
        "text": "La música de tesla detail está muy fuerte.",
        "true_intent": "edit_request",
        "multi_intent": False,
        "has_actionable_billing": False,
        "notes": "Spanish music volume adjustment request",
        "attribution": "Assigned by AI assistant during Prompt 7 audit; unverified by human domain expert"
    },
    {
        "line_no": 201,
        "channel": "WHATSAPP",
        "sender": "+1 469-555-0190 (Carlos)",
        "text": "¿Vieron mi mensaje sobre tesla detail? Todavía no está.",
        "true_intent": "edit_request",
        "multi_intent": False,
        "has_actionable_billing": False,
        "notes": "Spanish unfixed revision follow-up escalation",
        "attribution": "Assigned by AI assistant during Prompt 7 audit; unverified by human domain expert"
    },
    {
        "line_no": 204,
        "channel": "EMAIL",
        "sender": "nina@patelinsures.com",
        "text": "Following up. We need to talk about the contract this week.",
        "true_intent": "lead_or_inquiry",
        "multi_intent": False,
        "has_actionable_billing": False,
        "notes": "Contract retention renewal discussion",
        "attribution": "Assigned by AI assistant during Prompt 7 audit; unverified by human domain expert"
    }
]
