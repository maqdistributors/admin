# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    print_qty = fields.Integer(string="Print Qty")

    @api.onchange('product_uom_qty')
    def onchange_quantity(self):
        self.print_qty = int(self.product_uom_qty)

    @api.model
    def create(self, vals):
        if vals.get('product_uom_qty') and 'print_qty' not in vals:
            vals['print_qty'] = int(vals['product_uom_qty'])
        res = super(SaleOrderLine, self).create(vals)
        return res


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def _cart_update(self, product_id=None, line_id=None, add_qty=0, set_qty=0, attributes=None, **kwargs):
        """ Add or set product quantity, add_qty can be negative """
        order_line_vals = super(SaleOrder, self)._cart_update(product_id=product_id, line_id=line_id, add_qty=add_qty, set_qty=set_qty, attributes=attributes, **kwargs)
        if order_line_vals.get('line_id'):
            SaleOrderLineSudo = self.env['sale.order.line'].sudo()
            order_line = SaleOrderLineSudo.browse(order_line_vals['line_id'])
            if order_line.exists():
                order_line.print_qty = order_line_vals['quantity']
        return order_line_vals
