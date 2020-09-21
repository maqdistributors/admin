# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockMove(models.Model):

    _inherit = 'stock.move'
    
    @api.multi
    @api.depends('picking_id.partner_id', 'picking_id.company_id', 'product_id')
    def _get_vendor_code(self):
        '''
        This method sets the vendor code by searching vendor code from vendor pricelists on stock move. If no vendor code is set,
        then blank value is set for the field.
        '''
        for rec in self:
            vendor_name = rec.picking_id.partner_id.id
            company_id = rec.picking_id.company_id.id
            product_id = rec.product_id.id
            supplierinfo_search = self.env['product.supplierinfo'].search([('name','=',vendor_name),('product_id','=',product_id),('company_id','=',company_id)], limit=1)
            vendor_code = ''
            if supplierinfo_search:
                vendor_code = supplierinfo_search.product_code or ''
            rec.m_vendor_code = vendor_code

    m_vendor_code = fields.Char(string="Vendor Code", compute="_get_vendor_code",
                                help="This vendor's product code will be used when printing a request for quotation. Keep empty to use the internal one.",
                                track_visibility="onchange")
