# INFS Client Qualification Scoreboard (`infs_cqs`)

**Client Qualification Scoreboard (FRM-SAL-01)** implementation for Odoo 17 CRM.

---

## 1. Overview & Purpose
This module implements the **FRM-SAL-01 Client Qualification Scorecard** directly inside Odoo CRM Opportunities (`crm.lead`). It ensures that:
- Every prospect is systematically screened during the 15-minute qualification call.
- The score (0–12) and qualification status (*Qualified*, *Unclear need*, *Window shopper*) are automatically computed.
- Deals cannot move forward to client visit stages (such as **Discover**) unless they satisfy the qualification criteria.
- CQS Administrators can override the gate when necessary, with transparent chatter logging.

---

## 2. Technical Architecture

### Models Extended
1. **`crm.stage`**:
   - `need_cqs_passed` (`Boolean`): Flag indicating that leads currently in this stage must pass the CQS gate before they can be moved OUT to another stage. Moving into this stage has no restriction.

2. **`crm.lead`**:
   - **Section A (Call details)**:
     - `partner_id` (`Many2one` -> `res.partner`): Client Company.
     - `cqs_bdc_id` (`Many2one` -> `res.users`): BDC agent conducting the call.
     - `cqs_contact_person` (`Char`): Contact person (computed from `partner_id.name`).
     - `cqs_call_date` (`Date`): Mandatory date of the qualification call.
     - `cqs_lead_source` (`Char`): Lead acquisition source.
     - `cqs_lane` (`Selection`): `1 Infra`, `2 ERP/Odoo`, `3 Brand`, `4 BPA & AI`.
     - `cqs_opportunity_ref` (`Char`): Opportunity reference (computed from `crm.lead.name`).
   - **Section B (Scorecard questions, 0–2 points each)**:
     - `cqs_timing`: Why is now the right time to look at this?
     - `cqs_pain`: What does this problem cost you today in time, money or risk?
     - `cqs_deadline`: By when must this be solved, and what happens if it isn't?
     - `cqs_budget`: Has budget been allocated, or are you building the budget?
     - `cqs_decision`: Who besides you decides? Can they join our meeting?
     - `cqs_competition`: Who else are you talking to, and why did you include us?
     - `cqs_score` (`Integer`, computed, stored): Total points (0–12).
     - `cqs_score_completed` (`Boolean`, computed, stored): True when all 6 questions are answered.
     - `cqs_result` (`Selection`, computed, stored):
       - `incomplete`: Not all 6 questions answered.
       - `qualified`: 9–12 points.
       - `unclear`: 5–8 points.
       - `shopper`: 0–4 points.
   - **Section D (Give-to-get Commitments)**:
     - `cqs_g2g_decision_maker` (`Boolean`) + note
     - `cqs_g2g_info_sent` (`Boolean`) + note
     - `cqs_g2g_questionnaire` (`Boolean`) + note
     - `cqs_g2g_paid_diagnostic` (`Boolean`) + note
     - `cqs_g2g_received` (`Boolean`, computed, stored): True if any of the 4 is checked.
   - **Section E (Follow-up Signals)**:
     - `cqs_signal_reply` (Yes/No + Date)
     - `cqs_signal_info` (Yes/No + Date)
     - `cqs_signal_people` (Yes/No + Date)
     - `cqs_signal_next_step` (Yes/No + Date)
     - `cqs_missed_signals` (`Integer`, computed, stored): Count of 'No' responses.
     - `cqs_show_nurture_warning` (`Boolean`): Active when `cqs_missed_signals >= 2`.
   - **Section F (Client's Own Words & Attachments)**:
     - `cqs_client_words` (`Text`): Direct customer quotes and notes.
     - `cqs_scorecard_attachment` (`Binary`): Scanned/signed paper form FRM-SAL-01.
     - `cqs_bdc_signed` / `cqs_bdc_sign_date`: BDC review sign-off.
     - `cqs_reviewed_by_sales_head` / `cqs_sales_head_review_date`: Head of Sales review sign-off.

---

## 3. Stage Gate Screening Logic

- **Stages with `need_cqs_passed = True`**:
  - Leads can come in from other stages with **no restriction**.
  - Leads can be created directly in this stage with **no restriction** (no override warning required).
  - Leads can only **move OUT to other stages** if the scorecard is passed or if overridden by an Admin.
- **Stages with `need_cqs_passed = False`**:
  - Leads can move in and out freely with **no restriction**.

### Pass Condition:
$$\text{Passed} = (\text{Result} = \text{'qualified'} \land \text{Give-to-get Received} = \text{True}) \lor (\text{Paid Diagnostic Agreed} = \text{True})$$

### Block & Override Behavior:
* **Standard User (Non-Admin)**:
  - If an unqualified lead is moved out of a gated stage, raises a `UserError`:
    > *"This opportunity has not passed client screening (FRM-SAL-01). Complete the scorecard and obtain at least one give-to-get commitment before booking a visit."*
* **CQS Admin (`infs_cqs.group_cqs_admin`)**:
  - The stage change is allowed.
  - Automatically posts an override note in the opportunity's chatter:
    > *"CQS Screening Gate Override: User [User Name] moved this opportunity out of stage [Current Stage] to [Target Stage] on [Date/Time] without meeting full screening requirements."*

---

## 4. User Permission Groups
Configured under User Settings (**CQS Qualification** dropdown):
- **None**: Default standard CRM user without special CQS privileges.
- **Viewer** (`infs_cqs.group_cqs_viewer`): Read and view access to the qualification scorecard.
- **Admin** (`infs_cqs.group_cqs_admin`): Ability to configure stage gates and override blocked stage changes.

---

## 5. Views & Reporting
1. **Opportunity Form View**:
   - Tab named **"Qualification"** containing Sections A to F styled after the FRM-SAL-01 paper form.
   - Nurture warning banner appears when 2 or more signals are missed.
   - **Archive Unpassed Opportunity**: If the scorecard is completed and not passed, a red alert banner with **[Archive Opportunity]** appears with a confirmation popup. Confirming archives the lead, assigns the lost reason, and logs a note in the chatter.
2. **Opportunity Kanban View**:
   - Visual colored badge:
     - 🟢 **Green** (`9–12`): Qualified
     - 🟡 **Amber** (`5–8`): Unclear Need
     - 🔴 **Red** (`0–4`): Window Shopper
     - ⚪ **Grey**: Score Missing
3. **Search & Filters**:
   - Filters: *CQS Qualified (9–12)*, *CQS Unclear Need (5–8)*, *CQS Window Shopper (0–4)*, *CQS Score Missing*.
   - Group By: *CQS Result*, *CQS Lane*, *CQS BDC*.
4. **Thursday PQM Review Report**:
   - Accessible via **CRM > Reporting > Qualification Scorecard (CQS)**.
   - Pivot table and bar graph reporting average `cqs_score` and count grouped by Salesperson (`user_id`) and Service Lane (`cqs_lane`).
5. **Lost Reasons**:
   - Added: *Window shopper / no real need*
   - Added: *No give-to-get commitment*

---

## 6. Acceptance Testing Scenarios

| Test Case | Scenario | Expected Behavior |
|:---|:---|:---|
| **(a)** | Score = 10, Give-to-get = None | Blocked from moving to Discover with UserError. |
| **(b)** | Score = 10, Give-to-get = 1+ checked | Stage change to Discover succeeds. |
| **(c)** | Score = 6, Paid diagnostic agreed = True | Stage change to Discover succeeds. |
| **(d)** | Score = 3 (Window shopper), Give-to-get = None | Blocked from moving to Discover with UserError. |
| **(e)** | Unqualified lead moved by CQS Admin | Stage change succeeds; Chatter logs override with user and timestamp. |
| **(f)** | Missed signals counter reaches 2 | Warning banner appears advising "Move to nurture". |
| **(g)** | Saving question score without Call Date | Raises ValidationError requiring Call Date in Section A. |
