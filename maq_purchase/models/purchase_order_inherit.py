# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    '''new field added'''

    m_created_by = fields.Char(string="Created By")

    @api.onchange('partner_id', 'company_id')
    def onchange_partner_id(self):
        res = super(PurchaseOrder, self).onchange_partner_id()
        if self.partner_id:
            if self.order_line:
                warning_mess = {
                    'title': _('Vendor Change!'),
                    'message': 'You changed the vendor but product lines are still there.'
                }
                res.update({'warning': warning_mess})
        return res


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.onchange('product_id')
    def onchange_product_id(self):
        '''Show the products of selected PO supplier'''
        res = super(PurchaseOrderLine, self).onchange_product_id()
        product_supplier_ids = self.env['product.supplierinfo'].search(
            [('name', '=', self.partner_id.id)])
        product_id = self.env['product.product']
        template_ids = [
            supplier.product_tmpl_id.id for supplier in product_supplier_ids]
        product_product_ids = product_id.search(
            [('product_tmpl_id', 'in', template_ids), ('purchase_ok', '=', True)])
        product_list = [product.id for product in product_product_ids]
        res.update({'domain': {'product_id': [('id', 'in', product_list)]}})
        return res
