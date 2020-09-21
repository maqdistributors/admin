# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    print_qty = fields.Integer(string="Print Qty")

    @api.onchange('product_uom_qty')
    def onchange_quantity(self):
        self.print_qty = int(self.product_uom_qty)

    @api.model
    def create(self, vals):
        if vals.get('product_uom_qty'):
            vals['print_qty'] = int(vals['product_uom_qty'])
        res = super(StockMove, self).create(vals)
        return res
