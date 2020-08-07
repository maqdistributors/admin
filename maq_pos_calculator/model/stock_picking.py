# -*- coding: utf-8 -*-
# Part of Bistasolutions. See LICENSE file for full copyright and licensing details.
import logging
from odoo import api, fields, models, tools, _
from odoo.addons import decimal_precision as dp

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = "stock.picking"
    ordered_equivalent = fields.Float(string="Ordered Equivalent", compute="_compute_ordered_shipped_equivalent",
                                      digits=dp.get_precision('Weight Precision Three'))
    shipped_equivalent = fields.Float(string="Shipped Equivalent", compute="_compute_ordered_shipped_equivalent",
                                      digits=dp.get_precision('Weight Precision Three'))

    @api.multi
    @api.depends('move_lines')
    def _compute_ordered_shipped_equivalent(self):
        total_ordered_equivalent = 0.0
        total_shipped_equivalent = 0.0
        for rec in self:
            for move_line in rec.move_lines:
                if move_line.product_id.equivalent_weight > 0:
                    total_ordered_equivalent += move_line.product_id.equivalent_weight * move_line.product_uom_qty
                    total_shipped_equivalent += move_line.product_id.equivalent_weight * move_line.quantity_done
            rec.ordered_equivalent = total_ordered_equivalent
            rec.shipped_equivalent = total_shipped_equivalent
