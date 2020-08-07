# -*- coding: utf-8 -*-
# Part of Bistasolutions. See LICENSE file for full copyright and licensing details.
import logging
from odoo import api, fields, models, tools, _
from odoo.addons import decimal_precision as dp

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = "pos.order"
    ordered_cannabis = fields.Float(string='Ordered Cannabis', compute="_compute_ordered_cannabis",
                                    digits=dp.get_precision('Weight Precision Three'))

    @api.multi
    @api.depends('lines')
    def _compute_ordered_cannabis(self):
        total_ordered_cannabis = 0.0
        for rec in self:
            for pos_order_line in rec.lines:
                if pos_order_line.product_id.equivalent_weight > 0:
                    total_ordered_cannabis += pos_order_line.product_id.equivalent_weight * pos_order_line.qty
            rec.ordered_cannabis = total_ordered_cannabis
