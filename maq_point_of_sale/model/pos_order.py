# -*- coding: utf-8 -*-
# Part of Bistasolutions. See LICENSE file for full copyright and licensing details.
import logging
from odoo import api, fields, models, tools, _

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = "pos.order"
    customer_verified = fields.Boolean(string='Verified Customer ID',
                                       help='Need to raise a warning for each POS transaction prior to moving to payment screen.',
                                       default=False)

    @api.model
    def _order_fields(self, ui_order):
        order_fields = super(PosOrder, self)._order_fields(ui_order)
        order_fields['customer_verified'] = ui_order.get('customer_verified', False)
        return order_fields
