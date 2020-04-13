# -*- coding: utf-8 -*-

from odoo import fields, models,tools,api
import logging
from functools import partial
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, timedelta
from odoo.exceptions import UserError
import pytz

class pos_config(models.Model):
    _inherit = 'pos.config' 

    allow_order_return = fields.Boolean('Allow order return', default=True)

class product_product(models.Model):
    _inherit = 'product.product'

    is_not_returnable = fields.Boolean("Is Not Returnable",default=False) 

class pos_order_line(models.Model):
    _inherit = 'pos.order.line'

    returned_qty = fields.Float("Returned Qty")

class pos_order(models.Model):
    _inherit = 'pos.order'
    
    posreference_number = fields.Char()
    
    @api.model
    def _order_fields(self, ui_order):
        res = super(pos_order, self)._order_fields(ui_order)
        if 'reference_number' in ui_order:
            res['posreference_number'] = ui_order['reference_number']
        if 'order_id' in ui_order and ui_order['order_id'] != '0':
        	for order_line in ui_order['lines']:
        		if 'order_line_id' in order_line[2]:
        			wpos_order_line = self.env['pos.order.line'].browse(int(order_line[2]['order_line_id']))
        			if wpos_order_line:
        				wpos_order_line.returned_qty = wpos_order_line.returned_qty + abs(order_line[2]['qty'])
        return res

    @api.model
    def search_return_orders(self, refno):
        pos_order = self.browse(refno)
        if pos_order:
            # pos_order = pos_orders[0]
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
            tax_details = {}
            for line in pos_order.lines:
                discount += (line.price_unit * line.qty * line.discount) / 100
                order_line.append({
                	'line_id':line.id,
                	'returned_qty':line.returned_qty,
                    'product_name': line.product_id.name,
                    'product_id': line.product_id.id,
                    'is_not_returnable':line.product_id.is_not_returnable,
                    'qty': line.qty,
                    'price_unit': line.price_unit,
                    'unit_name':line.product_id.uom_id.name,
                    'discount': line.discount,
                    'price_subtotal':line.price_subtotal,
                    'price_subtotal_incl':line.price_subtotal_incl,
                    })
                for tax_d in line.tax_ids_after_fiscal_position:
                    if tax_d.name in tax_details:
                        tax_details[tax_d.name] += (tax_d.amount/100)*line.price_unit*line.qty
                    else:
                        tax_details[tax_d.name] = (tax_d.amount/100)*line.price_unit*line.qty

            user_tz = self.env.user.tz or pytz.utc
            local = pytz.timezone(user_tz)
            # order_date = datetime.strftime(pytz.utc.localize(datetime.strptime(pos_order.date_order,DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local),"%m/%d/%Y %I:%M %p") 
            order_date = ""
            if pos_order.date_order:
                order_date = datetime.strftime(pos_order.date_order, DEFAULT_SERVER_DATETIME_FORMAT)
                order_date = datetime.strptime(order_date, DEFAULT_SERVER_DATETIME_FORMAT)
            tax_details2 = []
            if tax_details:
                for k in tax_details:
                    tax_details2.append([k,round(tax_details[k],2)])

            return {
            	'session_id':pos_order.session_id.name,
           		'customer_name':pos_order.partner_id.name or "",
           		'order_name':pos_order.name,
                'order_line':order_line,
                'payment_lines':payment_lines,
                'discount':discount,
                'change':change,
                'tax_details2':tax_details2,
                'order_id':pos_order.id,
                'name':pos_order.pos_reference,
                'date_order':order_date.strftime("%d/%m/%Y %H:%M:%S") if order_date else "",
                'amount_total':pos_order.amount_total,
                'amount_tax':pos_order.amount_tax,
                'cashier':pos_order.user_id.name if pos_order.user_id else "",
            }




