# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models
from odoo.tools import float_is_zero


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        """
        Add undelivered so lines in invoice lines 
        """
        zero_qty_lines = []
        invoice_lines = self.env['account.invoice.line']
        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        for order in self:
            group_key = order.id if grouped else (
                order.partner_invoice_id.id, order.currency_id.id)
            for line in order.order_line.sorted(key=lambda l: l.qty_to_invoice < 0):
                if float_is_zero(line.qty_to_invoice, precision_digits=precision):
                    vals = line._prepare_invoice_line(qty=0)
                    vals.update({'sale_line_ids': [(6, 0, [line.id])]})
                    zero_qty_lines += [vals]
        invoice_id = super(
            SaleOrder, self).action_invoice_create(grouped, final)
        if invoice_id:
            for vals in zero_qty_lines:
                vals.update({'invoice_id': invoice_id[0]})
                self.env['account.invoice.line'].create(vals)
        return invoice_id
