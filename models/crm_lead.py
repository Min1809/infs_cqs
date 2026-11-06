# -*- coding: utf-8 -*-
from markupsafe import Markup
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    # -------------------------------------------------------------------------
    # SECTION A: Call details
    # -------------------------------------------------------------------------
    cqs_bdc_id = fields.Many2one(
        'res.users',
        string="BDC",
        default=lambda self: self.env.user,
        tracking=True,
        help="Business Development Consultant / Rep responsible for the screening call."
    )
    cqs_call_date = fields.Date(
        string="Call Date",
        tracking=True,
        help="Date of the qualification call. Required before scores can be saved."
    )
    cqs_lead_source = fields.Char(
        string="Lead Source",
        tracking=True,
        help="Source of the lead (inbound or outbound channel)."
    )
    cqs_lane = fields.Selection(
        [
            ('1', '1 Infra'),
            ('2', '2 ERP/Odoo'),
            ('3', '3 Brand'),
            ('4', '4 BPA & AI'),
        ],
        string="Lane",
        tracking=True,
        help="Infinity IT Group service lane."
    )
    cqs_contact_person = fields.Char(
        string="Contact Person",
        compute="_compute_cqs_contact_person",
        readonly=True
    )
    cqs_opportunity_ref = fields.Char(
        string="Odoo Opportunity Ref.",
        compute="_compute_cqs_opportunity_ref",
        readonly=True
    )

    # -------------------------------------------------------------------------
    # SECTION B: Qualification questions (score 0, 1 or 2)
    # -------------------------------------------------------------------------
    cqs_timing = fields.Selection(
        [
            ('0', 'Being polite, no current need, “send a brochure”'),
            ('1', 'General interest, no specific event'),
            ('2', 'Specific event: failure, audit, expansion, contract ending, unhappy with vendor'),
        ],
        string="1. Timing",
        tracking=True,
        help="Why is now the right time to look at this? (inbound or outbound)"
    )
    cqs_pain = fields.Selection(
        [
            ('0', 'Cannot name an impact'),
            ('1', 'Vague impact'),
            ('2', 'Clear cost described'),
        ],
        string="2. Pain",
        tracking=True,
        help="What does this problem cost you today in time, money or risk?"
    )
    cqs_deadline = fields.Selection(
        [
            ('0', 'No rush, maybe next year'),
            ('1', 'Rough quarter or year'),
            ('2', 'Date tied to a business reason'),
        ],
        string="3. Deadline",
        tracking=True,
        help="By when must this be solved, and what happens if it isn't?"
    )
    cqs_budget = fields.Selection(
        [
            ('0', 'Refuses to discuss budget'),
            ('1', 'Building next year\'s budget'),
            ('2', 'Budget allocated or range given'),
        ],
        string="4. Budget",
        tracking=True,
        help="Has budget been allocated, or are you building the budget?"
    )
    cqs_decision = fields.Selection(
        [
            ('0', '“I\'ll forward it to management”'),
            ('1', 'Decision maker known, not joining'),
            ('2', 'Decision maker identified and attending'),
        ],
        string="5. Decision",
        tracking=True,
        help="Who besides you decides? Can they join our meeting?"
    )
    cqs_competition = fields.Selection(
        [
            ('0', 'Needs 3 quotes, price only'),
            ('1', 'Comparing on several factors'),
            ('2', 'Referral, or chose us for a clear reason'),
        ],
        string="6. Competition",
        tracking=True,
        help="Who else are you talking to, and why did you include us?"
    )

    cqs_score_timing = fields.Char(string="Timing Score", compute="_compute_individual_scores")
    cqs_score_pain = fields.Char(string="Pain Score", compute="_compute_individual_scores")
    cqs_score_deadline = fields.Char(string="Deadline Score", compute="_compute_individual_scores")
    cqs_score_budget = fields.Char(string="Budget Score", compute="_compute_individual_scores")
    cqs_score_decision = fields.Char(string="Decision Score", compute="_compute_individual_scores")
    cqs_score_competition = fields.Char(string="Competition Score", compute="_compute_individual_scores")

    cqs_score = fields.Integer(
        string="Qualification Score",
        compute="_compute_cqs_score",
        store=True,
        tracking=True,
        help="Sum of the 6 qualification questions (0–12). Empty until all 6 are answered."
    )
    cqs_score_completed = fields.Boolean(
        string="Scorecard Completed",
        compute="_compute_cqs_score",
        store=True
    )
    cqs_result = fields.Selection(
        [
            ('incomplete', 'Incomplete'),
            ('qualified', 'Qualified (9–12)'),
            ('unclear', 'Unclear need (5–8)'),
            ('shopper', 'Window shopper (0–4)'),
        ],
        string="Qualification Result",
        compute="_compute_cqs_result",
        store=True,
        tracking=True
    )
    cqs_can_archive = fields.Boolean(
        string="Can Archive Unqualified",
        compute="_compute_cqs_can_archive"
    )

    # -------------------------------------------------------------------------
    # SECTION D: Give-to-get commitments
    # -------------------------------------------------------------------------
    cqs_g2g_decision_maker = fields.Boolean(
        string="Decision maker attends the first meeting",
        tracking=True
    )
    cqs_g2g_decision_maker_note = fields.Char(string="Decision Maker Date / Note")

    cqs_g2g_info_sent = fields.Boolean(
        string="Information sent in advance (counts, diagram, systems, reports)",
        tracking=True
    )
    cqs_g2g_info_sent_note = fields.Char(string="Information Sent Date / Note")

    cqs_g2g_questionnaire = fields.Boolean(
        string="Pre-meeting questionnaire completed",
        tracking=True
    )
    cqs_g2g_questionnaire_note = fields.Char(string="Questionnaire Date / Note")

    cqs_g2g_paid_diagnostic = fields.Boolean(
        string="Paid diagnostic agreed (Health Check, Pre-assessment, Audit, AI-readiness)",
        tracking=True
    )
    cqs_g2g_paid_diagnostic_note = fields.Char(string="Paid Diagnostic Date / Note")

    cqs_g2g_received = fields.Boolean(
        string="Give-to-get Received",
        compute="_compute_cqs_g2g_received",
        store=True,
        tracking=True,
        help="True if any of the 4 give-to-get boxes is ticked."
    )

    # -------------------------------------------------------------------------
    # SECTION E: Follow-up signals
    # -------------------------------------------------------------------------
    cqs_signal_reply = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')],
        string="Replied to our follow-up within 48 hours"
    )
    cqs_signal_reply_date = fields.Date(string="Reply Signal Date")

    cqs_signal_info = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')],
        string="Sent the information we requested"
    )
    cqs_signal_info_date = fields.Date(string="Info Signal Date")

    cqs_signal_people = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')],
        string="Brought the right people to the meeting"
    )
    cqs_signal_people_date = fields.Date(string="People Signal Date")

    cqs_signal_next_step = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')],
        string="Agreed a date for the next step"
    )
    cqs_signal_next_step_date = fields.Date(string="Next Step Signal Date")

    cqs_missed_signals = fields.Integer(
        string="Missed Follow-up Signals",
        compute="_compute_cqs_missed_signals",
        store=True,
        help="Counter of missed signals (where answer is 'No'). At 2, warning banner advises: 'Move to nurture'."
    )
    cqs_show_nurture_warning = fields.Boolean(
        string="Show Nurture Warning",
        compute="_compute_cqs_missed_signals"
    )

    # -------------------------------------------------------------------------
    # SECTION F: Client's own words & Attachments
    # -------------------------------------------------------------------------
    cqs_client_words = fields.Text(
        string="Client's Own Words",
        help="Key answers, pain points, stakeholder names."
    )
    cqs_scorecard_attachment = fields.Binary(
        string="Scorecard Attachment",
        attachment=True,
        help="Optional upload of the signed paper form (FRM-SAL-01)."
    )
    cqs_scorecard_attachment_name = fields.Char(string="Scorecard Attachment Filename")

    cqs_bdc_signed = fields.Boolean(string="BDC Signed")
    cqs_bdc_sign_date = fields.Date(string="BDC Signature Date")

    cqs_reviewed_by_sales_head = fields.Boolean(string="Reviewed by Head of Sales")
    cqs_sales_head_review_date = fields.Date(string="Head of Sales Review Date")

    # -------------------------------------------------------------------------
    # EXISTING CUSTOMER EXEMPTION
    # -------------------------------------------------------------------------
    cqs_is_existing_customer = fields.Boolean(
        string="Is Existing Customer",
        compute="_compute_cqs_existing_customer",
        help="True if the commercial partner has previous confirmed sales orders (state in 'sale' or 'done')."
    )
    cqs_previous_so_count = fields.Integer(
        string="Previous Confirmed Orders",
        compute="_compute_cqs_existing_customer",
        help="Number of previous confirmed sales orders for this commercial partner (excluding this opportunity)."
    )

    # -------------------------------------------------------------------------
    # COMPUTED METHODS & CONSTRAINTS
    # -------------------------------------------------------------------------
    @api.depends('partner_id', 'partner_id.commercial_partner_id')
    def _compute_cqs_existing_customer(self):
        sale_order_model = self.env['sale.order']
        has_opp_field = 'opportunity_id' in sale_order_model._fields

        for lead in self:
            partner = lead.partner_id
            if not partner:
                lead.cqs_is_existing_customer = False
                lead.cqs_previous_so_count = 0
                continue

            commercial_partner = partner.commercial_partner_id or partner
            domain = [
                ('partner_id', 'child_of', commercial_partner.id),
                ('state', 'in', ('sale', 'done')),
            ]
            # Exclude orders generated from this specific opportunity
            if lead.id and has_opp_field:
                domain.append(('opportunity_id', '!=', lead.id))

            so_count = sale_order_model.search_count(domain)
            lead.cqs_previous_so_count = so_count
            lead.cqs_is_existing_customer = (so_count > 0)

    @api.depends('partner_id', 'partner_id.name')
    def _compute_cqs_contact_person(self):
        for lead in self:
            lead.cqs_contact_person = lead.partner_id.name or ""

    @api.depends('name')
    def _compute_cqs_opportunity_ref(self):
        for lead in self:
            lead.cqs_opportunity_ref = lead.name or ""

    @api.depends('cqs_timing', 'cqs_pain', 'cqs_deadline', 'cqs_budget', 'cqs_decision', 'cqs_competition')
    def _compute_individual_scores(self):
        for lead in self:
            lead.cqs_score_timing = str(lead.cqs_timing) if lead.cqs_timing is not False and lead.cqs_timing is not None else "-"
            lead.cqs_score_pain = str(lead.cqs_pain) if lead.cqs_pain is not False and lead.cqs_pain is not None else "-"
            lead.cqs_score_deadline = str(lead.cqs_deadline) if lead.cqs_deadline is not False and lead.cqs_deadline is not None else "-"
            lead.cqs_score_budget = str(lead.cqs_budget) if lead.cqs_budget is not False and lead.cqs_budget is not None else "-"
            lead.cqs_score_decision = str(lead.cqs_decision) if lead.cqs_decision is not False and lead.cqs_decision is not None else "-"
            lead.cqs_score_competition = str(lead.cqs_competition) if lead.cqs_competition is not False and lead.cqs_competition is not None else "-"

    @api.depends('cqs_timing', 'cqs_pain', 'cqs_deadline', 'cqs_budget', 'cqs_decision', 'cqs_competition')
    def _compute_cqs_score(self):
        for lead in self:
            answers = [
                lead.cqs_timing,
                lead.cqs_pain,
                lead.cqs_deadline,
                lead.cqs_budget,
                lead.cqs_decision,
                lead.cqs_competition,
            ]
            if all(a is not False and a is not None for a in answers):
                lead.cqs_score = sum(int(a) for a in answers)
                lead.cqs_score_completed = True
            else:
                lead.cqs_score = 0
                lead.cqs_score_completed = False

    @api.depends('cqs_score', 'cqs_score_completed')
    def _compute_cqs_result(self):
        for lead in self:
            if not lead.cqs_score_completed:
                lead.cqs_result = 'incomplete'
            elif lead.cqs_score >= 9:
                lead.cqs_result = 'qualified'
            elif lead.cqs_score >= 5:
                lead.cqs_result = 'unclear'
            else:
                lead.cqs_result = 'shopper'

    @api.depends(
        'cqs_g2g_decision_maker',
        'cqs_g2g_info_sent',
        'cqs_g2g_questionnaire',
        'cqs_g2g_paid_diagnostic'
    )
    def _compute_cqs_g2g_received(self):
        for lead in self:
            lead.cqs_g2g_received = any([
                lead.cqs_g2g_decision_maker,
                lead.cqs_g2g_info_sent,
                lead.cqs_g2g_questionnaire,
                lead.cqs_g2g_paid_diagnostic,
            ])

    @api.depends(
        'cqs_signal_reply',
        'cqs_signal_info',
        'cqs_signal_people',
        'cqs_signal_next_step'
    )
    def _compute_cqs_missed_signals(self):
        for lead in self:
            signals = [
                lead.cqs_signal_reply,
                lead.cqs_signal_info,
                lead.cqs_signal_people,
                lead.cqs_signal_next_step,
            ]
            missed_count = sum(1 for s in signals if s == 'no')
            lead.cqs_missed_signals = missed_count
            lead.cqs_show_nurture_warning = (missed_count >= 2)

    @api.constrains('cqs_timing', 'cqs_pain', 'cqs_deadline', 'cqs_budget', 'cqs_decision', 'cqs_competition', 'cqs_call_date')
    def _check_cqs_call_date(self):
        for lead in self:
            has_any_score = any([
                lead.cqs_timing is not False,
                lead.cqs_pain is not False,
                lead.cqs_deadline is not False,
                lead.cqs_budget is not False,
                lead.cqs_decision is not False,
                lead.cqs_competition is not False,
            ])
            if has_any_score and not lead.cqs_call_date:
                raise ValidationError("Qualification Call Date (Section A) is required before qualification scorecard answers can be saved.")

    @api.depends('active', 'cqs_score_completed', 'cqs_result', 'cqs_g2g_received', 'cqs_g2g_paid_diagnostic', 'cqs_is_existing_customer')
    def _compute_cqs_can_archive(self):
        for lead in self:
            lead.cqs_can_archive = bool(
                lead.active and lead.cqs_score_completed and not lead._check_cqs_passed()
            )

    # -------------------------------------------------------------------------
    # STAGE GATE VALIDATION, ARCHIVING & OVERRIDE
    # -------------------------------------------------------------------------
    def _check_cqs_passed(self):
        """Check whether lead satisfies the qualification screening gate:
        1. (Result = Qualified AND Give-to-get Received = True)
        OR
        2. Paid diagnostic agreed = True
        OR
        3. Existing customer with previous confirmed sales orders (state in 'sale' or 'done')
        """
        self.ensure_one()
        is_qualified = (self.cqs_result == 'qualified')
        g2g_received = bool(self.cqs_g2g_received)
        paid_diagnostic = bool(self.cqs_g2g_paid_diagnostic)
        is_existing_customer = bool(self.cqs_is_existing_customer)
        return (is_qualified and g2g_received) or paid_diagnostic or is_existing_customer

    def action_archive_unpassed_cqs(self):
        """Archive unqualified opportunity with lost reason and log in chatter."""
        lost_reason_shopper = self.env.ref('infs_cqs.lost_reason_window_shopper', raise_if_not_found=False)
        lost_reason_no_g2g = self.env.ref('infs_cqs.lost_reason_no_give_to_get', raise_if_not_found=False)

        for lead in self:
            lost_reason = False
            if lead.cqs_result == 'shopper' and lost_reason_shopper:
                lost_reason = lost_reason_shopper
            elif lost_reason_no_g2g:
                lost_reason = lost_reason_no_g2g

            if hasattr(lead, 'action_set_lost') and lost_reason:
                lead.action_set_lost(lost_reason_id=lost_reason.id)
            else:
                vals = {'active': False}
                if lost_reason:
                    vals['lost_reason_id'] = lost_reason.id
                lead.write(vals)

            reason_text = f" (Lost Reason: <b>{lost_reason.name}</b>)" if lost_reason else ""
            result_label = dict(lead._fields['cqs_result'].selection).get(lead.cqs_result, lead.cqs_result or 'Incomplete')
            lead.message_post(
                body=Markup(
                    f"<b>Opportunity Archived:</b><br/>"
                    f"This opportunity was archived because it did not pass client screening (FRM-SAL-01).<br/>"
                    f"Score: <b>{lead.cqs_score}/12</b> ({result_label}).{reason_text}"
                ),
                subtype_xmlid='mail.mt_note'
            )

    def write(self, vals):
        stage_id = vals.get('stage_id')
        target_stage = self.env['crm.stage'].browse(stage_id) if stage_id else False

        # Identify leads that are currently in a stage with need_cqs_passed = True
        # and are attempting to move OUT of it to a different stage.
        gated_exit_leads = []
        if target_stage:
            for lead in self:
                if lead.stage_id and lead.stage_id.need_cqs_passed and lead.stage_id != target_stage:
                    gated_exit_leads.append((lead, lead.stage_id))

        res = super(CrmLead, self).write(vals)

        if gated_exit_leads:
            is_admin = self.env.user.has_group('infs_cqs.group_cqs_admin')
            now_str = fields.Datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            for lead, source_stage in gated_exit_leads:
                if not lead._check_cqs_passed():
                    if is_admin:
                        lead.message_post(
                            body=Markup(
                                f"<b>CQS Screening Gate Override:</b><br/>"
                                f"User <b>{self.env.user.name}</b> moved this opportunity out of stage "
                                f"<b>{source_stage.name}</b> to <b>{target_stage.name}</b> on {now_str} "
                                f"without meeting full screening requirements."
                            ),
                            subtype_xmlid='mail.mt_note'
                        )
                    else:
                        raise UserError(
                            "This opportunity has not passed client screening (FRM-SAL-01). "
                            "Complete the scorecard and obtain at least one give-to-get commitment before booking a visit."
                        )
        return res

