# -*- coding: utf-8 -*-
{
    "name": "INFS Client Qualification Scoreboard (CQS)",
    "version": "17.0.1.0.0",
    "category": "CRM",
    "summary": "Client Qualification Scorecard (FRM-SAL-01) with Stage Gate Screening for Odoo CRM",
    "description": """
Client Qualification Scorecard (FRM-SAL-01)
============================================
Implements the FRM-SAL-01 client screening scorecard directly on CRM Opportunities:

Key Features:
-------------
1. **Section A: Call Details**:
   - BDC representative, qualification call date, lead source, and service lane (1 Infra, 2 ERP/Odoo, 3 Brand, 4 BPA & AI).
   - Call date mandatory before qualification score can be saved.

2. **Section B: 6-Criterion Scoring (0, 1, or 2 points)**:
   - Timing, Pain, Deadline, Budget, Decision, Competition.
   - Automatic score calculation (0–12), empty until all 6 criteria are scored.
   - Result classification:
     * Incomplete: (< 6 answered)
     * Qualified: 9–12
     * Unclear need: 5–8
     * Window shopper: 0–4

3. **Section C: Dynamic Routing Guidance**:
   - Visual highlighting of the required action according to qualification score.

4. **Section D: Give-to-get Commitments**:
   - 4 specific commitments with date/note tracking.
   - Automatic Give-to-get Received status.

5. **Section E: Follow-up Signals**:
   - 4 behavioral signal checkpoints.
   - Automated missed-signal counter.
   - Warning alert banner advising 'Move to nurture' at 2+ missed signals.

6. **Section F: Client's Own Words & Attachments**:
   - Direct quote capture and physical FRM-SAL-01 upload.
   - BDC & Head of Sales sign-off fields.

7. **Stage Gate Enforcement (e.g. Discover Stage)**:
   - Configurable per stage via 'Need CQS Passed' flag.
   - Blocks advancement unless: (Qualified AND Give-to-get Received) OR Paid diagnostic agreed.
   - Administrator override logged automatically in opportunity chatter with user and timestamp.

8. **Views & Reporting**:
   - Scorecard tab laid out exactly like FRM-SAL-01 paper form.
   - Colored score badge on Kanban cards (Green, Amber, Red).
   - Dedicated search filters: Qualified, Unclear need, Window shopper, Score missing.
   - Thursday PQM review pivot and graph reports by salesperson and lane.
   - Custom lost reasons: 'Window shopper / no real need' and 'No give-to-get commitment'.
    """,
    "author": "Infinity IT Group",
    "website": "https://www.infinityitsuccess.com",
    "license": "LGPL-3",
    "depends": [
        "crm",
        "mail",
    ],
    "data": [
        "security/security_groups.xml",
        "data/crm_lost_reason_data.xml",
        "views/crm_stage_views.xml",
        "views/crm_lead_views.xml",
        "views/crm_lead_search_views.xml",
        "views/crm_lead_report_views.xml",
        "views/menu_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "infs_cqs/static/src/css/cqs_style.css",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
