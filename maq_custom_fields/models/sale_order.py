# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    @api.multi
    @api.depends('product_id', 'order_id.company_id')
    def _get_cost_price(self):
        '''
        This method sets cost price according to company dependent cost price field
        in sale order line. If we do not get cost price, the it will be set to 0.
        '''
        for rec in self:
            cost_price = 0
            if rec.order_id.company_id:
                resource = 'product.product,'+ str(rec.product_id.id)
                product_company_search = self.env['ir.property'].search([('res_id','=',resource), ('company_id', '=', rec.order_id.company_id.id)], limit=1)
                if product_company_search:
                    cost_price = product_company_search.value_float or 0
            rec.m_cost_price = cost_price

    m_cost_price = fields.Float(string="Cost", compute="_get_cost_price", readonly=True, 
                          help="Cost used for stock valuation in standard price and as a first price to set in average/fifo. Also used as a base price for pricelists. Expressed in the default unit of measure of the product.", track_visibility="onchange")
