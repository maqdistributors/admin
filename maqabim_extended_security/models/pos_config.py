# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    restrict_closing = fields.Boolean(compute="_compute_restrict_closing")

    @api.depends('session_ids')
    def _compute_restrict_closing(self):
        for pos_config in self:
            session = pos_config.session_ids.filtered(lambda r: r.user_id.id == self.env.uid and \
                not r.state == 'closed' and \
                not r.rescue)
            # sessions ordered by id desc
            pos_config.restrict_closing = session and session[0].restrict_session_closing


class PosSession(models.Model):
    _inherit = "pos.session"

    restrict_session_closing = fields.Boolean(compute="_compute_restrict_session_closing")

    def _compute_restrict_session_closing(self):
        for session in self:
            if session.state in ['opened', 'closing_control'] and self.env.user.has_group("maqabim_extended_security.group_restrict_pos_closing"):
                session.restrict_session_closing = True
