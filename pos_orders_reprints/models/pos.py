# -*- coding: utf-8 -*-


from odoo import fields, models,tools,api, _
from functools import partial
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, timedelta
from odoo.exceptions import UserError


class pos_config(models.Model):
    _inherit = 'pos.config'

    pos_order_reprint = fields.Boolean("Allow Order Reprint",default=True)


    @api.model
    def get_order_detail(self, order_id):
        pos_order = self.env['pos.order'].browse(order_id)
        payment_lines = []
        change = 0
        for i in pos_order.statement_ids:
            if i.amount > 0:
                temp = {
                    'amount': i.amount,
                    'name': i.journal_id.name
                }
                payment_lines.append(temp)
            else:
                change += i.amount
        discount = 0
        order_line = []
        taxes = {}
        amount_subtotal = 0
        currency = pos_order.session_id.currency_id
        for line in pos_order.lines:
            discount += (line.price_unit * line.qty * line.discount) / 100
            order_line.append({
                'product_id': line.product_id.display_name or line.product_id.name,
                'qty': line.qty,
                'price_unit': line.price_unit,
                'unit_name':line.product_id.uom_id.name,
                'discount': line.discount,
                'price_subtotal':line.price_subtotal
                })
            amount_subtotal += line.price_subtotal if line.price_subtotal else 0.0
            if line.tax_ids_after_fiscal_position and line.product_id:
                line_taxes = line.tax_ids_after_fiscal_position.compute_all(line.price_unit * (1-(line.discount or 0.0)/100.0), currency, line.qty, product=line.product_id, partner=line.order_id.partner_id or False)
                for tax in line_taxes['taxes']:
                    taxes.setdefault(tax['id'], {'name': tax['name'], 'tax_amount':0.0, 'base_amount':0.0})
                    taxes[tax['id']]['tax_amount'] += tax['amount'] if tax['amount'] else 0.0
                    taxes[tax['id']]['base_amount'] += tax['base'] if tax['base'] else 0.0
            else:
                taxes.setdefault(0, {'name': _('No Taxes'), 'tax_amount':0.0, 'base_amount':0.0})
                taxes[0]['base_amount'] += line.price_subtotal_incl if line.price_subtotal_incl else 0.0

        order = {
            'name':pos_order.pos_reference,
            'amount_total':pos_order.amount_total,
            'amount_tax':pos_order.amount_tax,
            'amount_subtotal':amount_subtotal,
        }
        return {
            'order_line':order_line,
            'payment_lines':payment_lines,
            'tax_lines': list(taxes.values()),
            'discount':discount,
            'change':change,
            'order':order
            }

