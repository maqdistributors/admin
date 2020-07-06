# -*- coding: utf-8 -*-
# Part of Bistasolutions. See LICENSE file for full copyright and licensing details.
import logging
from datetime import timedelta
from functools import partial

import psycopg2
import pytz

from odoo import api, fields, models, tools, _
from odoo.tools import float_is_zero
from odoo.exceptions import UserError
from odoo.http import request
from odoo.addons import decimal_precision as dp

_logger = logging.getLogger(__name__)


class PosConfig(models.Model):
    _inherit = "pos.config"
    payment_confirmation_box = fields.Boolean(string='Show Payment Confirmation Box',
                                              help='Raise a warning for each POS transaction prior to moving to payment screen.',
                                              default=False)
    iface_available_categ_ids = fields.Many2many('pos.category', string='Available PoS Product Categories',
                                                 help='The point of sale will not display products which are within one of the selected category trees. If no category is specified, all available products will be shown')
    limit_categories = fields.Boolean("Restrict Available Product Categories")

    @api.onchange('limit_categories', 'iface_available_categ_ids', 'iface_start_categ_id')
    def _onchange_limit_categories(self):
        res = {}
        if not self.limit_categories:
            self.iface_available_categ_ids = False
        if self.iface_available_categ_ids and self.iface_start_categ_id.id not in self.iface_available_categ_ids.ids:
            self.iface_start_categ_id = False
        return res

    @api.depends('iface_available_categ_ids')
    def _compute_selectable_categories(self):
        for config in self:
            if config.iface_available_categ_ids:
                config.selectable_categ_ids = config.iface_available_categ_ids
            else:
                config.selectable_categ_ids = self.env['pos.category'].search([])

    @api.multi
    def write(self, vals):
        context_id = self._context.get("context_id", 0)
        if context_id:
            context_id = context_id.id
        opened_session = self.mapped('session_ids').filtered(lambda s: s.state != 'closed' and s.id != context_id)
        if opened_session and opened_session[0].exists():
            raise UserError(
                _('Unable to modify this PoS Configuration because there is an open PoS Session based on it.'))

        result = super(PosConfig, self).write(vals)

        self.sudo()._set_fiscal_position()
        self.sudo()._check_modules_to_install()
        self.sudo()._check_groups_implied()
        return result

    @api.multi
    def open_session_cb(self):
        """ new session button

        create one if none exist
        access cash control interface if enabled or start a session
        """
        self.ensure_one()
        if not self.current_session_id:
            current_session_id = self.env['pos.session'].create({
                'user_id': self.env.uid,
                'config_id': self.id
            })
            ctx = dict(self._context)
            ctx['context_id'] = current_session_id
            self.with_context(ctx).current_session_id = current_session_id
            # self.current_session_id = current_session_id
            if self.current_session_id.state == 'opened':
                print("440")
                return self.open_ui()
            return self._open_session(self.current_session_id.id)
        return self._open_session(self.current_session_id.id)

